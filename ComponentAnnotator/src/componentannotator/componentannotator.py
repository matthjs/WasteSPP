from api.main import label_files
from execution.annotation import AnnotationExecution
from projectextractor.projectextractor import ProjectExtractor


class ComponentAnnotator:
    def __init__(self):
        self.project_extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01")

    def _annotate_files(self):
        """
        TODO: Use UI type call
        """
        abandoned_projects = self.project_extractor.find_abandoned_projects(10)

        for project in abandoned_projects:
            label_files()    
