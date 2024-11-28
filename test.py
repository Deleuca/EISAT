from pysat.formula import CNF
from src.construction import SATGraph

G = SATGraph()
G.generate_random_cnf(30, 3)
G.clause_to_clique()
G.x_to_x()
G.save_d3_visualization("test.html")