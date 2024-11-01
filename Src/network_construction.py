import networkx as nx
from sat_classes import Variable, Literal, Clause

variables = []
clauses = []

def newVariable(name: str):
    new_var = Variable(name)
    variables.append(new_var)
    return new_var
    
def newClause(literal_1: Literal, literal_2: Literal, literal_3: Literal):
    new_clause = Clause(literal_1, literal_2, literal_3)
    clauses.append(new_clause)
    return new_clause
    
def findVariable(name: str):
    for i in variables:
        if i.getName() == name:
            return i
    return None
    
def parseClause(string: str):
    # Note: Special characters: "V", "v", and "!"> Any other character is considered a variable.
    literals = []
    sep_list = string.split()
    for i in sep_list:
        if i == "V" or i == "v":
            continue
        else:
            if i[0] == "!": # which indicates negation
                name = i[1:]
                var = findVariable(name)
                if var is None:
                    new_var = newVariable(name)
                    new_literal = Literal(new_var, True)
               	else:
               	    new_literal = Literal(var, True)
               	literals.append(new_literal)
            else:
                var = findVariable(i)
                if var is None:
                    new_var = newVariable(i)
                    new_literal = Literal(new_var, False)
               	else:
               	    new_literal = Literal(var, False)
               	literals.append(new_literal)
    new_clause = newClause(literals[0], literals[1], literals[2])
    return new_clause
    

                    
