import pandas as pd

class ComponentAggregator:
    def __init__(self):
        """
        Initializes a ComponentAggregator instance with default attributes.

        Fields:
            self.components (cdlib.classes.node_clustering.NodeClustering): Node (file) community representation of project.
            self.file_annot (pd.DataFrame): DataFrame containing file annotations associated with components.
        """
        self.components = None
        self.dep_graph = None
        self.file_annot = None

    def create_aggregate(self):
        """
        Creates an aggregated representation of components based on the provided graph and file annotations.
        """
        communities = self.components.communities

        print(self.file_annot)

        for comm_id, comm in enumerate(communities):
            label_cnt = {}      # Counts
            df_component = pd.DataFrame(columns=self.file_annot.columns)

            for node_id in comm:
                node_attr = self.dep_graph.nodes[node_id]
                file_path = node_attr['filePathRelative']

                print("examining file: ", file_path)
                row = self.file_annot.loc[self.file_annot['path'] == file_path]
                file_label_arr = row['label'].values

                if not file_label_arr:          # path not in dataframe for some reason.
                    print("label not found")
                    continue

                file_label = file_label_arr[0]
                print("label found -> ", file_label)

                df_component = pd.concat([df_component, row])      # Append row.

                if file_label in label_cnt:
                    label_cnt[file_label] += 1
                else:
                    label_cnt[file_label] = 1

            if label_cnt:
                majority_label = max(label_cnt, key=label_cnt.get)
            else:
                majority_label = "None"     # No counts for some reason.

            df_component['ComponentLabel'] = majority_label
            print(df_component)


    def set_state(self, components, file_annot: pd.DataFrame, dep_graph):
        """
        Sets the state of the ComponentAggregator with the provided graph and file annotations.

        Args:
            components (cdlib.classes.node_clustering.NodeClustering): Node (file) community representation of project.
            file_annot (pd.DataFrame): DataFrame containing file annotations associated with components.
            dep_graph:
        """
        self.components = components
        self.dep_graph = dep_graph
        self.file_annot = file_annot
