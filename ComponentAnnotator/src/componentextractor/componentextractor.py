import networkx as nx
from cdlib import algorithms
import os
from os.path import join, exists
from subprocess import call
from loguru import logger

def check_status(path) -> bool:
    """
    Checks if the project has already been processed.

    Args:
        path: The path to check.

    Returns:
        bool: True if the project has been processed; False otherwise.
    """
    return exists(path)

def arcan_language_str(language: str) -> str:
    """
    Returns the language string that is compatible with Arcan.

    NOTE: Extend this if needed.

    Args:
        language: The language string for auto-fl.

    Returns:
        The language string for Arcan.
    """
    if language in ["JAVA", "CPP", "C", "ASML", "CSHARP", "PYTHON"]:
        return language

    if language == "C++":
        language = "CPP"
    elif language == "C#":
        language = "CSHARP"

    return language.upper()


def find_file_by_extension(directory: str, target_extension: str) -> str:
    """
    Find a file in the specified directory with the given extension.

    Args:
        directory (str): The path to the directory.
        target_extension (str): The target extension to search for.

    Returns:
        str: The filename if a matching file is found, otherwise, an empty string.
    """
    for filename in os.listdir(directory):
        if filename.endswith(target_extension):
            return filename

    print(f"No file with extension {target_extension} found in {directory}")
    return ""

class ComponentExtractor:
    """
    The ComponentExtractor class is responsible for extracting component graphs using the Arcan tool.
    """
    def __init__(self, language: str):
        """
        Initializes the ComponentExtractor instance.

        Args:
            language: The programming language of the project.
        """
        self.arcan_graphs: str = ""
        self.arcan_script: str = "/component-annotator/src/arcan/run-arcan.sh"           # NOTE: arcan.bat should be run on Windows
        self.arcan_path: str = "/component-annotator/src/arcan"
        self.repository_path: str = "/component-annotator/data/repository"
        self.arcan_out: str = "/component-annotator/data/"
        self.logs_path: str = "/component-annotator/data/arcan-log"
        self.language: str = arcan_language_str(language)

        # Class data.
        self.dep_graph = None
        self.project_name = None
        self.project_url = None
        self.valid = False
        self.arcan_run = False

    def set_project(self, project: str, project_url: str):
        """
        Args:
            project (str): The name of the GitHub project.
            project_url (str): The URL of the GitHub project.
        """
        self.project_name = project
        self.project_url = project_url
        self.arcan_run = False
        self.valid = True
        return self

    def dependency_graph(self):
        """
        Returns the dependency graph for a given project.

        Returns:
            nx.Graph: The dependency graph.
        """
        if not self.valid:
            raise ValueError("ComponentExtractor illegal state -> project not set or arcan failed")

        self._init_dep_graph()

        return self.dep_graph

    def infomap_components(self):
        """
        Runs the Infomap algorithm on the dependency graph and returns the resulting communities.

        Returns:
            cdlib.classes.node_clustering.NodeClustering: The result of the Infomap algorithm.
        """
        return algorithms.infomap(self.dependency_graph())

    def _init_dep_graph(self):
        if not self.valid:
            raise ValueError("ComponentExtractor illegal state -> project not set or arcan failed")

        if not self.arcan_run:
            self._run_arcan()
        self.arcan_run = True

        if self.dep_graph is None:
            directory: str = self.arcan_out + "arcanOutput/" + self.project_name + "/"
            if not os.path.exists(directory):
                self.valid = False
                raise ValueError("ComponentExtractor illegal state -> project directory cannot be found")

            self.dep_graph = nx.read_graphml(directory + find_file_by_extension(directory, ".graphml"))

    def _run_arcan(self) -> None:
        """
        Runs the script to extract the graphs using Arcan.
        NOTE: Functionality of checking if project is already analyzed is removed.
        """
        if not self.valid:
            raise ValueError("Illegal state -> project not set.")

        try:

            command = [self.arcan_script]

            args = [self.project_url, self.project_name,
                    self.language, self.arcan_path, self.repository_path, self.arcan_out, join(self.logs_path, 'arcan')]

            command.extend(args)

            logger.info(f"Running command: {' '.join(command)}")

            call(" ".join(command), shell=True)

            logger.info(f"Finished to extract graph for {self.project_name}")
            logger.debug("Passed A-9, A-10 (forwarding to Arcan successful)")

        except Exception as e:
            logger.error(f"Failed to extract graph for {self.project_name}")
            logger.error(f"{e}")
            self.valid = False