1. Create Variables as Vertices
Operation: create_variable_vertex(var_name)
Description: Adds a vertex to the graph for each SAT variable. This operation allows for representing variables as nodes in a graph.

2. Create Literal Vertices
Operation: create_literal_vertex(var_name, is_negated)
Description: Creates a vertex for each literal (either the variable or its negation). This operation distinguishes between positive and negative literals.

3. Create Edges Between Variables or Literals
Operation: create_edge(vertex_1, vertex_2)
Description: Adds an edge between two specified vertices. Useful for creating edges between variables, literals, or other elements of the graph.

4. Create Clique
Operation: create_clique(vertices_list)
Description: Takes a list of vertices and fully connects them, forming a clique. This operation is useful in reductions like SAT to Clique.

5. Create Opposite Literal Edges
Operation: create_opposite_literal_edges(var_name)
Description: Automatically creates edges between each literal and its opposite (negation). This is crucial in reductions to problems like Independent Set, where variables and their negations cannot both be true.

6. Create Clause as k-Clique
Operation: create_clause_clique(literals_list)
Description: Given a list of literals from a SAT clause, forms a k-clique (with k equal to the number of literals). This operation handles the common need to represent clauses as cliques.

7. Create Independent Set
Operation: create_independent_set(vertices_list)
Description: Takes a list of vertices and ensures no edges exist between them, forming an independent set. This is useful in reductions to problems like Independent Set or Vertex Cover.

8. Assign Weight to Edges
Operation: assign_weight(edge, weight_value)
Description: Assigns a weight to an edge between two vertices. This operation is essential for weighted graph problems, such as reductions to the Knapsack problem or Weighted Vertex Cover.

9. Connect Variables to Clauses
Operation: connect_literal_to_clause(var_literal, clause_clique)
Description: Connects a variable (or its literal) to a clause, often by adding edges between the variable's vertex and vertices representing the clause.

10. Create Bipartite Graph
Operation: create_bipartite_set(set_1, set_2)
Description: Creates a bipartite graph with two sets of vertices (i.e., edges only between vertices in different sets). This is useful for reductions like SAT to Bipartite Matching.

11. Force Truth Assignment by Deleting or Forbidding Edges
Operation: forbid_edge(vertex_1, vertex_2)
Description: Ensures that two specific vertices are not connected by an edge, which can be interpreted as preventing certain combinations from being true.

12. Create Hamiltonian Path Structure
Operation: create_hamiltonian_path(vertices_list)
Description: For reductions like SAT to Hamiltonian Path, this operation creates a path that visits each vertex exactly once.

13. Color Vertices or Edges
Operation: color_vertex(vertex, color)
Operation: color_edge(edge, color)
Description: Allows the user to color specific vertices or edges, which is useful for reductions involving graph coloring problems (e.g., SAT to 3-Colorability).

