import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import networkx as nx
import pandas as pd
import streamlit as st

from src.clique import maximum_clique
from src.coloring import color_graph, coloring_count
from src.coloring_tools import coloring_steps, compare_coloring_strategies, exact_coloring
from src.graph_stats import (
    adjacency_matrix,
    check_handshake_lemma,
    connected_components,
    degree_sequence,
    degree_table,
)
from src.interference import build_interference_graph, graph_statistics
from src.liveness import analyze_liveness, liveness_equation
from src.live_ranges import build_live_ranges
from src.relation_check import build_complement_graph, check_relation_properties
from src.validity import check_coloring_validity
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
            "Set equation": liveness_equation(
                item.use, live_out[index], item.define, live_in[index]
            ),
        }
        for index, item in enumerate(instructions)
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("What this means: union (∪) adds USE variables; set difference (−) removes variables defined by this instruction.")

    st.subheader("Live Range Timeline")
    live_range_rows = build_live_ranges(instructions, live_in, live_out)
    live_range_frame = pd.DataFrame(live_range_rows)
    st.dataframe(live_range_frame, use_container_width=True, hide_index=True)
    st.caption("What this means: each bar spans a variable's live range across instruction numbers.")
    if live_range_rows:
        timeline_fig, timeline_ax = plt.subplots(figsize=(10, max(3, len(live_range_rows) * 0.35)))
        for row_index, row in enumerate(live_range_rows):
            timeline_ax.barh(
                row["Variable"],
                row["End"] - row["Start"] + 0.7,
                left=row["Start"] - 0.35,
            )
        timeline_ax.set_xlabel("Instruction number")
        timeline_ax.set_ylabel("Variable")
        timeline_ax.set_xticks([item.number for item in instructions])
        timeline_ax.grid(axis="x", linestyle=":", alpha=0.4)
        timeline_fig.tight_layout()
        st.pyplot(timeline_fig, use_container_width=True)
        plt.close(timeline_fig)
    st.caption("Two variables whose bars overlap interfere, so they get an edge.")

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
    st.subheader("Interference Relation")
    relation_details = check_relation_properties(graph)
    relation_rows = [
        {"Property": "Reflexive", "Result": "Yes" if relation_details["reflexive"] else "No"},
        {"Property": "Irreflexive", "Result": "Yes" if relation_details["irreflexive"] else "No"},
        {"Property": "Symmetric", "Result": "Yes" if relation_details["symmetric"] else "No"},
        {"Property": "Transitive", "Result": "Yes" if relation_details["transitive"] else "No"},
    ]
    st.dataframe(pd.DataFrame(relation_rows), use_container_width=True, hide_index=True)
    st.caption("What this means: R contains ordered pairs of variables that interfere; undirected edges give symmetry.")
    if relation_details["counterexample"] is not None:
        first, middle, last = relation_details["counterexample"]
        st.write(f"Transitivity counter-example: ({first}, {middle}) and ({middle}, {last}) are in R, but ({first}, {last}) is not.")
        st.warning("R is not an equivalence relation because it is not transitive.")
    else:
        st.write("No transitivity counter-example exists, so the relation is transitive for this input.")

    st.subheader("Complement Graph")
    complement = build_complement_graph(graph)
    if complement.number_of_nodes():
        complement_positions = nx.spring_layout(complement, seed=17)
        complement_fig, complement_ax = plt.subplots(figsize=(9, 5))
        nx.draw_networkx(
            complement,
            complement_positions,
            ax=complement_ax,
            node_color="lightblue",
            edge_color="gray",
            node_size=1100,
            font_weight="bold",
        )
        complement_ax.set_axis_off()
        st.pyplot(complement_fig, use_container_width=True)
        plt.close(complement_fig)
    st.caption("What this means: these pairs can safely share a register.")

    st.subheader("Step-by-Step Coloring")
    steps = coloring_steps(graph)
    if steps:
        if "coloring_step" not in st.session_state or st.session_state.coloring_step > len(steps):
            st.session_state.coloring_step = 1
        step_number = st.slider("Coloring step", min_value=1, max_value=len(steps), key="coloring_step")
        current_step = steps[step_number - 1]
        used_by_neighbors = ", ".join(f"R{color + 1}" for color in current_step["neighbor_colors"])
        st.write(
            f"Vertex {current_step['vertex']} has neighbors using colors "
            f"{{{used_by_neighbors}}}, so the smallest free color is R{current_step['color'] + 1}."
        )
        partial_coloring = current_step["partial_coloring"]
        step_positions = nx.spring_layout(graph, seed=11)
        step_palette = plt.get_cmap("tab20")
        step_fills = [
            step_palette(partial_coloring[node] % 20) if node in partial_coloring else "#eeeeee"
            for node in graph.nodes()
        ]
        step_labels = {
            node: f"{node}\nR{partial_coloring[node] + 1}" if node in partial_coloring else node
            for node in graph.nodes()
        }
        step_fig, step_ax = plt.subplots(figsize=(9, 5))
        nx.draw_networkx(
            graph,
            step_positions,
            ax=step_ax,
            node_color=step_fills,
            labels=step_labels,
            node_size=1300,
            font_weight="bold",
        )
        step_ax.set_axis_off()
        st.pyplot(step_fig, use_container_width=True)
        plt.close(step_fig)
        st.caption("What this means: only variables colored up to the selected step receive register colors.")

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

    validity = check_coloring_validity(graph, coloring)
    if validity["valid"]:
        st.success("Coloring validity: PASS. For every edge (u, v): color(u) ≠ color(v).")
    else:
        st.error(f"Coloring validity: FAIL. Bad edges: {validity['bad_edges']}")
    st.caption("What this means: a valid coloring never gives the same color to both endpoints of an edge.")
    if st.button("Test a wrong coloring"):
        if graph.number_of_edges() == 0:
            st.info("This graph has no edges, so no adjacent pair can be assigned the same color.")
        else:
            wrong_coloring = coloring.copy()
            bad_left, bad_right = next(iter(graph.edges()))
            wrong_coloring[bad_right] = wrong_coloring[bad_left]
            wrong_result = check_coloring_validity(graph, wrong_coloring)
            st.error(f"Deliberately incorrect coloring: FAIL. Bad edges: {wrong_result['bad_edges']}")

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
