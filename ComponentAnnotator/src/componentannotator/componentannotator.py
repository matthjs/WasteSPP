import re
from typing import List

from typing import List
import numpy as np
import pandas as pd
import requests

from componentextractor.componentextractor import ComponentExtractor
from projectextractor.projectextractor import ProjectExtractor

def get_label(distribution, taxonomy):
    return taxonomy[str(np.argmax(distribution))]


def clean_github_url(url):
    # Define a regular expression pattern to match the specified parts
    pattern = re.compile(r'https://github\.com/(.*?)(\.git)?$')

    # Use re.sub to replace the matched pattern with an empty string
    cleaned_url = re.sub(pattern, r'\1', url)

    print(cleaned_url)

    return cleaned_url


class ComponentAnnotator:
    """
    The ComponentAnnotator class is responsible for annotating files in abandoned GitHub projects.
    It utilizes the ProjectExtractor to find abandoned projects, the ComponentExtractor to run the
    Arcan tool for component information, and the auto-fl annotator for file-level annotations (weak labels).
    """
    def __init__(self):
        """
        Initializes the ComponentAnnotator with default values for the ProjectExtractor.
        """
        self.project_extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01")
        self.component_extractor = ComponentExtractor()

    def annotate_file(self, project_name, project_url):
        # ret, _ = self._annotate_file(project_name, project_url, ["java"])
        self.component_extractor.run_arcan(project_name, project_url, "JAVA")

    def annotate_files(self):
        """
        Uses the project extractor to find abandoned GitHub projects,
        then runs the arcan tool (encapsulated in component_extractor) to get component information
        and in after that runs the annotator (auto-fl) to get file level annotations (weak labels)
        for all the files in the project.
        """
        abandoned_projects = self.project_extractor.find_abandoned_projects(3)

        for project in abandoned_projects:
            print(f"- {project['name']} ({project['html_url']})")
            self.component_extractor.run_arcan(project['name'], project['html_url'], "JAVA")
            # ret, _ = self._annotate_file(project['name'], project['html_url'], ["java"])
            # print(ret)

    def _annotate_file(self, project_name: str, remote: str, languages: List[str]):
        """
        Request to auto-fl to annotate a GitHub project.
        @param: project_name - name of the GitHub project.
        @param: remote - HTML URL of the GitHub project.
        @param: languages - list of programming languages of project
        NOTE: Only Java project are fully supported and tested with the auto-fl annotator.
        """
        url = 'http://auto-fl:8000/label/files'
        analysis = {
            "name": project_name,  # "Waikato|weka-3.8",
            "remote": remote,  # "https://github.com/Waikato/weka-3.8",
            "languages": languages  # ["java"]
        }

        res = requests.post(url, json=analysis)
        res = res.json()['result']
        taxonomy = res['taxonomy']
        print(taxonomy)
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
        # Skip package and project leven annotations

        return file_annot, taxonomy