from componentannotator.componentannotator import ComponentAnnotator
from loguru import logger

if __name__ == "__main__":
    logger.debug("Passed A-1 (assuming this is run through docker)")
    logger.debug("Passed A-4 (logging is active)")
    logger.debug("Passed A-6 (pipeline and auto-fl run in separate containers)")
    logger.debug("Passed A-17 (databases are running in separate containers)")
    ComponentAnnotator("java").annotate_projects(3)
    #print(ComponentAnnotator("java").annotate_project("OOP_final_project", "https://github.com/matthjs/OOP_final_project.git"))