"""Routines and class for all types of diagrams, inherited by others."""

from builtins import range
from builtins import object

import copy
import numpy
import networkx as nx


def no_trace(matrices):
    """Select matrices with full 0 diagonal.

    Args:
        matrices (list): A list of adjacency matrices.

    Returns:
        (list): The adjacency matrices without non-zero diagonal elements.

    >>> test_matrices = [[[0, 1, 2], [2, 0, 1], [5, 2, 0]], \
    [[2, 2, 2], [1, 2, 3], [0, 0, 0]], \
    [[0, 1, 3], [2, 0, 8], [2, 1, 0]]]
    >>> no_trace(test_matrices)
    [[[0, 1, 2], [2, 0, 1], [5, 2, 0]], [[0, 1, 3], [2, 0, 8], [2, 1, 0]]]

    """
    traceless_matrices = []
    for matrix in matrices:
        test_traceless = True
        for ind_i, line in enumerate(matrix):
            if line[ind_i] != 0:
                test_traceless = False
                break
        if test_traceless:
            traceless_matrices.append(matrix)
    return traceless_matrices


def check_vertex_degree(matrices, three_body_use, nbody_max_observable,
                        canonical_only, vertex_id):
    """Check the degree of a specific vertex in a set of matrices.

    Args:
        matrices (list): Adjacency matrices.
        three_body_use (bool): ``True`` if one uses three-body forces.
        nbody_max_observable (int): Maximum body number for the observable.
        canonical_only (bool): ``True`` if one draws only canonical diagrams.
        vertex_id (int): The position of the studied vertex.

    >>> test_matrices = [numpy.array([[0, 1, 2], [1, 0, 1], [0, 2, 0]]), \
        numpy.array([[2, 0, 2], [1, 2, 3], [1, 0, 0]]), \
        numpy.array([[0, 1, 3], [2, 0, 8], [2, 1, 0]])]
    >>> check_vertex_degree(test_matrices, True, 3, False, 0)
    >>> test_matrices #doctest: +NORMALIZE_WHITESPACE
    [array([[0, 1, 2], [1, 0, 1], [0, 2, 0]]),
     array([[2, 0, 2], [1, 2, 3], [1, 0, 0]])]
    >>> check_vertex_degree(test_matrices, False, 2, False, 0)
    >>> test_matrices #doctest: +NORMALIZE_WHITESPACE
    [array([[0, 1, 2], [1, 0, 1], [0, 2, 0]])]

    """
    authorized_deg = [4]
    if three_body_use:
        authorized_deg.append(6)
    if not canonical_only or vertex_id == 0:
        authorized_deg.append(2)
    authorized_deg = tuple(authorized_deg)

    for i_mat in range(len(matrices)-1, -1, -1):
        matrix = matrices[i_mat]
        vertex_degree = sum(matrix[index][vertex_id] + matrix[vertex_id][index]
                            for index in list(range(matrix.shape[0])))
        vertex_degree -= matrix[vertex_id][vertex_id]

        if (vertex_id != 0 and vertex_degree not in authorized_deg) \
                or (vertex_id == 0 and vertex_degree > 2*nbody_max_observable):
            del matrices[i_mat]


