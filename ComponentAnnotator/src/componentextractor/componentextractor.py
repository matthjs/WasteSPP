import shutil
import networkx as nx
from os.path import join, exists
from pathlib import Path
from shlex import quote
from subprocess import call

import hydra
import pandas as pd
from loguru import logger
import os
from omegaconf import DictConfig


class ComponentExtractor:
    def __init__(self):
        self.arcan_graphs: str = ""
        self.arcan_script: str = "/component-annotator/src/arcan/run-arcan.sh"           # NOTE: arcan.bat should be run on Windows
        self.arcan_path: str = "/component-annotator/src/arcan"
        self.repository_path: str = "/component-annotator/data/repository"
        self.arcan_out: str = "/component-annotator/data/arcan-out"
        self.logs_path: str = "/component-annotator/data/arcan-log"

        self.component_graph = None

    def component_graph(self, project: str, language = "JAVA"):
        self.run_arcan(project, language)
        return nx.read_graphml(self.arcan_out)

    """
    Run arcan
    """
    def check_status(self, path) -> bool:
        """
        Checks if the project has already been processed.
        :param path:
        :return:
        """
        return exists(path)

    def run_arcan(self, project_name: str, project_url: str, language: str) -> None:
        """
        Runs the script to extract the graphs using Arcan. It also checks if the project has already been processed,
         and if so, it skips it.
        :param cfg:
        :param project_name:
        :param language:
        :return:
        """

        # What is the point of this line? Is project a GitHub URL string?
        # check_path = join(self.arcan_graphs, project_url.replace('/', '|'), '.completed')

        #completed = self.check_status(check_path)
        try:
           #if completed:
           #     logger.info(f"Skipping {project_name} as it has already been processed")
           #     return

            command = [self.arcan_script]

            args = [project_url, project_name,
                    language, self.arcan_path, self.repository_path, self.arcan_out, join(self.logs_path, 'arcan')]

            command.extend(args)

            logger.info(f"Running command: {' '.join(command)}")

            call(" ".join(command), shell=True)

            #if not completed:
            #     with open(check_path, 'wt') as outf:
            #        logger.info(f"Creating file {outf.name}")

            logger.info(f"Finished to extract graph for {project_name}")

        except Exception as e:
            logger.error(f"Failed to extract graph for {project_name}")
            logger.error(f"{e}")

        finally:
            #if not completed:
            #    logger.info(f"Cleaning up {project_name} repository")
            #    repo_path = join(self.repository_path, project_name.replace('/', '|'))
            #    shutil.rmtree(repo_path, ignore_errors=True)
            return

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

        completed = self.check_status(check_path)
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
