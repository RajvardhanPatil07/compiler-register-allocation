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
from src.spilling import allocate_with_spilling, rewrite_program_with_registers


st.set_page_config(
    page_title="Register Allocation Laboratory",
    page_icon="🔢",
    layout="wide",
)

EXAMPLES = {
    "Custom Program": """a = b + c
d = a + e
result = d + c""",
    "Easy: 2 registers": """a = 1
b = a
c = a + b
d = a + c""",
    "Medium: 3 registers": """a = 1
b = a
c = a + b
d = b
e = b
d = e
a = c + d
b = a
e = c""",
    "Hard: 4 registers": """a = 1
b = a
c = a + b
d = b + c
e = c + d
f = a + e
g = f + b
h = a + g
g = c""",
    "Spilling demo: try 2 registers": """a = 1
b = 1
c = 1
t1 = a + b
t2 = t1 + c
result = t2 + a""",
    "Greedy vs exact minimum": """a = 1
b = 1
c = a + b
d = b + a
e = d + c
f = b + a
g = e + d
h = f + a
i = a + c
b = d + g
b = c + d
a = i""",
    "Disconnected components": """a = 1
b = 1
left = a + b
x = 2
y = 3
right = x + y
unused = 7""",
}

EXAMPLE_DESCRIPTIONS = {
    "Custom Program": "Write your own short assignment sequence.",
    "Easy: 2 registers": "Small graph with an exact minimum of 2 colors.",
    "Medium: 3 registers": "A slightly richer graph that needs 3 colors.",
    "Hard: 4 registers": "A denser graph with an exact minimum of 4 colors.",
    "Spilling demo: try 2 registers": "Needs 3 colors; the example automatically sets the budget to 2.",
    "Greedy vs exact minimum": "A checked example where largest_first uses 6 colors but exact search finds 5.",
    "Disconnected components": "Several independent graph components plus isolated variables.",
}

THEORY_CONCEPTS = [
    ("Set", "A set is a collection of distinct elements.", "{a, b, c}", "Program page: USE, DEF, LIVE-IN and LIVE-OUT."),
    ("Union", "Union combines the elements that appear in either set.", "{a, b} ∪ {b, c} = {a, b, c}", "Liveness equation: USE ∪ (LIVE-OUT − DEF)."),
    ("Difference", "Set difference keeps elements from the first set that are not in the second.", "{a, b, c} − {b} = {a, c}", "Liveness equation: remove variables defined by the instruction."),
    ("Relation", "A relation is a set of ordered pairs between elements.", "R = {(a, b), (b, a)}", "The interference graph is shown as an ordered-pair relation."),
    ("Reflexive", "A relation is reflexive when every element relates to itself.", "(a, a) must be in R for every a", "The interference relation is not reflexive because there are no self-edges."),
    ("Symmetric", "A relation is symmetric when aRb implies bRa.", "If (a, b) is in R, then (b, a) is in R", "Undirected interference edges create pairs in both directions."),
    ("Transitive", "A relation is transitive when aRb and bRc imply aRc.", "On a path a—b—c, (a, c) is missing", "The relation checker finds a counter-example when one exists."),
    ("Equivalence relation", "An equivalence relation is reflexive, symmetric and transitive.", "Equality is an equivalence relation", "Interference is not an equivalence relation when it fails reflexivity or transitivity."),
    ("Undirected graph", "An undirected graph has vertices joined by edges without direction.", "Vertices {a, b}; edge {a, b}", "The interference graph models variables and conflicts."),
    ("Degree", "A vertex degree is the number of edges connected to that vertex.", "If a connects to b and c, degree(a) = 2", "Degree table and the spilling heuristic."),
    ("Handshake lemma", "The sum of all vertex degrees equals twice the number of edges.", "Degrees 1, 2, 1 sum to 4 = 2 × 2 edges", "Advanced graph details validate this identity."),
    ("Connected component", "A connected component is a maximal group joined by paths.", "Component {a, b}, separate component {c, d}", "Different graph outlines identify connected components."),
    ("Clique", "A clique is a set of vertices that are all pairwise adjacent.", "A triangle is a clique of size 3", "The clique size gives a lower bound on the required registers."),
    ("Graph coloring", "A proper coloring assigns different colors to adjacent vertices.", "For edge a—b, use R1 and R2", "Coloring and register assignment page."),
    ("Chromatic number", "The chromatic number is the fewest colors needed for a proper coloring.", "A triangle has chromatic number 3", "The bounded exact-coloring search reports the minimum for small graphs."),
    ("Greedy algorithm", "A greedy algorithm makes the next local choice without searching every full solution.", "Color the highest-degree uncolored vertex first", "Compare largest_first, smallest_last and DSATUR."),
    ("Complement graph", "The complement connects distinct vertices that were not connected in the original graph.", "If a—b is absent, it appears in the complement", "Complement graph: these pairs do not interfere."),
    ("Proposition", "A proposition is a statement that can be true or false.", "x(a, 1): a receives color 1", "The CNF view represents color choices with propositions."),
    ("CNF", "Conjunctive normal form is an AND of clauses, where each clause is an OR of literals.", "(x(a,1) OR x(a,2)) AND (NOT x(a,1) OR NOT x(a,2))", "The app lists the clauses for k-coloring; it does not run a SAT solver."),
    ("Pigeonhole principle", "If more objects than boxes must be assigned, at least one box receives two objects.", "3 pairwise-interfering variables cannot fit in 2 registers", "The clique/register-budget message explains why spilling is required."),
    ("NP-completeness", "For each fixed k ≥ 3, deciding whether a general graph has a k-coloring is NP-complete; computing the chromatic number is NP-hard.", "Exact search can become expensive as a graph grows", "The app limits exact coloring to 12 vertices and compares fast heuristics."),
    ("Backtracking", "Backtracking tries a choice and undoes it when that choice cannot lead to a solution.", "Try R1; if a neighbor conflicts, undo and try R2", "The exact chromatic-number search tries colors one at a time."),
]