def topologically_distinct_diagrams(diagrams):
    """Return a list of diagrams all topologically distinct.

    Args:
        diagrams (list): The Diagrams of interest.

    Returns:
        (list): Topologically unique diagrams.

    """
    import adg.tsd
    iso = nx.algorithms.isomorphism
    op_nm = iso.categorical_node_match('operator', False)
    anom_em = iso.categorical_multiedge_match('anomalous', False)
    for i_diag in range(len(diagrams)-1, -1, -1):
        graph = diagrams[i_diag].graph
        diag_io_degrees = diagrams[i_diag].io_degrees
        for i_comp_diag in range(len(diagrams)-1, i_diag, -1):
            if diag_io_degrees == diagrams[i_comp_diag].io_degrees:
                # Check anomalous character of props for PBMBPT
                if isinstance(diagrams[i_diag],
                              adg.pbmbpt.ProjectedBmbptDiagram):
                    doubled_graph = create_checkable_diagram(graph)
                    doubled_comp_diag = create_checkable_diagram(diagrams[i_comp_diag].graph)
                    matcher = iso.DiGraphMatcher(doubled_graph,
                                                 doubled_comp_diag,
                                                 node_match=op_nm,
                                                 edge_match=anom_em)
                # Check for topolically equivalent diags considering vertex
                # properties but not edge attributes, i.e. anomalous character
                else:
                    matcher = iso.DiGraphMatcher(graph,
                                                 diagrams[i_comp_diag].graph,
                                                 node_match=op_nm)
                if matcher.is_isomorphic():
                    # Store the set of permutations to recover the original TSD
                    if isinstance(diagrams[i_diag],
                                  adg.tsd.TimeStructureDiagram):
                        diagrams[i_diag].perms.update(
                            update_permutations(diagrams[i_comp_diag].perms,
                                                diagrams[i_comp_diag].tags[0],
                                                matcher.mapping)
                            )
                    diagrams[i_diag].tags += diagrams[i_comp_diag].tags
                    del diagrams[i_comp_diag]
                    break
    return diagrams


def update_permutations(comp_graph_perms, comp_graph_tag, mapping):
    """Update permutations associated to the BMBPT diags for a shared TSD.

    Args:
        comp_graph_perms (dict): Permutations to be updated.
        comp_graph_tag (int): The tag associated to the TSD configuration.
        mapping (dict): permutations to go from previous ref TSD to new one.

    """
    identity = {key: key for key in comp_graph_perms[comp_graph_tag]}
    # Do permutations only when necessary
    if mapping != identity:
        for graph_id in comp_graph_perms:
            # Create a dummy dictionarry to avoid overwriting some nodes
            dummy_nodes = copy.deepcopy(comp_graph_perms[graph_id])
            # Permute the nodes according to the new mapping
            for node in comp_graph_perms[graph_id]:
                comp_graph_perms[graph_id][node] = dummy_nodes[mapping[node]]

    return comp_graph_perms


def create_checkable_diagram(pbmbpt_graph):
    """Return agraph with anomalous props going both ways for topo check.

    Args:
        pbmbpt_graph (NetworkX MultiDiGraph): The graph to be copied.

    Returns:
        (NetworkX MultiDiGraph): Graph with double the anomalous props.

    """
    doubled_graph = copy.deepcopy(pbmbpt_graph)
    props_to_add = []
    for prop in doubled_graph.edges(keys=True, data=True):
        if prop[3]['anomalous'] and not prop[0] == prop[1]:
            props_to_add.append((prop[1], prop[0]))
    for prop in props_to_add:
        doubled_graph.add_edge(prop[0], prop[1], anomalous=True, weight=1)
    return doubled_graph


def label_vertices(graphs_list, theory_type):
    """Account for different status of vertices in operator diagrams.

    Args:
        graphs_list (list): The Diagrams of interest.
        theory_type (str): The name of the theory of interest.

    """
    for graph in graphs_list:
        for node in graph:
            graph.node[node]['operator'] = False
        if theory_type == "BMBPT" or "PBMBPT":
            graph.node[0]['operator'] = True


