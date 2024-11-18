class Node:
    def __init__(self, name, literal, clause, iteration, cluster = False):
        self.name = name
        self.literal = literal
        self.clause = clause
        self.iteration = iteration
        self.cluster = cluster
    def getName(self):
        return self.name
    def getLiteral(self):
        return self.literal
    def getClause(self):
        return self.clause
    def getIteration(self):
        return self.iteration
    def inCluster(self):
        return self.cluster
    def __repr__(self):
        return f"{self.clause}: {self.literal}"
