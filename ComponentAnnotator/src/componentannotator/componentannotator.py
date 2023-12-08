from execution.annotation import AnnotationExecution
from projectextractor.projectextractor import ProjectExtractor


class ComponentAnnotator:
    def __init__(self):
        self.project_extractor = ProjectExtractor(min_stars=100, last_pushed_date="2022-01-01")
        # self.annotator = AnnotationExecution()

    def _annotate_files(self):
        self.project_extractor.find_abandoned_projects(10)
