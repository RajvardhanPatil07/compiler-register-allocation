import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import networkx as nx
import pandas as pd
import streamlit as st

from src.clique import maximum_clique
from src.coloring import color_graph, coloring_count
from src.coloring_tools import compare_coloring_strategies, exact_coloring
from src.graph_stats import (
    adjacency_matrix,
    check_handshake_lemma,
    connected_components,
    degree_sequence,
    degree_table,
)
from src.interference import build_interference_graph, graph_statistics
from src.liveness import analyze_liveness
from src.parser import parse_program


st.set_page_config(
    page_title="Register Allocation | Graph Coloring Laboratory",
    page_icon="🔢",
    layout="wide",
)
st.title("Register Allocation Through Graph Coloring")
st.caption("DISCRETE MATHEMATICS LABORATORY  •  COMPILER DESIGN  •  GRAPH THEORY")
st.markdown(
    "Explore how variable liveness determines interference relationships and how "
    "graph coloring maps variables to a limited set of registers."
)

examples = {
    "Custom Program": "",
    "Multiplication and Division": """t1 = a * b
t2 = t1 / c
t3 = t2 + d
result = t3 - e""",
    "Modulo and Copy Assignment": """x = a % b
y = x
z = y * c
result = z + d""",
    "Mixed Arithmetic Operations": """t1 = a * b
t2 = c / d
t3 = t1 + t2
t4 = t3 % e
result = t4 - f""",
    "Extended Instruction Sequence": """p = a * b
q = p + c
r = q / d
s = r % e
t = s + p
result = t * f""",
    "High Interference": """t1 = a + b
t2 = c + d
t3 = e + f
t4 = t1 + t2
t5 = t3 + t4
result = t5 + a""",
    "Isolated Variable": """a = b + c
d = a * e
unused = d + c""",
}

st.subheader("Program Configuration")
example_name = st.selectbox(
    "Example program",
    list(examples.keys()),
    index=3,
    help="Select a predefined program or choose Custom Program to enter your own instructions.",
)
default_program = examples[example_name]
if example_name == "Custom Program":
    default_program = """a = b + c
d = a + e
f = d + c
g = f + a"""
program = st.text_area(
    "Three-address code",
    value=default_program,
    height=180,
    help=(
        "Supported format: destination = value, or destination = value operator value. "
        "Operators: +, -, *, /, %. Each instruction may contain at most one operator."
    ),
)
register_count = st.slider(
    "Available register count",
    min_value=1,
    max_value=12,
    value=3,
    help="Set the register budget used to evaluate the coloring result.",
)
st.divider()