# Previous versions working for theories other than PBMBPT
# def feynmf_generator(graph, theory_type, diagram_name):
#     """Generate the feynmanmp instructions corresponding to the diagram.
#
#     Args:
#         graph (NetworkX MultiDiGraph): The graph of interest.
#         theory_type (str): The name of the theory of interest.
#         diagram_name (str): The name of the studied diagram.
#
#     """
#     p_order = graph.number_of_nodes()
#     diag_size = 20*p_order
#
#     theories = ["MBPT", "BMBPT", "PBMBPT"]
#     prop_types = ["half_prop", "prop_pm", "prop_pm"]
#     propa = prop_types[theories.index(theory_type)]
#
#     fmf_file = open(diagram_name + ".tex", 'w')
#     fmf_file.write("\\parbox{%ipt}{\\begin{fmffile}{%s}\n" % (diag_size,
#                                                               diagram_name)
#                    + "\\begin{fmfgraph*}(%i,%i)\n" % (diag_size, diag_size))
#
#     # Define the appropriate line propagator_style
#     fmf_file.write(propagator_style(propa))
#     if theory_type == "PBMBPT":
#         fmf_file.write(propagator_style("prop_mm"))
#
#     # Set the position of the vertices
#     fmf_file.write(vertex_positions(graph, p_order))
#
#     # Loop over all elements of the graph to draw associated propagators
#     for vert_i in graph:
#         for vert_j in graph:
#             props_left_to_draw = graph.number_of_edges(vert_i, vert_j)
#             # Special config for consecutive vertices
#             if (props_left_to_draw % 2 == 1) and (abs(vert_i-vert_j) == 1):
#                 fmf_file.write("\\fmf{%s" % propa)
#                 # Check for specific MBPT configuration
#                 if graph.number_of_edges(vert_j, vert_i) == 1:
#                     fmf_file.write(",right=0.5")
#                 fmf_file.write("}{v%i,v%i}\n" % (vert_i, vert_j))
#                 props_left_to_draw -= 1
#             while props_left_to_draw > 0:
#                 fmf_file.write("\\fmf{%s," % propa)
#                 fmf_file.write("right=" if props_left_to_draw % 2 == 1
#                                else "left=")
#                 if props_left_to_draw in (5, 6):
#                     fmf_file.write("0.9")
#                 elif props_left_to_draw in (3, 4) \
#                         or (props_left_to_draw == 1
#                             and graph.number_of_edges(vert_j, vert_i) == 2):
#                     fmf_file.write("0.75")
#                 elif props_left_to_draw in (1, 2):
#                     fmf_file.write("0.5" if abs(vert_i-vert_j) == 1 else "0.6")
#                 fmf_file.write("}{v%i,v%i}\n" % (vert_i, vert_j))
#                 props_left_to_draw -= 1
#         # Special config for self-contraction
#         props_left_to_draw = len(list(edge for edge
#                                       in nx.selfloop_edges(graph,
#                                                            data=True,
#                                                            keys=True)
#                                       if edge[0] == vert_i))
#         while props_left_to_draw > 0:
#             if props_left_to_draw > 1:
#                 fmf_file.write("\\fmf{prop_mm,left=45}{v%i,v%i}\n"
#                                % (vert_i, vert_i))
#             else:
#                 fmf_file.write("\\fmf{prop_mm,right=45}{v%i,v%i}\n"
#                                % (vert_i, vert_i))
#             props_left_to_draw -= 1
#     fmf_file.write("\\end{fmfgraph*}\n\\end{fmffile}}\n")
#     fmf_file.close()


