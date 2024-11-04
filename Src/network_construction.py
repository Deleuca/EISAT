import networkx as nx
from sat_classes import Variable, Literal, Clause

G = nx.Graph()

variables = []
clauses = []


'''
3-SAT Problem Istantiation Methods
'''

def new_variable(name: str):
    for variable in variables:
        if variable.getName() == name:
            print("Variable already exists.")
            return
    new_var = Variable(name)
    variables.append(new_var)
    return new_var
    
def new_clause(literal_1: Literal, literal_2: Literal, literal_3: Literal):
    new_clause = Clause(literal_1, literal_2, literal_3)
    clauses.append(new_clause)
    return new_clause
    
def find_variable(name: str):
    for i in variables:
        if i.getName() == name:
            return i
    return None
    
def parse_clause(string: str):
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
    

'''
Network Construction Methods
'''

'''
1. Variable Operations
'''

def variables_to_nodes():
    for variable in variables:
        name = variable.getName()
        G.add_node(name)

'''
2. Clause Operations
'''

def create_cliques(k = 1):
    if i == 1:
        for clause in clauses:
            literals = clause.getLiterals()
            
            G.add_node(str(literals[0]))
            G.add_node(str(literals[1]))
            G.add_node(str(literals[2]))

            G.add_edge(str(literals[0]), str(literals[1]))
            G.add_edge(str(literals[1]), str(literals[2]))
            G.add_edge(str(literals[0]), str(literals[2]))
        return    
    for i in k:
        for clause in clauses:
            literals = clause.getLiterals()
            
            l0 = str(literals[0]) + "_" + str(i)
            l1 = str(literals[1]) + "_" + str(i)
            l2 = str(literals[2]) + "_" + str(i)

            G.add_node(l0)
            G.add_node(l1)
            G.add_node(l2)

            G.add_edge(l0, l1)
            G.add_edge(l1, l2)
            G.add_edge(l0, l2)