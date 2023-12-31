import shutil
import networkx as nx
import os
from os.path import join, exists
from shlex import quote
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

    if language == "C++":       # check if this is how it is for auto-fl
        language = "CPP"
    elif language == "C#":      # check if this is how it is for auto-fl
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

    def component_graph(self, project: str, project_url: str):
        self.run_arcan(project, project_url)
        directory: str = self.arcan_out + "arcanOutput/" + project + "/"
        return nx.read_graphml(directory + find_file_by_extension(directory, ".graphml"))

    def run_arcan(self, project_name: str, project_url: str) -> None:
        """
        Runs the script to extract the graphs using Arcan.
        NOTE: Functionality of checking if project is already analyzed is removed for now.
        TODO: Add functionality so that it can skip already analyzed projects.
        Args:
            project_name (str): The name of the GitHub project.
            project_url (str): The URL of the GitHub project.
        """
        try:

            command = [self.arcan_script]

            args = [project_url, project_name,
                    self.language, self.arcan_path, self.repository_path, self.arcan_out, join(self.logs_path, 'arcan')]

            command.extend(args)

            logger.info(f"Running command: {' '.join(command)}")

            call(" ".join(command), shell=True)

            logger.info(f"Finished to extract graph for {project_name}")

        except Exception as e:
            logger.error(f"Failed to extract graph for {project_name}")
            logger.error(f"{e}")

    def run_arcan_OTHER(self, project_name: str,  language: str) -> None:
        """
        Runs the script to extract the graphs using Arcan. It also checks if the project has already been processed,
         and if so, it skips it.
        :param cfg:
        :param project_name:
        :param language:
        :return:
        """

        # What is the point of this line? Is project a GitHub URL string?
        check_path = join(self.arcan_graphs, project_name.replace('/', '|'), '.completed')

        completed = check_status(check_path)
        try:
            if completed:
                logger.info(f"Skipping {project_name} as it has already been processed")
                return

            command = [self.arcan_script]

            args = [project_name, quote(project_name.replace('/', '|')),
                    language, self.arcan_path, self.repository_path, self.arcan_out, join(self.logs_path, 'arcan')]

            command.extend(args)

            logger.info(f"Running command: {' '.join(command)}")

            call(" ".join(command), shell=True)

            if not completed:
                 with open(check_path, 'wt') as outf:
                    logger.info(f"Creating file {outf.name}")

            logger.info(f"Finished to extract graph for {project_name}")

        except Exception as e:
            logger.error(f"Failed to extract graph for {project_name}")
            logger.error(f"{e}")

        finally:
            if not completed:
                logger.info(f"Cleaning up {project_name} repository")
                repo_path = join(self.repository_path, project_name.replace('/', '|'))
                shutil.rmtree(repo_path, ignore_errors=True)
            return
