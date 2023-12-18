from typing import List

from typing import List
import numpy as np
import pandas as pd
import requests
from projectextractor.projectextractor import ProjectExtractor

def get_label(distribution, taxonomy):
    return taxonomy[str(np.argmax(distribution))]


class ComponentAnnotator:
    def __init__(self):
        self.project_extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01")

    def annotate_files(self):
        """
        TODO: Use UI type call
        """
        abandoned_projects = self.project_extractor.find_abandoned_projects(10)

        for project in abandoned_projects:
            print(f"- {project['name']} ({project['html_url']})")
            ret, _ = self._annotate_file(project['name'], project['html_url'], ["java"])
            self._annotate_file(project['name'], project['html_url'], ["java"])
            print(ret)

    def _annotate_file(self, project_name: str, remote: str, languages: List[str]):
        url = 'http://auto-fl:8000/label/files'
        analysis = {
            "name": project_name,  # "Waikato|weka-3.8",
            "remote": remote,  # "https://github.com/Waikato/weka-3.8",
            "languages": languages  # ["java"]
        }

        res = requests.post(url, json=analysis)
        res = res.json()['result']
        taxonomy = res['taxonomy']
        entries = []
        files = res['versions'][0]['files']
        for file_name in files:
            file = files[file_name]
            entries.append({
                "path": file["path"],
                "package": file["package"],
                "distribution": file["annotation"]["distribution"],
                "unannotated": file["annotation"]["unannotated"],
                "label": get_label(file["annotation"]["distribution"], taxonomy)
            })

        annotations_df = pd.DataFrame(entries)

        return annotations_df, taxonomy