import networkx as nx
import matplotlib.pyplot as plt
from pysat.formula import CNF
import re
from construction import *

sat_graph = SATGraph()
sat_graph.clause_to_clique()
sat_graph.all_to_all()

# Visualize as adjacency matrix
matrix_fig = sat_graph.plot_adjacency_matrix()
matrix_fig.savefig('adjacency_matrix.png')
plt.close(matrix_fig)
