import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import networkx as nx
import pandas as pd
import streamlit as st

from src.coloring import color_graph, coloring_count
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
    help=(
        "Set the register budget used to evaluate the greedy coloring result. "
        "Changing this value does not alter the interference graph."
    ),
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
    st.caption("Each instruction is represented by its variables used (USE) and defined (DEF).")
    rows = [
        {
            "Instruction": x.number,
            "Three-Address Code": x.text,
            "USE": ", ".join(sorted(x.use)) or "∅",
            "DEF": ", ".join(sorted(x.define)) or "∅",
        }
        for x in instructions
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("02  |  Liveness Analysis")
    st.caption("LIVE-IN identifies variables live before an instruction; LIVE-OUT identifies variables live after it.")
    rows = [
        {
            "Instruction": x.number,
            "Three-Address Code": x.text,
            "LIVE-IN": ", ".join(sorted(live_in[i])) or "∅",
            "LIVE-OUT": ", ".join(sorted(live_out[i])) or "∅",
        }
        for i, x in enumerate(instructions)
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("03  |  Interference Graph")
    st.caption("Vertices represent variables. An edge connects variables that cannot share a register in this model.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vertices", stats["vertices"])
    c2.metric("Edges", stats["edges"])
    c3.metric("Maximum Vertex Degree", stats["max_degree"])
    c4.metric("Connected Components", stats["connected_components"])

    if graph.number_of_edges():
        with st.expander("View interference edge list"):
            edge_rows = [
                {"Variable 1": left, "Variable 2": right}
                for left, right in sorted(graph.edges())
            ]
            st.dataframe(pd.DataFrame(edge_rows), use_container_width=True, hide_index=True)

    if graph.number_of_nodes():
        positions = nx.kamada_kawai_layout(graph)

        cmap = plt.get_cmap("tab20")
        node_colors = [
            cmap(coloring[node] % 20)
            for node in graph.nodes()
        ]
        labels = {
            node: f"{node}\nR{coloring[node] + 1}"
            for node in graph.nodes()
        }

        fig, ax = plt.subplots(figsize=(12, 8))
        nx.draw_networkx_edges(
            graph,
            positions,
            ax=ax,
            edge_color="gray",
            width=1.4,
        )
        nx.draw_networkx_nodes(
            graph,
            positions,
            ax=ax,
            node_color=node_colors,
            node_size=1500,
            edgecolors="black",
            linewidths=1.0,
        )
        nx.draw_networkx_labels(
            graph,
            positions,
            labels=labels,
            ax=ax,
            font_size=9,
            font_weight="bold",
        )

        legend_handles = [
            Patch(
                facecolor=cmap(i % 20),
                edgecolor="black",
                label=f"R{i + 1} / Color {i}",
            )
            for i in range(used_colors)
        ]
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                title="Assigned Registers",
                loc="upper right",
                fontsize=9,
            )
        ax.set_axis_off()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.subheader("04  |  Register Allocation")
    st.caption("The greedy coloring assigns a register label to each variable in the interference graph.")
    rows = []
    for variable in sorted(graph.nodes()):
        color = coloring.get(variable)
        rows.append(
            {
                "Variable": variable,
                "Color Index": color,
                "Assigned Register": f"R{color + 1}",
                "Vertex Degree": graph.degree(variable),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Colors Used by Greedy Algorithm", used_colors)
    c2.metric("Available Registers", register_count)

    if greedy_fits:
        c3.metric("Unused Registers", register_count - used_colors)
        st.success(
            f"Register budget satisfied by the current greedy coloring: "
            f"{used_colors} color(s) assigned within a budget of {register_count} register(s)."
        )
    else:
        c3.metric("Register Budget Deficit", used_colors - register_count)
        st.warning(
            f"The current greedy coloring uses {used_colors} color(s), exceeding "
            f"the available register budget of {register_count}."
        )
        st.caption(
            "This result reflects the selected greedy strategy, not a proof that no "
            "alternative coloring could fit the available register budget. "
            "Register spilling and alternative-coloring search are not implemented."
        )

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
- **Examine an isolated vertex:** select *Isolated Variable* and inspect the graph for a variable with no interference edges.
- **Compare program structures:** select different examples to compare graph statistics and register assignments.
- **Evaluate input validation:** enter an unsupported expression and review the diagnostic message.
        """
    )

except ValueError as exc:
    st.warning("Analysis could not be completed for the current input.")
    st.error(f"Input validation: {exc}")
    st.caption(
        "Review the instruction format above, correct the reported issue, "
        "or select a predefined example to continue the analysis."
    )
