class Literal:
    def __init__(self, name: str, negated: bool = False):
        """
        Represents a Boolean literal, which can be negated.
        
        :param name: The name of the variable (e.g., "x1", "x2").
        :param negated: Whether the literal is negated.
        """
        self.name = name
        self.negated = negated
    
    def __repr__(self):
        return f"{'¬' if self.negated else ''}{self.name}"
    
class Clause:
    def __init__(self, var1: Literal, var2: Literal, var3: Literal):
        """
        Represents a 3-variable clause in a SAT formula.
        
        :param var1: First variable in the clause.
        :param var2: Second variable in the clause.
        :param var3: Third variable in the clause.
        """
        self.variables = [var1, var2, var3]
    
    def __repr__(self):
        return f"({self.variables[0]} ∨ {self.variables[1]} ∨ {self.variables[2]})"

