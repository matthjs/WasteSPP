from typing import List
import numpy as np
import pandas as pd
import requests

from componentextractor.componentextractor import ComponentExtractor
from projectextractor.projectextractor import ProjectExtractor

def get_label(distribution, taxonomy):
    """
    Returns the label for a given distribution and taxonomy.

    Args:
        distribution:
        taxonomy:

    Returns:
        The label for the distribution and taxonomy.
    """
    return taxonomy[str(np.argmax(distribution))]

class ComponentAnnotator:
    """
    The ComponentAnnotator class is responsible for annotating files in abandoned GitHub projects.
    It utilizes the ProjectExtractor to find abandoned projects, the ComponentExtractor to run the
    Arcan tool for component information, and the auto-fl annotator for file-level annotations (weak labels).
    """
    def __init__(self, language: str = "java"):
        """
        Initializes the ComponentAnnotator with default values for the ProjectExtractor.

        Args:
            language: The programming language used in the project.
        """
        self.project_extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01", language=language)
        self.component_extractor = ComponentExtractor(language)
        self.language = language

    def annotate_project(self, project_name, project_url):
        """
        Annotate a single GitHub project
        then runs the arcan tool (encapsulated in component_extractor) to get component information
        and in after that runs the annotator (auto-fl) to get file level annotations (weak labels)
        for all the files in the project.
        """
        ret, _ = self._annotate_file(project_name, project_url)
        self.component_extractor.run_arcan(project_name, project_url)

    def annotate_projects(self) -> None:    # For now void function but see later whether it needs to return something
        """
        Uses the project extractor to find abandoned GitHub projects. Then annotates the files
        and extracts the components.
        """
        abandoned_projects = self.project_extractor.find_abandoned_projects(10)

        for project in abandoned_projects:
            self.annotate_project(project['name'], project['html_url'])

    def _annotate_file(self, project_name: str, remote: str):
        """
        Request to auto-fl to annotate a GitHub project.

        Args:
            project_name: Name of the GitHub project.
            remote: HTML URL of the GitHub project.

        NOTE: Only Java project are fully supported and tested with the auto-fl annotator.
        """
        url = 'http://auto-fl:8000/label/files'
        analysis = {
            "name": project_name,  # "Waikato|weka-3.8",
            "remote": remote,  # "https://github.com/Waikato/weka-3.8",
            "languages": [self.language]  # ["java"]
        }

        res = requests.post(url, json=analysis)
        res = res.json()['result']
        taxonomy = res['taxonomy']
        file_entries = []
        files = res['versions'][0]['files']
        for file_name in files:
            file = files[file_name]
            file_entries.append({
                "path": file["path"],
                "package": file["package"],
                "distribution": file["annotation"]["distribution"],
                "unannotated": file["annotation"]["unannotated"],
                "label": get_label(file["annotation"]["distribution"], taxonomy)
            })

        file_annot = pd.DataFrame(file_entries)
        # Skip package and project level annotations

        return file_annot, taxonomy