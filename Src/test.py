import networkx as nx
import matplotlib.pyplot as plt
from pysat.formula import CNF
import re
from node import Node
import random
from construction import (
    add_clause,
    clause_to_clique,
    clause_to_cluster,
    literal_to_node,
    literal_and_negation_to_node,
    variable_to_node,
    all_to_all,
    x_to_x,
    x_to_not_x,
    x_to_all_but_x,
    x_to_all_but_not_x
)

G = nx.Graph()

def generate_random_cnf(num_clauses=5, num_variables=3):
    random_cnf = CNF()
    for _ in range(num_clauses):
        random_clause = random.sample(range(1, num_variables + 1), k=3)
        for i in range(len(random_clause)):
            if random.random() > 0.5:
                random_clause[i] = - random_clause[i]
        random_cnf.append(random_clause)
    return random_cnf

cnf = generate_random_cnf(num_clauses=4)
print("Random CNF Clauses:")
for clause in cnf.clauses:
    print(clause)

# Step 2: Call the graph construction functions
clause_to_clique(k=2)  # Convert clauses to cliques
literal_to_node()  # Add literals as nodes
x_to_x()  # Connect nodes with the same literal


# Step 3: Inspect the graph
print("\nGraph Nodes:")
for node in G.nodes:
    print(node)

print("\nGraph Edges:")
for edge in G.edges:
    print(edge)

# Step 4: Visualize the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(
    G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2000
)
plt.title("Visualization of the Graph")
