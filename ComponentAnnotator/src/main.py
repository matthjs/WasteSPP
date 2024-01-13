from componentannotator.componentannotator import ComponentAnnotator
from componentaggregator.componentaggregator import ComponentAggregator

if __name__ == "__main__":
    print(ComponentAnnotator("java").annotate_project("OOP_final_project", "https://github.com/matthjs/OOP_final_project.git"))