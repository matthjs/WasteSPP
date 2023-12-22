from componentannotator.componentannotator import ComponentAnnotator

if __name__ == "__main__":
    ComponentAnnotator("java").annotate_project("pumpernickel", "https://github.com/mickleness/pumpernickel.git")
    # ComponentAnnotator("java").annotate_projects()