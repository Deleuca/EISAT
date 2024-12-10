import networkx as nx
from node import Node

class Gadget:
    def __init__(self, gadget_num, iteration, is_directed=False):
        if is_directed:
            self.G = nx.DiGraph()
        else:
            self.G = nx.Graph()
        self.gadget_num = gadget_num
        self.iteration = iteration

    def addVertex(self):
        num_nodes = len(self.G.nodes)
        name = str(self.gadget_num) + "." + str(num_nodes) + "." + str(self.iteration) + ".g"
        node = Node(name, literal=None, clause=self.gadget_num, iteration=self.iteration, cluster=False)
        self.G.add_node(node)

    def addEdge(self, v1, v2):
        self.G.add_edge(v1, v2)