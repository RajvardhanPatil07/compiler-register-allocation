"""Page 3: interference graph and the mathematics behind it."""

import streamlit as st

from frontend import format_set, show_graph
from graph_tools import graph_details, adjacency_rows, largest_clique


analysis = st.session_state.analysis
graph, coloring = analysis["graph"], analysis["coloring"]
budget = st.session_state.register_budget
details = graph_details(graph)

st.title("Graph analysis")
st.write("Variables are vertices. An edge connects two variables that need different registers.")
st.caption(f"{graph.number_of_nodes()} vertices · {graph.number_of_edges()} edges · {len(details['components'])} connected components")
show_graph(graph, coloring)
st.caption("Fill colors show the greedy register assignment. Labels identify each variable and its register.")
st.write("Conflicting pairs:", ", ".join(f"{a} - {b}" for a, b in sorted(graph.edges())) or "None")

degrees_tab, matrix_tab, clique_tab = st.tabs(["Degrees & components", "Adjacency matrix", "Clique lower bound"])
with degrees_tab:
    st.subheader("Degree and connectivity")
    st.dataframe(details["degrees"], hide_index=True, width="stretch")
    st.write("Degree sequence:", details["degree_sequence"])
    st.success(f"Handshake lemma: sum of degrees = {details['degree_sum']} = 2 × {graph.number_of_edges()} edges.")
    st.write("A connected component is a group of vertices joined by paths.")
    for number, component in enumerate(details["components"], start=1):
        st.write(f"Component {number}: {format_set(component)}")
with matrix_tab:
    st.subheader("Read the adjacency matrix")
    st.write("1 means there is an edge; 0 means there is no edge. The matrix is symmetric.")
    st.dataframe(adjacency_rows(graph), hide_index=True, width="stretch")
with clique_tab:
    st.subheader("Clique and pigeonhole principle")
    if graph.number_of_nodes() <= 20:
        clique = largest_clique(graph)
        st.write(f"Maximum clique: {format_set(clique)}. Size: {len(clique)}.")
        st.write("In a clique, each variable is linked to all the others. They all need different registers.")
        if len(clique) > budget:
            st.warning("The clique is larger than the budget. By the pigeonhole principle, allocation without spilling is impossible in this model.")
        else:
            st.info("This clique lower bound fits the budget. That alone does not prove the whole graph fits.")
    else:
        st.info("Maximum-clique search is limited to 20 vertices to keep this demonstration small.")
st.page_link("views/allocation.py", label="Continue to register allocation", icon=":material/arrow_forward:")
