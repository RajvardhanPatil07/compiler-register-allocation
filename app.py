import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

from src.clique import explain_pigeonhole, maximum_clique
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
from src.parser import parse_program
from src.relation_check import build_complement_graph, check_relation_properties
from src.cnf_view import generate_coloring_cnf
from src.validity import check_coloring_validity


st.set_page_config(
    page_title="Register Allocation Laboratory",
    page_icon="🔢",
    layout="wide",
)

EXAMPLES = {
    "Custom Program": """a = b + c
d = a + e
result = d + c""",
    "Easy: Simple chain": """t1 = a + b
t2 = t1 + c
result = t2 + d""",
    "Mixed arithmetic": """t1 = a * b
t2 = c / d
t3 = t1 + t2
result = t3 - e""",
    "Extended sequence": """p = a * b
q = p + c
r = q / d
s = r % e
t = s + p
result = t * f""",
    "High interference": """t1 = a + b
t2 = c + d
t3 = e + f
t4 = t1 + t2
t5 = t3 + t4
result = t5 + a""",
    "Isolated variable": """a = b + c
d = a * e
unused = d + c""",
}


def load_example() -> None:
    # DM concept: example programs are finite instruction sequences for testing the graph model.
    selected = st.session_state["example_choice"]
    if selected == "Custom Program":
        st.session_state["program_text"] = EXAMPLES["Custom Program"]
    else:
        st.session_state["program_text"] = EXAMPLES[selected]


def draw_graph(graph: nx.Graph, coloring: dict, width: float = 8.5,
               height: float | None = None):
    # DM concept: vertices and edges draw the interference graph; colors show register assignments.
    count = graph.number_of_nodes()
    figure_height = height if height is not None else max(5.5, min(7.5, 4.5 + count * 0.18))
    fig, ax = plt.subplots(figsize=(width, figure_height))
    if count == 0:
        ax.text(0.5, 0.5, "No variables to draw", ha="center", va="center")
        ax.set_axis_off()
        fig.tight_layout(pad=0.5)
        return fig

    density = nx.density(graph)
    if count > 9 or density >= 0.45:
        positions = nx.circular_layout(graph, scale=0.9)
    else:
        positions = nx.kamada_kawai_layout(graph, scale=0.9)

    components = list(nx.connected_components(graph))
    outline_palette = plt.get_cmap("tab10", max(1, len(components)))
    register_palette = plt.get_cmap("tab20")
    component_number = {}
    for number, component in enumerate(components):
        for vertex in component:
            component_number[vertex] = number

    faces, outlines, labels = [], [], {}
    for vertex in graph.nodes():
        if vertex in coloring:
            faces.append(register_palette(coloring[vertex] % 20))
            labels[vertex] = f"{vertex}\nR{coloring[vertex] + 1}"
        else:
            faces.append("#eeeeee")
            labels[vertex] = str(vertex)
        outlines.append(outline_palette(component_number[vertex]))

    node_size = max(620, min(1200, 12000 / count))
    font_size = max(7, min(10, 11 - count * 0.18))
    nx.draw_networkx_edges(
        graph, positions, ax=ax, edge_color="#777777",
        width=1.0 if count > 10 else 1.3, alpha=0.75
    )
    nx.draw_networkx_nodes(
        graph, positions, ax=ax, node_color=faces,
        edgecolors=outlines, node_size=node_size, linewidths=2.2
    )
    nx.draw_networkx_labels(
        graph, positions, labels=labels, ax=ax,
        font_size=font_size, font_weight="bold"
    )
    ax.set_xlim(-1.22, 1.22)
    ax.set_ylim(-1.22, 1.22)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    fig.tight_layout(pad=0.35)
    return fig

st.title("Register Allocation Laboratory")
st.caption("A visual, step-by-step introduction to the Discrete Mathematics behind compiler registers.")
st.markdown(
    "**The idea:** variables are vertices, interference is an edge, and registers are colors. "
    "Connected vertices must receive different colors."
)

if "example_choice" not in st.session_state:
    st.session_state["example_choice"] = "Extended sequence"
if "program_text" not in st.session_state:
    st.session_state["program_text"] = EXAMPLES[st.session_state["example_choice"]]