try:
    instructions = parse_program(program)
    live_in, live_out = analyze_liveness(instructions)
    graph = build_interference_graph(instructions, live_in, live_out)
    stats = graph_statistics(graph)
    coloring = color_graph(graph)
    used_colors = coloring_count(coloring)
    greedy_fits = used_colors <= register_count

    st.subheader("01  |  Instruction Parsing")
    rows = [
        {
            "Instruction": item.number,
            "Three-Address Code": item.text,
            "USE": ", ".join(sorted(item.use)) or "∅",
            "DEF": ", ".join(sorted(item.define)) or "∅",
        }
        for item in instructions
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("What this means: USE lists values read by an instruction; DEF lists the value it writes.")

    st.subheader("02  |  Liveness Analysis")
    rows = [
        {
            "Instruction": item.number,
            "Three-Address Code": item.text,
            "LIVE-IN": ", ".join(sorted(live_in[index])) or "∅",
            "LIVE-OUT": ", ".join(sorted(live_out[index])) or "∅",
        }
        for index, item in enumerate(instructions)
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("What this means: LIVE-IN and LIVE-OUT show which variables may still be needed around each instruction.")

    st.subheader("03  |  Interference Graph")
    st.caption("What this means: vertices are variables and edges connect variables that cannot share a register.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vertices", stats["vertices"])
    c2.metric("Edges", stats["edges"])
    c3.metric("Maximum Vertex Degree", stats["max_degree"])
    c4.metric("Connected Components", stats["connected_components"])

    with st.expander("Degree table, degree sequence and handshake lemma", expanded=True):
        st.dataframe(degree_table(graph), use_container_width=True, hide_index=True)
        st.caption("What this means: the degree of a variable is the number of variables it interferes with.")
        st.write("Degree sequence (high to low):", degree_sequence(graph))
        st.caption("What this means: the degree sequence is the sorted list of all vertex degrees.")
        handshake = check_handshake_lemma(graph)
        handshake_rows = [{
            "Sum of degrees": handshake["degree_sum"],
            "2 × number of edges": handshake["twice_edges"],
            "Equal?": "Yes" if handshake["holds"] else "No",
        }]
        st.dataframe(pd.DataFrame(handshake_rows), use_container_width=True, hide_index=True)
        st.caption("What this means: each undirected edge contributes one degree at both endpoints.")

    with st.expander("Adjacency matrix", expanded=False):
        st.dataframe(adjacency_matrix(graph), use_container_width=True)
        st.caption("What this means: 1 means two variables share an interference edge; 0 means they do not.")

    components = connected_components(graph)
    component_rows = [
        {"Component": index + 1, "Variables": ", ".join(component)}
        for index, component in enumerate(components)
    ]
    st.dataframe(pd.DataFrame(component_rows), use_container_width=True, hide_index=True)
    st.caption("What this means: a connected component is a group of variables joined by paths.")

    if graph.number_of_edges():
        with st.expander("View interference edge list"):
            edge_rows = [
                {"Variable 1": left, "Variable 2": right}
                for left, right in sorted(graph.edges())
            ]
            st.dataframe(pd.DataFrame(edge_rows), use_container_width=True, hide_index=True)
            st.caption("What this means: every edge identifies a pair that must receive different colors.")

    if graph.number_of_nodes():
        positions = nx.kamada_kawai_layout(graph)
        register_palette = plt.get_cmap("tab20")
        component_palette = plt.get_cmap("hsv", max(1, len(components)))
        component_lookup = {}
        for component_index, component in enumerate(components):
            for variable in component:
                component_lookup[variable] = component_index
        node_colors = [register_palette(coloring[node] % 20) for node in graph.nodes()]
        outline_colors = [component_palette(component_lookup[node]) for node in graph.nodes()]
        labels = {node: f"{node}\nR{coloring[node] + 1}" for node in graph.nodes()}

        fig, ax = plt.subplots(figsize=(12, 8))
        nx.draw_networkx_edges(graph, positions, ax=ax, edge_color="gray", width=1.4)
        nx.draw_networkx_nodes(
            graph,
            positions,
            ax=ax,
            node_color=node_colors,
            node_size=1500,
            edgecolors=outline_colors,
            linewidths=3.0,
        )
        nx.draw_networkx_labels(graph, positions, labels=labels, ax=ax, font_size=9, font_weight="bold")
        register_handles = [
            Patch(facecolor=register_palette(index % 20), edgecolor="black", label=f"R{index + 1}")
            for index in range(used_colors)
        ]
        component_handles = [
            Patch(facecolor="white", edgecolor=component_palette(index), label=f"Component {index + 1}")
            for index in range(len(components))
        ]
        register_legend = ax.legend(handles=register_handles, title="Register fill", loc="upper right")
        ax.add_artist(register_legend)
        ax.legend(handles=component_handles, title="Component outline", loc="lower right", fontsize=8)
        ax.set_axis_off()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.caption("What this means: node fill shows the assigned register; outline color identifies the connected component.")

    clique_vertices, clique_size = maximum_clique(graph)
    st.subheader("Maximum Clique")
    st.write(f"Largest clique: {{{', '.join(clique_vertices)}}} (size {clique_size}).")
    st.caption(
        f"A clique of size {clique_size} needs at least {clique_size} registers, "
        f"so {clique_size} is a lower bound."
    )

    st.subheader("04  |  Register Allocation")
    allocation_rows = []
    for variable in sorted(graph.nodes()):
        color = coloring[variable]
        allocation_rows.append({
            "Variable": variable,
            "Color Index": color,
            "Assigned Register": f"R{color + 1}",
            "Vertex Degree": graph.degree(variable),
        })
    st.dataframe(pd.DataFrame(allocation_rows), use_container_width=True, hide_index=True)
    st.caption("What this means: every edge must have endpoints with different register labels.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Colors Used by Greedy Algorithm", used_colors)
    c2.metric("Available Registers", register_count)
    if greedy_fits:
        c3.metric("Unused Registers", register_count - used_colors)
        st.success(
            f"Register budget satisfied: {used_colors} color(s) fit within "
            f"{register_count} register(s)."
        )
    else:
        c3.metric("Register Budget Deficit", used_colors - register_count)
        st.warning(
            f"The current greedy coloring uses {used_colors} color(s), exceeding "
            f"the available budget of {register_count} register(s)."
        )

    st.subheader("Greedy Strategy Comparison")
    strategy_results = compare_coloring_strategies(graph)
    strategy_rows = [
        {key: value for key, value in result.items() if key != "Coloring"}
        for result in strategy_results
    ]
    st.dataframe(pd.DataFrame(strategy_rows), use_container_width=True, hide_index=True)
    st.caption("What this means: each greedy strategy chooses the next vertex in a different order.")

    exact_count, exact_assignment = exact_coloring(graph)
    if exact_count is None:
        st.info("graph too large for exact search")
    else:
        st.write(f"Greedy used {used_colors} colors, the exact minimum is {exact_count}.")
        st.caption("What this means: the chromatic number is the fewest colors that can color every edge properly.")
        if used_colors > exact_count:
            st.warning("Greedy coloring is not always optimal; another valid coloring uses fewer colors.")
    st.caption("Finding the exact chromatic number is NP-complete, so real compilers use heuristics.")

    st.info(
        "**Graph-coloring model:** variables are vertices, interference relationships "
        "are edges, and registers are colors. Adjacent vertices must receive different colors."
    )
    st.subheader("05  |  Interactive Experiments")
    st.markdown(
        """
Use the controls above to investigate the relationship between program structure and register allocation.

- **Vary the register budget:** compare the allocation result with 2, 3, and 4 available registers.
- **Modify the instruction sequence:** add or remove an instruction and observe changes in liveness and interference.
- **Examine an isolated vertex:** select Isolated Variable and inspect the graph for a variable with no interference edges.
- **Compare program structures:** select different examples to compare graph statistics and register assignments.
- **Evaluate input validation:** enter an unsupported expression and review the diagnostic message.
        """
    )
except ValueError as exc:
    st.warning("Analysis could not be completed for the current input.")
    st.error(f"Input validation: {exc}")
    st.caption("Review the instruction format, correct the reported issue, or select a predefined example.")