def load_example() -> None:
    # DM concept: each example is a finite instruction sequence with a known graph property.
    selected = st.session_state["example_choice"]
    st.session_state["program_text"] = EXAMPLES[selected]
    if selected == "Spilling demo: try 2 registers":
        st.session_state["register_count"] = 2


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
    st.session_state["example_choice"] = "Easy: 2 registers"
if "program_text" not in st.session_state:
    st.session_state["program_text"] = EXAMPLES[st.session_state["example_choice"]]
if "register_count" not in st.session_state:
    st.session_state["register_count"] = 3

with st.sidebar:
    st.header("Your program")
    st.caption("These controls stay available while you switch pages.")
    st.selectbox(
        "Choose an example",
        list(EXAMPLES.keys()),
        key="example_choice",
        on_change=load_example,
    )
    st.caption(EXAMPLE_DESCRIPTIONS[st.session_state["example_choice"]])
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
        key="register_count",
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
        st.dataframe(pd.DataFrame(instruction_rows), width="stretch", hide_index=True)
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
        st.dataframe(pd.DataFrame(live_rows), width="stretch", hide_index=True)
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
                line_numbers = [item.number for item in instructions]
                range_ax.set_xlim(min(line_numbers) - 0.5, max(line_numbers) + 0.5)
                range_ax.set_xticks(line_numbers)
                range_ax.grid(axis="x", linestyle=":", alpha=0.4)
                range_fig.tight_layout(pad=0.5)
                st.pyplot(range_fig, width="stretch")
                plt.close(range_fig)
            st.caption("What this means: overlapping live intervals are a visual clue; actual interference edges are determined by the liveness sets.")

        st.subheader("The interference graph")
        st.write("Each circle is a variable. An edge means the two variables must use different registers.")
        graph_fig = draw_graph(graph, coloring)
        st.pyplot(graph_fig, width="stretch")
        plt.close(graph_fig)
        st.caption("What this means: node fill shows the assigned register; outline color distinguishes connected components.")

        metrics = st.columns(4)
        metrics[0].metric("Variables", stats["vertices"])
        metrics[1].metric("Edges", stats["edges"])
        metrics[2].metric("Max degree", stats["max_degree"])
        metrics[3].metric("Components", stats["connected_components"])

        with st.expander("Advanced graph details"):
            st.markdown("**Degree table**")
            st.dataframe(degree_table(graph), width="stretch", hide_index=True)
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
            st.dataframe(adjacency_matrix(graph), width="stretch")
            st.caption("What this means: 1 means an edge exists; 0 means there is no edge.")
            st.markdown("**Connected components**")
            component_rows = [
                {"Component": number + 1, "Variables": ", ".join(sorted(component))}
                for number, component in enumerate(connected_components(graph))
            ]
            st.dataframe(pd.DataFrame(component_rows), width="stretch", hide_index=True)
            st.caption("What this means: each component is a group of vertices connected by paths.")

        with st.expander("Relation properties and complement graph"):
            relation = check_relation_properties(graph)
            relation_rows = [
                {"Property": "Reflexive", "Result": "Yes" if relation["reflexive"] else "No"},
                {"Property": "Irreflexive", "Result": "Yes" if relation["irreflexive"] else "No"},
                {"Property": "Symmetric", "Result": "Yes" if relation["symmetric"] else "No"},
                {"Property": "Transitive", "Result": "Yes" if relation["transitive"] else "No"},
            ]
            st.dataframe(pd.DataFrame(relation_rows), width="stretch", hide_index=True)
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
            st.pyplot(complement_fig, width="stretch")
            plt.close(complement_fig)
            st.caption("What this means: complement edges connect pairs that do not interfere, so they may share a register.")


    else:
        st.header("3. Coloring & Results")
        st.write("Explore the coloring result, allocation model, mathematical constraints, or concept reference.")
        coloring_tab, allocation_tab, logic_tab, reference_tab = st.tabs(
            ["Coloring", "Allocation", "Proofs & logic", "Concept reference"]
        )
        exact_count, exact_assignment = exact_coloring(graph)
        strategy_results = compare_coloring_strategies(graph)
        validity = check_coloring_validity(graph, coloring)

        with coloring_tab:
            summary = st.columns(3)
            summary[0].metric("Greedy colors used", used_colors)
            summary[1].metric("Registers available", register_count)
            summary[2].metric("Exact minimum", "Too large" if exact_count is None else exact_count)
            if exact_count is None:
                st.info("Exact coloring is limited to graphs with at most 12 vertices.")
            else:
                st.write(f"Greedy used {used_colors} colors; the exact minimum is {exact_count}.")
                if used_colors > exact_count:
                    st.warning("Greedy is not always optimal: another valid coloring uses fewer colors.")
            if used_colors > register_count:
                st.warning(
                    f"The selected greedy strategy uses {used_colors} colors, more than the "
                    f"{register_count} available registers. This alone does not prove every "
                    "coloring needs that many registers."
                )
            else:
                st.success("The selected greedy coloring fits the available register budget.")
            st.caption(
                "For general graphs, deciding whether a 3-coloring exists is NP-complete; "
                "computing the chromatic number is NP-hard. Practical compilers use fast heuristics."
            )

            st.subheader("Compare coloring strategies")
            strategy_rows = [
                {key: value for key, value in item.items() if key != "Coloring"}
                for item in strategy_results
            ]
            st.dataframe(pd.DataFrame(strategy_rows), width="stretch", hide_index=True)
            st.caption("What this means: each greedy strategy visits vertices in a different order.")

            if validity["valid"]:
                st.success("Coloring check: PASS. Every vertex is colored and every edge has different endpoint colors.")
            else:
                st.error("Coloring check: FAIL.")
                if validity["bad_edges"]:
                    st.write("Conflicting or incompletely colored edges:", validity["bad_edges"])
                if validity["missing_vertices"]:
                    st.write("Uncolored vertices:", validity["missing_vertices"])
            st.caption("What this means: a proper coloring assigns every vertex a color and keeps adjacent vertices different.")

            if st.button("Demonstrate a wrong coloring"):
                if graph.number_of_edges() == 0:
                    st.info("There are no edges, so no adjacent pair can be given the same color.")
                else:
                    wrong_coloring = coloring.copy()
                    left, right = next(iter(graph.edges()))
                    wrong_coloring[right] = wrong_coloring[left]
                    wrong_result = check_coloring_validity(graph, wrong_coloring)
                    st.error(f"Expected result: FAIL. Conflicting edges: {wrong_result['bad_edges']}")

            with st.expander("Color one vertex at a time"):
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
                    step_fig = draw_graph(
                        graph, step["partial_coloring"], width=7.5, height=4.4
                    )
                    st.pyplot(step_fig, width="stretch")
                    plt.close(step_fig)
                    st.caption("What this means: gray vertices have not been colored yet.")
                else:
                    st.write("There are no vertices to color.")

        with allocation_tab:
            st.subheader("Allocation with spilling")
            spill_result = allocate_with_spilling(graph, register_count)
            spilled = spill_result["spilled"]
            spill_coloring = spill_result["coloring"]
            if spilled:
                order_text = ", ".join(
                    f"{index + 1}. {name}" for index, name in enumerate(spilled)
                )
                st.warning(f"Spilled to memory in this order: {order_text}")
            else:
                st.success("No spilling was needed for this register budget.")
            st.metric("Registers used after spilling", spill_result["registers_used"])
            st.caption(
                "A spilled variable lives in memory instead of a register. This teaching model "
                "chooses the highest-degree variable; real compilers estimate spill cost."
            )
            post_spill_fig = draw_graph(
                spill_result["graph"], spill_coloring, width=7.5, height=4.4
            )
            st.pyplot(post_spill_fig, width="stretch")
            plt.close(post_spill_fig)
            st.caption("What this means: spilled vertices are removed from the reduced graph; the rest are colored.")

            st.subheader("Original code vs. register model")
            rewritten_lines = rewrite_program_with_registers(instructions, spill_coloring, spilled)
            source_column, rewritten_column = st.columns(2)
            with source_column:
                st.markdown("**Original code**")
                st.code(program, language="text")
            with rewritten_column:
                st.markdown("**Teaching-model rewrite**")
                st.code("\n".join(rewritten_lines), language="text")
            st.caption("What this means: R1, R2, ... represent registers; MEM[name] marks a spilled variable.")

            st.subheader("Final storage assignment")
            storage_rows = []
            for variable in sorted(graph.nodes()):
                if variable in spilled:
                    location = f"MEM[{variable}]"
                else:
                    location = f"R{spill_coloring[variable] + 1}"
                storage_rows.append({
                    "Variable": variable,
                    "Degree": graph.degree(variable),
                    "Storage location": location,
                })
            st.dataframe(pd.DataFrame(storage_rows), width="stretch", hide_index=True)
            st.caption("What this means: each variable is assigned either a register or a teaching-model memory location.")

        with logic_tab:
            st.subheader("Clique lower bound")
            clique_vertices, clique_size = maximum_clique(graph)
            st.write(f"Largest clique: {{{', '.join(clique_vertices)}}} (size {clique_size}).")
            st.caption(
                f"A clique of size {clique_size} needs at least {clique_size} registers, "
                f"so {clique_size} is a lower bound."
            )
            pigeonhole = explain_pigeonhole(graph, register_count)
            if pigeonhole["impossible"]:
                st.error(pigeonhole["message"])
            else:
                st.info(pigeonhole["message"])
            st.caption("What this means: a clique larger than the available register set proves that spilling is necessary for this model.")

            st.subheader("CNF encoding of k-coloring")
            cnf = generate_coloring_cnf(graph, register_count)
            st.write("The proposition x(v, c) means variable v receives register/color c.")
            st.dataframe(pd.DataFrame(cnf["counts"]), width="stretch", hide_index=True)
            st.caption("What this means: the count table shows how many clauses each rule creates.")
            st.dataframe(pd.DataFrame(cnf["clauses"]), width="stretch", hide_index=True)
            if cnf["truncated"]:
                st.info(f"Showing the first {cnf['display_limit']} of {cnf['total_clauses']} clauses.")
            st.caption(
                "Propositions represent choices; OR combines alternatives; NOT forbids a choice; "
                "CNF is an AND of OR-clauses. No SAT solver is used."
            )
            st.caption("What this means: the clauses encode the rules for proper graph coloring.")

        with reference_tab:
            st.subheader("Discrete Mathematics reference")
            st.caption("Each topic has a short definition, a small example, and its connection to this application.")
            concept_details = {item[0]: item[1:] for item in THEORY_CONCEPTS}
            sections = [
                ("Sets and relations", [
                    "Set", "Union", "Difference", "Relation", "Reflexive",
                    "Symmetric", "Transitive", "Equivalence relation"
                ]),
                ("Graph theory", [
                    "Undirected graph", "Degree", "Handshake lemma",
                    "Connected component", "Clique", "Complement graph"
                ]),
                ("Coloring and logic", [
                    "Graph coloring", "Chromatic number", "Greedy algorithm",
                    "Proposition", "CNF", "Pigeonhole principle",
                    "NP-completeness", "Backtracking"
                ]),
            ]
            for section_title, concept_names in sections:
                st.markdown(f"#### {section_title}")
                for concept in concept_names:
                    definition, example, location = concept_details[concept]
                    with st.expander(concept):
                        st.write(f"**Definition:** {definition}")
                        st.code(example, language="text")
                        st.write(f"**Where it appears in this application:** {location}")

except ValueError as error:
    st.header("Input needs a small fix")
    st.error(str(error))
    st.caption("Check the line mentioned above. Each non-empty line should look like x = a or x = a + b.")
