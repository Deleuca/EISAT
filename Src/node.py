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

    def to_dict(self):
        return {
            "name": self.name,
            "strname": str(self),
            "literal": self.literal,
            "clause": self.clause,
            "iteration": self.iteration,
            "cluster": self.cluster,
        }

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Node) and self.name == other.name

    def __repr__(self):
        return f"{self.clause}: {self.literal}"

    def __str__(self):
        return f"$x_{{{self.literal}}}$" if self.literal > 0 else f"$\\neg x_{{{str(self.literal)[1:]}}}$"

    def __lt__(self, other):
        return self.name < other.name