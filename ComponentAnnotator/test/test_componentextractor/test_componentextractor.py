import os
import unittest
import cdlib
import networkx as nx
from componentextractor.componentextractor import ComponentExtractor

def test_graph():
    # Create a simple graph
    dummy_graph = nx.Graph()
    dummy_graph.add_nodes_from([1, 2, 3])
    dummy_graph.add_edges_from([(1, 2), (2, 3)])

    # Save the graph in GraphML format
    if not os.path.exists("/component-annotator/data/arcanOutput/"):
        os.makedirs("/component-annotator/data/arcanOutput/")

    if not os.path.exists("/component-annotator/data/arcanOutput/TestProject"):
        os.makedirs("/component-annotator/data/arcanOutput/TestProject")
    graphml_filename = "/component-annotator/data/arcanOutput/TestProject/dummy_graph.graphml"
    nx.write_graphml(dummy_graph, graphml_filename)

    return dummy_graph

class TestComponentExtractor(unittest.TestCase):
    def setUp(self):
        self.component_extractor = ComponentExtractor(language="java")
        self.component_extractor.set_project(project="TestProject",
                     project_url="https://github.com/testuser/testproject")
        self.component_extractor.arcan_run = True       # Ensure arcan is not run.
        self.test_dep_graph = test_graph()

    def test_dependency_graph(self):
        dep_graph = self.component_extractor.dependency_graph()
        self.assertIsNotNone(dep_graph)
        self.assertIsInstance(dep_graph, nx.Graph)
        self.assertTrue(nx.is_isomorphic(self.test_dep_graph, dep_graph))

    def test_infomap_components(self):
        components = self.component_extractor.infomap_components()
        exp_communities = [['1', '2', '3']]

        self.assertIsNotNone(components)
        self.assertIsNotNone(components.communities)
        self.assertIsInstance(components, cdlib.classes.node_clustering.NodeClustering)
        self.assertEqual(components.communities, exp_communities)


if __name__ == '__main__':
    unittest.main()
