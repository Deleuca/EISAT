class Node:
    def __init__(self, name, literal, clause, iteration, cluster = False):
        self.name = name
        self.literal = literal
        self.clause = clause
        self.iteration = iteration
        self.cluster = cluster

    def __repr__(self):
        return f"{self.clause}: {self.literal}"
