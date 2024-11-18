import networkx as nx
from pysat.formula import CNF
import re
import random
from node import Node
G = nx.Graph()

history = {"K cliques": 0, "K clusters": 0, "K literals": 0, "K literals and negs": 0, "K Variables": 0}

'''
3-SAT Problem Instantiation Methods
'''

cnf = CNF()

def generate_random_cnf(num_clauses=5, num_variables=3):
    random_cnf = CNF()
    for _ in range(num_clauses):
        random_clause = random.sample(range(1, num_variables + 1), k=3)
        for i in range(len(random_clause)):
            if random.random() > 0.5:
                random_clause[i] = - random_clause[i]
        random_cnf.append(random_clause)
    return random_cnf

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

def toggle_directed_graph(G):
    if G.is_directed():
        G = nx.Graph()
    else:
        G = nx.DiGraph()
    return G

'''
1. Clause Operations
'''

def clause_to_clique(k = 1):
    for clause_index in range(1, len(cnf.clauses) + 1):
        for i in range(1, k + 1):
            clause_nodes = []
            for literal_index in range(1, 4):
                name = str(clause_index) + "." + str(literal_index) + "." + str(i + history.get("K cliques"))
                new_node = Node(name=name, literal=cnf.clauses[clause_index-1][literal_index-1], clause=cnf.clauses[clause_index-1], iteration=i + history.get("K cliques"))
                G.add_node(new_node)
                clause_nodes.append(new_node)
            G.add_edge(clause_nodes[0], clause_nodes[1])
            G.add_edge(clause_nodes[0], clause_nodes[2])
            G.add_edge(clause_nodes[1], clause_nodes[2])
    history["K cliques"] += k

def clause_to_cluster(k = 1):
    for clause_index in range(1, len(cnf.clauses) + 1):
        for i in range(1, k + 1):
            for literal_index in range(1, 4):
                name = str(clause_index) + "." + str(literal_index) + "." + str(i + history.get("K clusters")) + ".c"
                new_node = Node(name=name, literal=cnf.clauses[clause_index-1][literal_index-1], clause=cnf.clauses[clause_index-1], iteration=i + history.get("K clusters"), cluster=True)
                G.add_node(new_node)
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
            name = str(literal) + "." + str(i + history.get("K literals")) + ".l"
            new_node = Node(name=name, literal=literal, clause=None, iteration=i + history.get("K literals"))
            G.add_node(new_node)
    history["K literals"] += k

def literal_and_negation_to_node(k = 1):
    literals = set()
    for clause in cnf.clauses:
        for literal in clause:
            literals.add(abs(literal))
    for literal in literals:
        for i in range(1, k + 1):
            name = str(literal) + "." + str(i + history.get("K literals and negs"))
            p_node = Node(name=name+".p", literal=literal, clause=None, iteration=i+history.get("K literals and negs"))
            n_node = Node(name=name+".n", literal=-literal, clause=None, iteration=i+history.get("K literals and negs"))
            G.add_node(p_node)
            G.add_node(n_node)
    history["K literals and negs"] += k

def variable_to_node(k = 1):
    literals = set()
    for clause in cnf.clauses:
        for literal in clause:
            literals.add(abs(literal))
    for literal in literals:
        for i in range(1, k + 1):
            name = str(literal) + "." + str(i + history.get("K variables")) + ".v"
            new_node = Node(name=name, literal=literal, clause=None, iteration=i+history.get("K variables"))
            G.add_node(new_node)
    history["K variables"] += k

'''
3. Connection Functions
'''

def same_cluster(node_1: Node, node_2: Node):
    if node_1.inCluster() and node_2.inCluster():
        if node_1.getClause() == node_2.getClause():
            if node_1.getIteration() == node_2.getIteration():
                return True
    return False

'''
3.1 Undirected Functions
'''

def all_to_all():
    if G.is_directed():
        print("Error: G is a directed graph.")
        print("Returning.")
        return
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        node_1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            node_2 = node_list[j]
            if not same_cluster(node_1, node_2):
                G.add_edge(node_1, node_2)

def x_to_x():
    if G.is_directed():
        print("Error: G is a directed graph.")
        print("Returning.")
        return
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        node_1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            node_2 = node_list[j]
            if not same_cluster(node_1, node_2) and node_1.getLiteral() == node_2.getLiteral():
                G.add_edge(node_1, node_2)

def x_to_not_x():
    if G.is_directed():
        print("Error: G is a directed graph.")
        print("Returning.")
        return
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        node_1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            node_2 = node_list[j]
            if not same_cluster(node_1, node_2) and node_1.getLiteral() == - node_2.getLiteral():
                G.add_edge(node_1, node_2)

def x_to_all_but_x():
    if G.is_directed():
        print("Error: G is a directed graph.")
        print("Returning.")
        return
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        node_1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            node_2 = node_list[j]
            if not same_cluster(node_1, node_2) and node_1.getLiteral() != node_2.getLiteral():
                G.add_edge(node_1, node_2)

def x_to_all_but_not_x():
    if G.is_directed():
        print("Error: G is a directed graph.")
        print("Returning.")
        return
    node_list = list(G.nodes)
    for i in range(len(node_list)):
        node_1 = node_list[i]
        for j in range(i + 1, len(node_list)):
            node_2 = node_list[j]
            if not same_cluster(node_1, node_2) and node_1.getLiteral() != - node_2.getLiteral():
                G.add_edge(node_1, node_2)

'''
3.2 Directed Functions
'''

