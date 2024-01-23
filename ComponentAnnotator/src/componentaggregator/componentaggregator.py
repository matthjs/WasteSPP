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
        # logger.debug(f"Look at communities to see if A-14 is satisfied: {communities}")

        df_project = pd.DataFrame(columns=self.file_annot.columns)
        df_project["component"] = None  # Add column.

        for community_id, community in enumerate(communities):
            label_cnt = {}      # Counts
            df_component = pd.DataFrame(columns=self.file_annot.columns)

            for node_id in community:
                node_attr = self.dep_graph.nodes[node_id]
                file_path = node_attr['filePathRelative']

                #logger.info(f"Examining file: {file_path}")
                row = self.file_annot.loc[self.file_annot['path'] == file_path]
                file_label_arr = row['label'].values

                if not file_label_arr:          # path not in dataframe for some reason.
                    #logger.info("Label not found.")
                    continue

                file_label = file_label_arr[0]
                #logger.info(f"Label found -> {file_label}.")

                df_component = pd.concat([df_component, row])      # Append row.

                if file_label in label_cnt:
                    label_cnt[file_label] += 1
                else:
                    label_cnt[file_label] = 1

            if label_cnt:
                majority_label = max(label_cnt, key=label_cnt.get)
            else:
                majority_label = "None"     # No counts for some reason.

            df_component['componentlabel'] = majority_label
            df_component['component'] = community_id
            df_component['mismatch'] = df_component['label'] != df_component['componentlabel']

            df_project = pd.concat([df_project, df_component])

        logger.debug(f"Printing dataframe")

        df_project['projectname'] = self.project_name

        df_project.to_sql(self.project_name, self.engine, if_exists='replace', index=False)
        logger.info(f"Wrote component annotations for {self.project_name} to database.")
        logger.debug("Passed A-16 (database success)")

        print(df_project)

        return df_project           # Return dataframe


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
