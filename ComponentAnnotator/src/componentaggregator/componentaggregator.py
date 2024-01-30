import pandas as pd
from sqlalchemy import create_engine
from loguru import logger

class ComponentAggregator:
    def __init__(self):
        """
        Initializes a ComponentAggregator instance with default attributes.

        Fields:
            self.components (cdlib.classes.node_clustering.NodeClustering): Node (file) community representation of project.
            self.file_annot (pd.DataFrame): DataFrame containing file annotations associated with components.
        """
        self.project_name = None
        self.components = None
        self.dep_graph = None
        self.file_annot = None
        self.valid = False

        # Hardcoded see docker-compose yaml file.
        self.db_username = "pipeline_user"
        self.db_password = "pipeline_pw"
        self.db_host = "db_pipeline"
        self.db_name = "pipeline"
        self.engine = create_engine(
            f'postgresql+psycopg://{self.db_username}:{self.db_password}@{self.db_host}/{self.db_name}')

    def set_state(self, components, file_annot: pd.DataFrame, dep_graph, project_name: str):
        """
        Sets the state of the ComponentAggregator with the provided graph and file annotations.

        Args:
            components (cdlib.classes.node_clustering.NodeClustering): Node (file) community representation of project.
            file_annot (pd.DataFrame): DataFrame containing file annotations associated with components.
            dep_graph:
            project_name:
        """
        self.components = components
        self.dep_graph = dep_graph
        self.file_annot = file_annot
        self.project_name = project_name
        self.valid = True

    def create_aggregate(self) -> pd.DataFrame:
        """
        Creates an aggregated representation of components based on the provided graph and file annotations.
        NOTE: Also puts resulting dataframe inside a postgres database.

        Returns:
            pd.DataFrame: Dataframe containing files in the project with component and component-label information.
        """
        if not self.valid:
            raise ValueError("Illegal state -> project not set.")

        communities = self.components.communities

        df_project = self._initialize_project_dataframe()
        if not communities:
            return self._handle_no_communities(df_project)

        for community_id, community in enumerate(communities):
            df_component = self._create_component_dataframe(community)
            majority_label = self._get_majority_label(df_component)

            df_project = self._update_project_dataframe(df_project, df_component, community_id, majority_label)

        self._save_to_database(df_project)

        return df_project

    def _initialize_project_dataframe(self) -> pd.DataFrame:
        """
        Initializes the project dataframe.

        Returns:
            pd.DataFrame: Initialized project dataframe.
        """
        df_project = pd.DataFrame(columns=self.file_annot.columns)
        df_project["component"] = None
        df_project['componentlabel'] = None
        df_project['mismatch'] = None
        df_project['case'] = None
        return df_project

    def _handle_no_communities(self, df_project: pd.DataFrame) -> pd.DataFrame:
        """
        Handles the case where no communities are found.

        Args:
            df_project (pd.DataFrame): Project dataframe.

        Returns:
            pd.DataFrame: Updated project dataframe for the no communities case.
        """
        logger.error("No communities from infomap detected. Returning empty dataframe")
        new_row = {'projectname': self.project_name, "case": "no_communities_found"}
        df_project = pd.concat([df_project, pd.DataFrame([new_row])], ignore_index=True)
        return df_project

    def _create_component_dataframe(self, community) -> pd.DataFrame:
        """
        Creates a dataframe for a given community.

        Args:
            community: A community from the components.

        Returns:
            pd.DataFrame: Dataframe for the given community.
        """
        df_component = pd.DataFrame(columns=self.file_annot.columns)
        for node_id in community:
            node_attr = self.dep_graph.nodes[node_id]
            file_path = node_attr['filePathRelative']
            row = self.file_annot.loc[self.file_annot['path'] == file_path]
            df_component = pd.concat([df_component, row])
        return df_component

    def _get_majority_label(self, df_component: pd.DataFrame) -> str:
        """
        Gets the majority label for a component.

        Args:
            df_component (pd.DataFrame): Dataframe for a component.

        Returns:
            str: Majority label.
        """
        label_counts = df_component['label'].value_counts()
        majority_label = label_counts.idxmax() if not label_counts.empty else "None"
        return majority_label

    def _update_project_dataframe(self, df_project, df_component, community_id, component_label) -> pd.DataFrame:
        """
        Updates the project dataframe with information from a component.

        Args:
            df_project (pd.DataFrame): Project dataframe.
            df_component (pd.DataFrame): Dataframe for a component.
            community_id: ID of the current community.
            component_label: label for the component.
        """
        df_component['componentlabel'] = component_label
        df_component['component'] = community_id
        df_component['mismatch'] = df_component['label'] != df_component['componentlabel']
        return pd.concat([df_project, df_component])

    def _save_to_database(self, df_project: pd.DataFrame):
        """
        Saves the project dataframe to the database and CSV file.

        Args:
            df_project (pd.DataFrame): Project dataframe.
        """
        if df_project.empty:
            new_row = {'projectname': self.project_name, "case": "no_file_matches"}
            df_project = pd.concat([df_project, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df_project['case'] = "success"

        df_project['projectname'] = self.project_name
        df_project.to_sql(self.project_name, self.engine, if_exists='replace', index=False)
        df_project.to_csv(f'output_{self.project_name}.csv', index=False)
        logger.info(f"Wrote component annotations for {self.project_name} to database.")