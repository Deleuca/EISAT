class Variable:
    def __init__(self, name: str):
        """
        Represents a boolean variable as a general term.
        
       	:param name: The name of the variable
       	"""
       	self.name = name
    def getName(self):
        return self.name
    def __str__(self):
    	return self.name

class Literal:
    def __init__(self, variable: Variable, negated: bool = False):
        """
        Represents a Boolean literal, which can be negated.
        
        :param variable: The name of the variable (e.g., "x1", "x2").
        :param negated: Whether the literal is negated.
        """
        self.variable = variable
        self.negated = negated
    
    def getVariable(self):
    	return self.variable
    def getName(self):
    	return self.variable.getName()
    def isNegated(self):
    	return self.negated
    def __str__(self):
        return f"{'¬' if self.negated else ''}{self.variable.getName()}"
    
class Clause:
    def __init__(self, literal_1: Literal, literal_2: Literal, literal_3: Literal):
        """
        Represents a 3-variable clause in a SAT formula.
        
        :param literal_1: First literal in the clause.
        :param literal_2: Second literal in the clause.
        :param literal_3: Third literal in the clause.
        """
        self.literals = [literal_1, literal_2, literal_3]
    def getLiterals(self):
        return self.literals
    def __str__(self):
        return f"({self.literals[0]} ∨ {self.literals[1]} ∨ {self.literals[2]})"