with st.sidebar:
    st.header("Your program")
    st.caption("These controls stay available while you switch pages.")
    st.selectbox(
        "Choose an example",
        list(EXAMPLES.keys()),
        key="example_choice",
        on_change=load_example,
    )
    program = st.text_area(
        "Edit the instructions",
        key="program_text",
        height=180,
        help="Write one assignment per line: x = a or x = a + b.",
    )
    register_count = st.slider(
        "Available registers",
        min_value=1,
        max_value=12,
        value=3,
        help="The number of register colors that are available to the allocator.",
    )
    st.caption("Allowed operators: +, -, *, /, %. The input is a small teaching language, not full Python or C.")

page = st.radio(
    "Choose a page",
    ["1 · Program", "2 · Liveness & Graph", "3 · Coloring & Results"],
    horizontal=True,
    label_visibility="collapsed",
)

try:
    instructions = parse_program(program)
    live_in, live_out = analyze_liveness(instructions)
    graph = build_interference_graph(instructions, live_in, live_out)
    stats = graph_statistics(graph)
    coloring = color_graph(graph)
    used_colors = coloring_count(coloring)
    clique_vertices, clique_size = maximum_clique(graph)

    if page == "1 · Program":
        st.header("1. Program")
        st.write("Start here: choose an example on the left or edit the code yourself.")
        instruction_rows = []
        for item in instructions:
            instruction_rows.append({
                "Line": item.number,
                "Instruction": item.text,
                "USE (read)": ", ".join(sorted(item.use)) or "∅",
                "DEF (written)": ", ".join(sorted(item.define)) or "∅",
            })
        st.dataframe(pd.DataFrame(instruction_rows), use_container_width=True, hide_index=True)
        st.caption("What this means: USE is the set of variables an instruction reads; DEF is the variable it writes.")

        st.subheader("What the project does")
        steps = st.columns(4)
        steps[0].markdown("**1. Read code**\n\nFind USE and DEF.")
        steps[1].markdown("**2. Track variables**\n\nFind when each value is still needed.")
        steps[2].markdown("**3. Build a graph**\n\nConnect variables that cannot share a register.")
        steps[3].markdown("**4. Assign colors**\n\nEach color represents a register.")
        st.caption("What this means: each stage uses the result of the stage before it.")
        summary = st.columns(3)
        summary[0].metric("Instructions", len(instructions))
        summary[1].metric("Variables", stats["vertices"])
        summary[2].metric("Interference edges", stats["edges"])
        st.info("Tip: edit one line in the sidebar, then open the next page to see how the graph changes.")

    elif page == "2 · Liveness & Graph":
        st.header("2. Liveness & Graph")
        st.write("This page explains why two variables may need different registers.")
        live_rows = []
        for index, item in enumerate(instructions):
            live_rows.append({
                "Line": item.number,
                "Instruction": item.text,
                "USE": "{" + ", ".join(sorted(item.use)) + "}",
                "DEF": "{" + ", ".join(sorted(item.define)) + "}",
                "LIVE-IN": "{" + ", ".join(sorted(live_in[index])) + "}",
                "LIVE-OUT": "{" + ", ".join(sorted(live_out[index])) + "}",
                "Set equation": liveness_equation(
                    item.use, live_out[index], item.define, live_in[index]
                ),
            })
        st.subheader("When is each variable needed?")
        st.dataframe(pd.DataFrame(live_rows), use_container_width=True, hide_index=True)
        st.caption("What this means: union (∪) adds variables from USE; set difference (−) removes variables written by DEF.")

        with st.expander("Show the live-range timeline"):
            ranges = build_live_ranges(instructions, live_in, live_out)
            if ranges:
                range_fig, range_ax = plt.subplots(
                    figsize=(9, min(5.5, max(2.6, len(ranges) * 0.32)))
                )
                for row in ranges:
                    range_ax.barh(
                        row["Variable"], row["End"] - row["Start"] + 0.7,
                        left=row["Start"] - 0.35
                    )
                range_ax.set_xlabel("Instruction number")
                range_ax.set_ylabel("Variable")
                range_ax.set_xlim(0.5, len(instructions) + 0.5)
                range_ax.set_xticks(list(range(1, len(instructions) + 1)))
                range_ax.grid(axis="x", linestyle=":", alpha=0.4)
                range_fig.tight_layout(pad=0.5)
                st.pyplot(range_fig, use_container_width=True)
                plt.close(range_fig)
            st.caption("What this means: overlapping live-range bars indicate variables that may need different registers.")

        st.subheader("The interference graph")
        st.write("Each circle is a variable. An edge means the two variables must use different registers.")
        graph_fig = draw_graph(graph, coloring)
        st.pyplot(graph_fig, use_container_width=True)
        plt.close(graph_fig)
        st.caption("What this means: node fill shows the assigned register; outline color distinguishes connected components.")

        metrics = st.columns(4)
        metrics[0].metric("Variables", stats["vertices"])
        metrics[1].metric("Edges", stats["edges"])
        metrics[2].metric("Max degree", stats["max_degree"])
        metrics[3].metric("Components", stats["connected_components"])

        with st.expander("Advanced graph details"):
            st.markdown("**Degree table**")
            st.dataframe(degree_table(graph), use_container_width=True, hide_index=True)
            st.caption("What this means: a vertex's degree is the number of incident edges.")
            st.write("Degree sequence, highest first:", degree_sequence(graph))
            handshake = check_handshake_lemma(graph)
            st.write(
                f"Handshake lemma: sum of degrees = {handshake['degree_sum']}; "
                f"2 × edges = {handshake['twice_edges']}; "
                f"{'they match' if handshake['holds'] else 'they do not match'}."
            )
            st.caption("What this means: every undirected edge contributes two to the total degree.")
            st.markdown("**Adjacency matrix**")
            st.dataframe(adjacency_matrix(graph), use_container_width=True)
            st.caption("What this means: 1 means an edge exists; 0 means there is no edge.")
            st.markdown("**Connected components**")
            component_rows = [
                {"Component": number + 1, "Variables": ", ".join(sorted(component))}
                for number, component in enumerate(connected_components(graph))
            ]
            st.dataframe(pd.DataFrame(component_rows), use_container_width=True, hide_index=True)
            st.caption("What this means: each component is a group of vertices connected by paths.")

        with st.expander("Relation properties and complement graph"):
            relation = check_relation_properties(graph)
            relation_rows = [
                {"Property": "Reflexive", "Result": "Yes" if relation["reflexive"] else "No"},
                {"Property": "Irreflexive", "Result": "Yes" if relation["irreflexive"] else "No"},
                {"Property": "Symmetric", "Result": "Yes" if relation["symmetric"] else "No"},
                {"Property": "Transitive", "Result": "Yes" if relation["transitive"] else "No"},
            ]
            st.dataframe(pd.DataFrame(relation_rows), use_container_width=True, hide_index=True)
            st.caption("What this means: an interference edge gives a relation between its two endpoints in both directions.")
            if relation["counterexample"] is not None:
                first, middle, last = relation["counterexample"]
                st.write(
                    f"Not transitive: ({first}, {middle}) and ({middle}, {last}) are in R, "
                    f"but ({first}, {last}) is not."
                )
                st.warning("R is not an equivalence relation because it is not transitive.")
            else:
                st.write("The relation is transitive for this input.")
            complement = build_complement_graph(graph)
            complement_fig = draw_graph(complement, {})
            st.pyplot(complement_fig, use_container_width=True)
            plt.close(complement_fig)
            st.caption("What this means: complement edges connect pairs that do not interfere, so they may share a register.")

    else:
        st.header("3. Coloring & Results")
        st.write("A coloring is valid when every edge connects two different colors.")
        exact_count, exact_assignment = exact_coloring(graph)
        top = st.columns(3)
        top[0].metric("Greedy colors used", used_colors)
        top[1].metric("Registers available", register_count)
        top[2].metric("Maximum clique size", clique_size)

        if exact_count is None:
            st.info("The graph is too large for exact search (the limit is 12 vertices).")
        else:
            st.success(f"Greedy used {used_colors} colors; the exact minimum is {exact_count}.")
            if used_colors > exact_count:
                st.warning("Greedy is not always optimal: a different valid coloring uses fewer colors.")
        st.caption("What this means: the chromatic number is the smallest number of colors needed for a proper coloring.")
        st.caption("Finding an exact chromatic number is NP-complete, so practical compilers use heuristics.")

        if clique_size:
            st.info(
                f"Largest clique: {{{', '.join(clique_vertices)}}}. "
                f"A clique of size {clique_size} needs at least {clique_size} registers, "
                f"so {clique_size} is a lower bound."
            )

        pigeonhole = explain_pigeonhole(graph, register_count)
        if pigeonhole["impossible"]:
            st.error(pigeonhole["message"])
        else:
            st.success(pigeonhole["message"])
        st.caption("What this means: if more pairwise-interfering variables exist than registers, two would have to share a register.")

        if used_colors <= register_count:
            st.success("The current greedy coloring fits the available register budget.")
        else:
            st.warning(
                f"The current greedy coloring needs {used_colors - register_count} "
                "more register(s) than are available."
            )

        strategy_results = compare_coloring_strategies(graph)
        strategy_rows = [
            {key: value for key, value in result.items() if key != "Coloring"}
            for result in strategy_results
        ]
        st.subheader("Compare coloring strategies")
        st.dataframe(pd.DataFrame(strategy_rows), use_container_width=True, hide_index=True)
        st.caption("What this means: each greedy strategy visits vertices in a different order.")

        validity = check_coloring_validity(graph, coloring)
        if validity["valid"]:
            st.success("Coloring check: PASS. For every edge (u, v): color(u) ≠ color(v).")
        else:
            st.error(f"Coloring check: FAIL. Bad edges: {validity['bad_edges']}")
        st.caption("What this means: adjacent vertices must never receive the same color.")
        if st.button("Demonstrate a wrong coloring"):
            if graph.number_of_edges() == 0:
                st.info("There are no edges, so no adjacent pair can be given the same color.")
            else:
                wrong_coloring = coloring.copy()
                left, right = next(iter(graph.edges()))
                wrong_coloring[right] = wrong_coloring[left]
                wrong_result = check_coloring_validity(graph, wrong_coloring)
                st.error(f"Expected result: FAIL. Conflicting edges: {wrong_result['bad_edges']}")

        with st.expander("CNF encoding of k-coloring"):
            cnf = generate_coloring_cnf(graph, register_count)
            st.write("The proposition x(v, c) means variable v receives register/color c.")
            st.dataframe(pd.DataFrame(cnf["counts"]), use_container_width=True, hide_index=True)
            st.caption("What this means: the count table reports how many constraints are created in each group.")
            st.dataframe(pd.DataFrame(cnf["clauses"]), use_container_width=True, hide_index=True)
            if cnf["truncated"]:
                st.info(f"Showing the first {cnf['display_limit']} of {cnf['total_clauses']} clauses.")
            st.caption("Propositions represent choices, OR means at least one option holds, NOT forbids a choice, and CNF is an AND of OR-clauses.")
            st.caption("What this means: the clauses encode coloring rules; no SAT solver is used.")

        with st.expander("Explore coloring one vertex at a time"):
            steps = coloring_steps(graph)
            if steps:
                step_number = st.slider(
                    "Coloring step", min_value=1, max_value=len(steps), value=1,
                    key="coloring_step"
                )
                step = steps[step_number - 1]
                neighbors = ", ".join(f"R{color + 1}" for color in step["neighbor_colors"])
                st.write(
                    f"Vertex {step['vertex']} has neighbors using colors "
                    f"{{{neighbors}}}, so the smallest free color is R{step['color'] + 1}."
                )
                step_fig = draw_graph(graph, step["partial_coloring"], width=7.5, height=4.4)
                st.pyplot(step_fig, use_container_width=True)
                plt.close(step_fig)
                st.caption("What this means: gray vertices are not colored yet.")
            else:
                st.write("There are no vertices to color.")

        with st.expander("Show variable-to-register assignments"):
            allocation_rows = [
                {
                    "Variable": variable,
                    "Degree": graph.degree(variable),
                    "Color": coloring[variable],
                    "Register": f"R{coloring[variable] + 1}",
                }
                for variable in sorted(graph.nodes())
            ]
            st.dataframe(pd.DataFrame(allocation_rows), use_container_width=True, hide_index=True)
            st.caption("What this means: the register is the hardware resource represented by the assigned color.")

except ValueError as error:
    st.header("Input needs a small fix")
    st.error(str(error))
    st.caption("Check the line mentioned above. Each non-empty line should look like x = a or x = a + b.")
