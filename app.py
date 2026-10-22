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
    page_title="Compiler Register Allocation — Graph Coloring Lab",
    page_icon="🔢",
    layout="wide",
)

st.title("Compiler Register Allocation — Graph Coloring Lab")
st.write(
    "Experiment with simplified three-address code and observe how parsing, "
    "liveness, interference, graph coloring, and register availability change."
)

examples = {
    "Custom": "",
    "Multiplication and Division": """t1 = a * b
t2 = t1 / c
t3 = t2 + d
result = t3 - e""",
    "Modulo and Copy": """x = a % b
y = x
z = y * c
result = z + d""",
    "Mixed Operations": """t1 = a * b
t2 = c / d
t3 = t1 + t2
t4 = t3 % e
result = t4 - f""",
    "Longer Program": """p = a * b
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

example_name = st.selectbox(
    "Try an example",
    list(examples.keys()),
    index=3,
    help="Choose an example, or choose Custom and edit the code yourself.",
)

default_program = examples[example_name]
if example_name == "Custom":
    default_program = """a = b + c
d = a + e
f = d + c
g = f + a"""

program = st.text_area(
    "Three-Address Code",
    value=default_program,
    height=180,
    help="Use a variable or number, optionally with one operator (+, -, *, /, %) and a second value per instruction.",
)

register_count = st.slider(
    "Available registers",
    min_value=1,
    max_value=12,
    value=3,
    help=(
        "Change the number of registers to see allocation succeed or become "
        "insufficient. The interference graph itself depends on the program, "
        "not on this slider."
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

    st.subheader("1. Parsed Instructions")
    rows = [
        {
            "Instruction": x.number,
            "Code": x.text,
            "USE": ", ".join(sorted(x.use)) or "∅",
            "DEF": ", ".join(sorted(x.define)) or "∅",
        }
        for x in instructions
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.subheader("2. Liveness Analysis")
    rows = [
        {
            "Instruction": x.number,
            "Code": x.text,
            "LIVE-IN": ", ".join(sorted(live_in[i])) or "∅",
            "LIVE-OUT": ", ".join(sorted(live_out[i])) or "∅",
        }
        for i, x in enumerate(instructions)
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    st.subheader("3. Interference Graph")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Variables", stats["vertices"])
    c2.metric("Edges", stats["edges"])
    c3.metric("Maximum Degree", stats["max_degree"])
    c4.metric("Connected Components", stats["connected_components"])

    if graph.number_of_edges():
        with st.expander("Inspect interference edges"):
            edge_rows = [
                {"Variable A": left, "Variable B": right}
                for left, right in sorted(graph.edges())
            ]
            st.dataframe(pd.DataFrame(edge_rows), use_container_width=True)

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
                title="Register Allocation",
                loc="upper right",
                fontsize=9,
            )
        ax.set_axis_off()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.subheader("4. Graph Coloring and Register Allocation")
    rows = []
    for variable in sorted(graph.nodes()):
        color = coloring.get(variable)
        rows.append(
            {
                "Variable": variable,
                "Color": color,
                "Register": f"R{color + 1}",
                "Degree": graph.degree(variable),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Greedy Colors Used", used_colors)
    c2.metric("Registers Available", register_count)

    if greedy_fits:
        c3.metric("Spare Registers", register_count - used_colors)
        st.success(
            f"The current greedy assignment fits: it uses {used_colors} color(s) "
            f"and {register_count} register(s) are available."
        )
    else:
        c3.metric("Register Shortage", used_colors - register_count)
        st.warning(
            f"The current greedy assignment does not fit: it uses {used_colors} "
            f"color(s), but only {register_count} register(s) are available."
        )
        st.caption(
            "Greedy coloring does not test every possible coloring. A different "
            "valid coloring may use fewer colors; this version does not search "
            "for that alternative."
        )

    st.info(
        "DM interpretation: variables are vertices, interference is represented "
        "by edges, and registers are colors. Adjacent vertices cannot receive "
        "the same color."
    )

    st.subheader("5. Experiment — Observe the Cause and Effect")
    st.markdown(
        """
Try changing one thing at a time:

- **Registers:** move the slider from 2 → 3 → 4. The program and interference graph stay the same, but allocation may change from insufficient to possible.
- **Remove an instruction:** liveness can change, which can remove variables or edges.
- **Add an instruction or variable:** new USE/DEF information can create new interference relationships.
- **Make a dead variable:** define a variable and never use it later. It may appear as an isolated vertex.
- **Fix an error:** syntax errors are shown below the input so you can edit the program and immediately try again.
        """
    )

except ValueError as exc:
    st.warning("The current input cannot be analyzed yet.")
    st.error(str(exc))
    st.write(
        "Edit the three-address code above, add or remove an instruction, "
        "or choose one of the example programs and try again."
    )
