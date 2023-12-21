import networkx as nx
from componentannotator.componentannotator import ComponentAnnotator

if __name__ == "__main__":
    ComponentAnnotator().annotate_file("pumpernickel", "https://github.com/mickleness/pumpernickel.git")
    #ComponentAnnotator().annotate_files()