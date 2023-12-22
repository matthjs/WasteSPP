from componentannotator.componentannotator import ComponentAnnotator

if __name__ == "__main__":
    ComponentAnnotator("java").annotate_project("JavaTest", "https://github.com/matthjs/JavaTest.git")
    # ComponentAnnotator("java").annotate_projects()