def feynmf_generator(graph, theory_type, diagram_name):
    """Generate the feynmanmp instructions corresponding to the diagram.

    Args:
        graph (NetworkX MultiDiGraph): The graph of interest.
        theory_type (str): The name of the theory of interest.
        diagram_name (str): The name of the studied diagram.

    """
    p_order = graph.number_of_nodes()
    diag_size = 20*p_order

    theories = ["MBPT", "BMBPT", "PBMBPT"]
    prop_types = ["half_prop", "prop_pm", "prop_pm"]
    propa = prop_types[theories.index(theory_type)]

    fmf_file = open(diagram_name + ".tex", 'w')
    fmf_file.write("\\parbox{%ipt}{\\begin{fmffile}{%s}\n" % (diag_size,
                                                              diagram_name)
                   + "\\begin{fmfgraph*}(%i,%i)\n" % (diag_size, diag_size))

    # Define the appropriate line propagator_style
    fmf_file.write(propagator_style(propa))
    if theory_type == "PBMBPT":
        fmf_file.write(propagator_style("prop_mm"))

    # Set the position of the vertices
    fmf_file.write(vertex_positions(graph, p_order))

    # Special config for self-contraction
    if theory_type == "PBMBPT":
        fmf_file.write(self_contractions(graph))

    directions = [",left=0.9", ",left=0.75", ",left=0.6", ",left=0.5", "",
                  ",right=0.5", ",right=0.6", ",right=0.75", ",right=0.9"]

    # Loop over all elements of the graph to draw associated propagators
    for vert_i in graph:
        for vert_j in list(graph.nodes())[vert_i+1:]:
            props_to_draw = [edge for edge in graph.edges([vert_i, vert_j],
                                                          data=True, keys=True)
                             if edge[1] in (vert_i, vert_j)
                             and edge[0] != edge[1]]
            # Set the list of propagators directions to use
            if vert_j - vert_i != 1:
                props_dir = directions[:3] + directions[-3:]
            else:
                props_dir = directions[:2] + directions[3:6] + directions[-2:]
                if len(props_to_draw) % 2 != 1:
                    props_dir = props_dir[:3] + props_dir[-3:]
                else:
                    props_dir = props_dir[1:]
            if len(props_to_draw) < 5:
                props_dir = props_dir[1:-1]
                if len(props_to_draw) < 3:
                    props_dir = props_dir[1:-1]
            # Draw the diagrams
            key = 0
            for prop in props_to_draw:
                if prop[1] < prop[0] \
                        and not ('anomalous' in prop[3]
                                 and prop[3]['anomalous']):
                    fmf_file.write("\\fmf{%s%s}{v%i,v%i}\n"
                                   % (propa, props_dir[key], vert_j, vert_i))
                    key += 1
            for prop in props_to_draw:
                if prop[0] < prop[1] \
                        and not ('anomalous' in prop[3]
                                 and prop[3]['anomalous']):
                    fmf_file.write("\\fmf{%s%s}{v%i,v%i}\n"
                                   % (propa, props_dir[key], vert_i, vert_j))
                    key += 1
            for prop in props_to_draw:
                if 'anomalous' in prop[3] and prop[3]['anomalous']:
                    fmf_file.write("\\fmf{prop_mm%s}{v%i,v%i}\n"
                                   % (props_dir[key], vert_i, vert_j))
                    key += 1

    fmf_file.write("\\end{fmfgraph*}\n\\end{fmffile}}\n")
    fmf_file.close()


def propagator_style(prop_type):
    """Return the FeynMF definition for the appropriate propagator type.

    Args:
        prop_type (str): The type of propagators used in the diagram.

    Returns:
        (str): The FeynMF definition for the propagator style used.

    """
    line_styles = {}

    line_styles['prop_pm'] = "\\fmfcmd{style_def prop_pm expr p =\n" \
        + "draw_plain p;\nshrink(.7);\n" \
        + "\tcfill (marrow (p, .25));\n" \
        + "\tcfill (marrow (p, .75))\n" \
        + "endshrink;\nenddef;}\n"

    line_styles['prop_mm'] = "\\fmfcmd{style_def prop_mm expr p =\n" \
        + "draw_plain p;\nshrink(.7);\n" \
        + "\tcfill (marrow (p, .75));\n" \
        + "\tcfill (marrow (reverse p, .75))\n" \
        + "endshrink;\nenddef;}\n"

    line_styles['half_prop'] = "\\fmfcmd{style_def half_prop expr p =\n" \
        + "draw_plain p;\nshrink(.7);\n" \
        + "\tcfill (marrow (p, .5))\n" \
        + "endshrink;\nenddef;}\n"

    return line_styles[prop_type]


