from componentannotator.componentannotator import ComponentAnnotator
from componentaggregator.componentaggregator import ComponentAggregator

if __name__ == "__main__":
    # ComponentAnnotator("java").annotate_project("pumpernickel", "https://github.com/mickleness/pumpernickel.git")
    ComponentAnnotator("java").annotate_projects()
    # ComponentAggregator()