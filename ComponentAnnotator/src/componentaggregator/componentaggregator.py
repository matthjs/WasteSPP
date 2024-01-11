import pandas as pd
from sqlalchemy import create_engine


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

        self.db_username = "postgres"
        self.db_password = "temp"
        self.db_host = "0.0.0.0"
        self.db_port = "5432"
        self.db_name = "auto_fl"
        self.engine = create_engine(
            f'postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}')

    def create_aggregate(self):
        """
        Creates an aggregated representation of components based on the provided graph and file annotations.
        """
        communities = self.components.communities

        # print(self.file_annot)

        df_project = pd.DataFrame(columns=self.file_annot.columns)
        df_project["component"] = None  # Add column.

        for comm_id, comm in enumerate(communities):
            label_cnt = {}      # Counts
            df_component = pd.DataFrame(columns=self.file_annot.columns)

            for node_id in comm:
                node_attr = self.dep_graph.nodes[node_id]
                file_path = node_attr['filePathRelative']

                #print("examining file: ", file_path)
                row = self.file_annot.loc[self.file_annot['path'] == file_path]
                file_label_arr = row['label'].values

                if not file_label_arr:          # path not in dataframe for some reason.
                    #print("label not found")
                    continue

                file_label = file_label_arr[0]
                #print("label found -> ", file_label)

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
            df_component['component'] = comm_id

            df_project = pd.concat([df_project, df_component])

        print(df_project)
        print(df_project.columns)

        # Iterate over each project and write its DataFrames to separate tables
        #table_name = f'{project_name}_table_{idx}'  # Create a unique table name for each DataFrame
        df_project.to_sql(self.project_name, self.engine, if_exists='replace', index=False)


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