def vertex_positions(graph, order):
    """Return the positions of the graph's vertices.

    Args:
        graph (NetworkX MultiDiGraph): The graph of interest.
        order (int): The perturbative order of the graph.

    Returns:
        (str): The FeynMP instructions for positioning the vertices.

    """
    positions = "\\fmftop{v%i}\\fmfbottom{v0}\n" % (order-1)
    for vert in range(order-1):
        positions += "\\fmf{phantom}{v%i,v%i}\n" % (vert, (vert+1)) \
            + ("\\fmfv{d.shape=square,d.filled=full,d.size=3thick"
               if graph.node[vert]['operator']
               else "\\fmfv{d.shape=circle,d.filled=full,d.size=3thick") \
            + "}{v%i}\n" % vert
    positions += "\\fmfv{d.shape=circle,d.filled=full,d.size=3thick}{v%i}\n" \
        % (order-1) + "\\fmffreeze\n"
    return positions


def self_contractions(graph):
    """Return the instructions for drawing the graph's self-contractions.

    Args:
        graph (NetworkX MultiDiGraph): The graph being drawn.

    Returns:
        (str): FeynMF instructions for drawing the self-contractions.

    """
    instructions = ""
    # Check for self-contractions before going further
    if [nx.selfloop_edges(graph)]:
        instructions += propagator_style("half_prop")
        for vert in graph:
            props_to_draw = [edge for edge
                             in nx.selfloop_edges(graph, data=True, keys=True)
                             if edge[0] == vert]
            positions = ["15pt", "-15pt"]
            key = 0
            for prop in props_to_draw:
                if prop[3]['anomalous']:
                    a_name = "a%i%i" % (vert, key)
                    instructions += ("\\fmfv{}{%s}\n" % a_name
                                     + "\\fmffixed{(%s,0)}{v%i,%s}\n"
                                     % (positions[key], vert, a_name)
                                     + "\\fmf{half_prop,right}{%s,v%i}\n"
                                     % (a_name, vert)
                                     + "\\fmf{half_prop,left}{%s,v%i}\n"
                                     % (a_name, vert))
                    key += 1
        instructions += "\\fmffreeze\n"
    return instructions


def draw_diagram(directory, result_file, diagram_index, diag_type):
    """Copy the diagram feynmanmp instructions in the result file.

    Args:
        directory (str): The path to the output folder.
        result_file (file): The LaTeX ouput file of the program.
        diagram_index (str): The number associated to the diagram.
        diag_type (str): The type of diagram used here.

    """
    diag_file = open(directory+"/Diagrams/%s_%s.tex" % (diag_type,
                                                        diagram_index))
    result_file.write(diag_file.read())
    diag_file.close()


def to_skeleton(graph):
    """Return the bare skeleton of a graph, i.e. only non-redundant links.

    Args:
        graph (NetworkX MultiDiGraph): The graph to be turned into a skeleton.

    Returns:
        (NetworkX MultiDiGraph): The skeleton of the initial graph.

    """
    for vertex_a in graph:
        for vertex_b in graph:
            while graph.number_of_edges(vertex_a, vertex_b) > 1:
                graph.remove_edge(vertex_a, vertex_b)
            if len(list(nx.all_simple_paths(graph, vertex_a, vertex_b))) > 1:
                while len(nx.shortest_path(graph, vertex_a, vertex_b)) == 2:
                    graph.remove_edge(vertex_a, vertex_b)
    return graph


