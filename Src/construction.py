import json
import os

import networkx as nx
from matplotlib import pyplot as plt
from pysat.formula import CNF
import random

from pyvis.network import Network

from node import Node
import re

class SATGraph:
    def __init__(self, cnf=None):
        self.G = nx.Graph()
        self.history = {
            "K cliques": 0,
            "K clusters": 0,
            "K literals": 0,
            "K literals and negs": 0,
            "K Variables": 0,
        }
        if cnf is None:
            self.cnf = CNF()
        else:
            self.cnf = cnf

    def getGraph(self):
        return self.G

    '''
    3-SAT Problem Instantiation Methods
    '''

    def generate_random_cnf(self, num_clauses=5, num_variables=3):
        self.cnf = CNF()
        for _ in range(num_clauses):
            random_clause = random.sample(range(1, num_variables + 1), k=3)
            for i in range(len(random_clause)):
                if random.random() > 0.5:
                    random_clause[i] = -random_clause[i]
            self.cnf.append(random_clause)

    def add_clause(self, clause_string):
        pattern = r"-?\d+\s-?\d+\s-?\d+"
        if not re.fullmatch(pattern, clause_string):
            print("Invalid Clause. Returning.")
            return
        clause = list(map(int, clause_string.split()))
        self.cnf.append(clause)

    '''
    Network Construction Methods
    '''

    def toggle_directed_graph(self):
        if self.G.is_directed():
            self.G = nx.Graph()
        else:
            self.G = nx.DiGraph()
            
    def write(self):
        g = self.getGraph()
        nodes = [{"id": node.getName()} for node in g.nodes()]
        links = [{"source": u.getName(), "target": v.getName()} for u, v in g.edges()]
        graph_data = {"nodes": nodes,"links": links}
        with open("graph.json", "w") as f:
           json.dump(graph_data, f, indent=4)

    '''
    1. Clause Operations
    '''

    def clause_to_clique(self, k=1):
        for clause_index in range(1, len(self.cnf.clauses) + 1):
            for i in range(1, k + 1):
                clause_nodes = []
                for literal_index in range(1, 4):
                    name = f"{clause_index}.{literal_index}.{i + self.history['K cliques']}"
                    new_node = Node(
                        name=name,
                        literal=self.cnf.clauses[clause_index - 1][literal_index - 1],
                        clause=self.cnf.clauses[clause_index - 1],
                        iteration=i + self.history["K cliques"],
                    )
                    self.G.add_node(new_node)
                    clause_nodes.append(new_node)
                self.G.add_edge(clause_nodes[0], clause_nodes[1])
                self.G.add_edge(clause_nodes[0], clause_nodes[2])
                self.G.add_edge(clause_nodes[1], clause_nodes[2])
        self.history["K cliques"] += k

    def clause_to_cluster(self, k=1):
        for clause_index in range(1, len(self.cnf.clauses) + 1):
            for i in range(1, k + 1):
                for literal_index in range(1, 4):
                    name = f"{clause_index}.{literal_index}.{i + self.history['K clusters']}.c"
                    new_node = Node(
                        name=name,
                        literal=self.cnf.clauses[clause_index - 1][literal_index - 1],
                        clause=self.cnf.clauses[clause_index - 1],
                        iteration=i + self.history["K clusters"],
                        cluster=True,
                    )
                    self.G.add_node(new_node)
        self.history["K clusters"] += k

    '''
    2. Literal Operations
    '''

    def literal_to_node(self, k=1):
        literals = set()
        for clause in self.cnf.clauses:
            for literal in clause:
                literals.add(literal)
        for literal in literals:
            for i in range(1, k + 1):
                name = f"{literal}.{i + self.history['K literals']}.l"
                new_node = Node(name=name, literal=literal, clause=None, iteration=i + self.history["K literals"])
                self.G.add_node(new_node)
        self.history["K literals"] += k

    def literal_and_negation_to_node(self, k=1):
        literals = set()
        for clause in self.cnf.clauses:
            for literal in clause:
                literals.add(abs(literal))
        for literal in literals:
            for i in range(1, k + 1):
                name = f"{literal}.{i + self.history['K literals and negs']}"
                p_node = Node(name=name + ".p", literal=literal, clause=None, iteration=i + self.history["K literals and negs"])
                n_node = Node(name=name + ".n", literal=-literal, clause=None, iteration=i + self.history["K literals and negs"])
                self.G.add_node(p_node)
                self.G.add_node(n_node)
        self.history["K literals and negs"] += k

    def variable_to_node(self, k=1):
        literals = set()
        for clause in self.cnf.clauses:
            for literal in clause:
                literals.add(abs(literal))
        for literal in literals:
            for i in range(1, k + 1):
                name = f"{literal}.{i + self.history['K Variables']}.v"
                new_node = Node(name=name, literal=literal, clause=None, iteration=i + self.history["K Variables"])
                self.G.add_node(new_node)
        self.history["K Variables"] += k

    '''
    3. Connection Functions
    '''

    @staticmethod
    def same_cluster(node_1: Node, node_2: Node):
        if node_1.inCluster() and node_2.inCluster():
            if node_1.getClause() == node_2.getClause():
                if node_1.getIteration() == node_2.getIteration():
                    return True
        return False

    '''
    3.1 Undirected Functions
    '''

    def all_to_all(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2):
                    self.G.add_edge(node_1, node_2)

    def x_to_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() == node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def x_to_not_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() == -node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def x_to_all_but_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() != node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def x_to_all_but_not_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() != -node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    '''
    3.2 Directed Functions
    '''

    def dir_all_to_all(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2):
                    self.G.add_edge(node_1, node_2)

    def dir_x_to_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() == node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def dir_x_to_not_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() == -node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def dir_x_to_all_but_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() != node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)

    def dir_x_to_all_but_not_x(self):
        node_list = list(self.G.nodes)
        for i in range(len(node_list)):
            node_1 = node_list[i]
            for j in range(len(node_list)):
                node_2 = node_list[j]
                if not self.same_cluster(node_1, node_2) and node_1.getLiteral() != -node_2.getLiteral():
                    self.G.add_edge(node_1, node_2)
                    
    ''' Plotting Methods '''

    def plot_graph(self):
        pos = nx.kamada_kawai_layout(self.G)
        fig = plt.figure(figsize=(12, 12))  # Create a new figure
        ax = fig.add_subplot(1, 1, 1)  # Add a subplot to the figure
        nx.draw(
            self.G,
            pos,
            with_labels=True,
            font_weight='bold',
            node_size=1800,
            node_color='lightgreen',
            font_size=10,
            ax=ax  # Pass the Axes instance to the drawing function
        )
        return fig  # Return the Figure object

    def to_d3_json(self):
        """
        Converts the graph to a JSON format compatible with D3.js.
        :return: JSON representation of the graph.
        """
        d3_json = {"nodes": [], "links": []}
        node_mapping = {}
        for i, node in enumerate(self.G.nodes):
            d3_json["nodes"].append({
                "id": i,
                "name": node.name,
                "strname": str(node),
                "literal": node.literal,
                "clause": node.clause,
                "iteration": node.iteration,
                "cluster": node.cluster,
                "group": node.name.split(".")[0],
            })
            node_mapping[node] = i

        for edge in self.G.edges:
            d3_json["links"].append({
                "source": node_mapping[edge[0]],
                "target": node_mapping[edge[1]],
                "value": 1,
            })

        return d3_json

    def save_d3_visualization(self, output_dir="graph"):
        """
        Saves the graph in a JSON format compatible with D3.js and generates an HTML file
        to visualize the graph.
        :param output_dir: Directory where the JSON and HTML files will be saved.
        """
        # Resolve the output directory to an absolute path
        output_dir = os.path.abspath(output_dir)

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Convert the graph to D3-compatible JSON
        d3_json = self.to_d3_json()
        json_path = os.path.join(output_dir, "graph.json")
        with open(json_path, "w") as f:
            json.dump(d3_json, f, indent=4)

        # Copy the template `graph.html` to `index.html` in the correct directory
        template_path = os.path.abspath("graph/graph/graph.html")
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template HTML file not found: {template_path}")

        # Save `index.html` in the specified output directory
        destination_html_path = os.path.join(output_dir, "index.html")
        with open(template_path, "r") as template_file:
            html_content = template_file.read()
        with open(destination_html_path, "w") as output_file:
            output_file.write(html_content)

        print(f"D3 visualization files saved in {output_dir}.")


