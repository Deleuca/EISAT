import networkx as nx
from pysat.formula import CNF
import re

G = nx.Graph()

history = {"K cliques": 0, "K clusters": 0, "K literals": 0}

'''
3-SAT Problem Instantiation Methods
'''

cnf = CNF()

def add_clause(string):
    pattern = r"-?\d+\s-?\d+\s-?\d+"
    if not re.fullmatch(pattern, string):
        print("Invalid Clause. Returning.")
        return
    l = string.split()
    for i in range(len(l)):
        l[i] = int(l[i])
    cnf.append(l)

'''
Network Construction Methods
'''

'''
1. Clause Operations
'''

def clause_to_clique(k = 1):
    for clause_index in range(1, len(cnf.clauses) + 1):
        for i in range(1, k + 1):
            clause_nodes = []
            for literal_index in range(1, 4):
                name = str(clause_index) + "." + str(literal_index) + "." + str(i + history.get("K cliques"))
                G.add_node(name)
                clause_nodes.append(name)
            G.add_edge(clause_nodes[0], clause_nodes[1])
            G.add_edge(clause_nodes[0], clause_nodes[2])
            G.add_edge(clause_nodes[1], clause_nodes[2])
    history["K cliques"] += k

def clause_to_cluster(k = 1):
    for clause_index in range(1, len(cnf.clauses) + 1):
        for i in range(1, k + 1):
            for literal_index in range(1, 4):
                name = str(clause_index) + "." + str(literal_index) + "." + str(i + history.get("K clusters")) + ".c"
                G.add_node(name)
    history["K clusters"] += k

'''
2. Literal Operations
'''

def literal_to_node(k = 1):
    literals = set()
    for clause in cnf.clauses:
        for literal in clause:
            literals.add(literal)
    for literal in literals:
        for i in range(1, k + 1):
            name = str(literal) + "." + str(i + history.get("K literals"))
            G.add_node(name)
    history["K literals"] += k

def literal_and_negation_to_node(k = 1):
    literals = set()
    for clause in cnf.clauses:
        for literal in clause:
            literals.add(abs(literal))
    for literal in literals:
        for i in range(1, k + 1):
            name = str(literal) + "." + str(i + history.get("K literals and negs"))
            G.add_node(name + ".p")
            G.add_node(name + ".n")
    history["K literals and negs"] += k

def variable_to_node(k = 1):
    literals = set()
    for clause in cnf.clauses:
        for literal in clause:
            literals.add(abs(literal))
    for literal in literals:
        for i in range(1, k + 1):
            name = str(literal) + "." + str(i + history.get("K variables"))
            G.add_node(name + ".v")
    history["K variables"] += k

'''
3. Connection Functions
'''