def extract_denom(start_graph, subgraph):
    """Extract the appropriate denominator using the subgraph rule.

    Args:
        start_graph (NetworkX MultiDiGraph): The studied graph.
        subgraph (NetworkX MultiDiGraph): The subgraph used for this particular
            denominator factor.

    Returns:
        (str): The denominator factor for this subgraph.

    """
    denomin = r"\epsilon^{" \
        + "".join("%s"
                  % prop[3]['qp_state']
                  for prop
                  in start_graph.out_edges(subgraph, keys=True, data=True)
                  if not subgraph.has_edge(prop[0], prop[1], prop[2])
                  and not ('anomalous' in prop[3] and prop[3]['anomalous'])) \
        + "}_{" \
        + "".join("%s"
                  % prop[3]['qp_state']
                  for prop
                  in start_graph.in_edges(subgraph, keys=True, data=True)
                  if not subgraph.has_edge(prop[0], prop[1], prop[2])
                  and not ('anomalous' in prop[3] and prop[3]['anomalous'])) \
        + "".join("%s"
                  % prop[3]['qp_state']
                  for prop
                  in start_graph.in_edges(subgraph, keys=True, data=True)
                  if subgraph.has_edge(prop[0], prop[1], prop[2])
                  and ('anomalous' in prop[3] and prop[3]['anomalous'])) \
        + "".join("%s"
                  % (prop[3]['qp_state'].split("}")[1] + "}")
                  for prop
                  in start_graph.in_edges(subgraph, keys=True, data=True)
                  if not subgraph.has_edge(prop[0], prop[1], prop[2])
                  and ('anomalous' in prop[3] and prop[3]['anomalous'])) \
        + "".join("%s"
                  % (prop[3]['qp_state'].split("}")[0] + "}")
                  for prop
                  in start_graph.out_edges(subgraph, keys=True, data=True)
                  if not subgraph.has_edge(prop[0], prop[1], prop[2])
                  and ('anomalous' in prop[3] and prop[3]['anomalous'])) \
        + "}"
    return denomin


def print_adj_matrices(directory, diagrams):
    """Print a computer-readable file with the diagrams' adjacency matrices.

    Args:
        directory (str): The path to the output directory.
        diagrams (list): All the diagrams.

    """
    with open(directory+"/adjacency_matrices.txt", "w") as mat_file:
        for idx, diagram in enumerate(diagrams):
            mat_file.write("Diagram n: %i\n" % (idx + 1))
            numpy.savetxt(mat_file,
                          nx.to_numpy_matrix(diagram.graph, dtype=int),
                          fmt='%d')
            mat_file.write("\n")


class Diagram(object):
    """Describes a diagram with its related properties.

    Attributes:
        graph (NetworkX MultiDiGraph): The actual graph.
        unsorted_degrees (tuple): The degrees of the graph vertices
        degrees (tuple): The ascendingly sorted degrees of the graph vertices.
        unsort_io_degrees (tuple): The list of in- and out-degrees for each
            vertex of the graph, stored in a (in, out) tuple.
        io_degrees (tuple): The sorted version of unsort_io_degrees.
        max_degree (int): The maximal degree of a vertex in the graph.
        tags (list): The tag numbers associated to a diagram.

    """

    __slots__ = ('graph', 'unsort_degrees', 'degrees', 'unsort_io_degrees',
                 'io_degrees', 'max_degree', 'tags')

    def __init__(self, nx_graph):
        """Generate a Diagram object starting from the NetworkX graph.

        Args:
            nx_graph (NetworkX MultiDiGraph): The graph of interest.

        """
        self.graph = nx_graph
        self.unsort_degrees = tuple(nx_graph.degree(node) for node in nx_graph)
        self.degrees = tuple(sorted(self.unsort_degrees))
        self.unsort_io_degrees = tuple((nx_graph.in_degree(node),
                                        nx_graph.out_degree(node))
                                       for node in nx_graph)
        self.io_degrees = tuple(sorted(self.unsort_io_degrees))
        self.max_degree = self.degrees[-1]
        self.tags = [0]

    def write_graph(self, latex_file, directory, write_time):
        """Write the graph of the diagram to the LaTeX file.

        Args:
            latex_file (file): The LaTeX ouput file of the program.
            directory (str): Path to the result folder.
            write_time (bool): (Here to emulate polymorphism).

        """
        latex_file.write('\n\\begin{center}\n')
        draw_diagram(directory, latex_file, self.tags[0], 'diag')
        latex_file.write('\n\\end{center}\n\n')
