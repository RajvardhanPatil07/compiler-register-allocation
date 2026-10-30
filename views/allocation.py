"""Page 4: register assignments, coloring demonstrations, and spilling."""

import streamlit as st

from frontend import show_graph
from graph_tools import check_coloring, compare_strategies, allocate_with_spilling, rewrite_program


analysis = st.session_state.analysis
instructions, graph = analysis["instructions"], analysis["graph"]
coloring, steps = analysis["coloring"], analysis["steps"]
register_budget = st.session_state.register_budget
registers_used = len(set(coloring.values()))

st.title("Register allocation")
st.write("Visit names alphabetically. Choose the first color not used by already-colored neighbors.")
st.subheader("Your register assignment")
rows = []
for variable in sorted(coloring):
    rows.append({"Variable": variable, "Register": f"R{coloring[variable] + 1}"})
st.dataframe(rows, hide_index=True, width="stretch")
st.write(f"Registers used by greedy coloring: {registers_used}")
if registers_used <= register_budget:
    st.success(f"This assignment uses {registers_used} of the {register_budget} registers you allowed.")
else:
    st.warning(f"This assignment exceeds the budget: it uses {registers_used} registers, but you allowed {register_budget}. Another coloring may use fewer.")
st.caption("A register is a small storage slot used by the CPU. Variables can share one when their values are needed at different times.")
validity = check_coloring(graph, coloring)
if validity["valid"]:
    st.success("Coloring check: PASS. Every variable has a register. Linked variables use different registers.")
else:
    st.error(f"Coloring check: FAIL. Missing: {validity['missing']}; invalid colors: {validity['invalid']}; conflicts: {validity['conflicts']}.")

steps_tab, compare_tab, spill_tab = st.tabs(["Step through", "Compare strategies", "Spilling & code"])
with steps_tab:
    st.subheader("Color one vertex at a time")
    step_number = st.number_input("Coloring step", min_value=1, max_value=len(steps), value=1, key="coloring_step")
    step = steps[step_number - 1]
    neighbor_registers = [f"R{color + 1}" for color in step["neighbor_colors"]]
    st.write(f"Vertex {step['variable']}: colored neighbors use {neighbor_registers}; choose R{step['color'] + 1}.")
    show_graph(graph, step["coloring"])
    st.caption("Gray vertices have not been colored yet.")
    if st.button("Demonstrate a wrong coloring"):
        if graph.number_of_edges():
            first, second = next(iter(graph.edges()))
            wrong = coloring.copy()
            wrong[second] = wrong[first]
            st.error(f"Expected FAIL. Conflicting edges: {check_coloring(graph, wrong)['conflicts']}")
        else:
            st.info("This graph has no edges, so sharing a color creates no edge conflict.")
with compare_tab:
    st.subheader("Compare greedy strategies")
    st.dataframe(compare_strategies(graph), hide_index=True, width="stretch")
    st.caption("Our alphabetical method uses simple loops. NetworkX provides the other three methods.")
    st.write("largest_first starts with variables that have many links. smallest_last removes variables with few links, then visits them in reverse order.")
    st.write("DSATUR picks a variable next to the most different colors.")
    st.info("These are quick methods. They do not always find the fewest registers.")
with spill_tab:
    st.subheader("Fit the register budget")
    allocation = allocate_with_spilling(graph, register_budget)
    st.write("Spilled variables:", ", ".join(allocation["spilled"]) or "None")
    st.write("Registers after spilling:", len(set(allocation["coloring"].values())))
    st.caption("Move a variable with the most links to memory, then color again. Repeat until it fits. This simple rule may move more variables than needed.")
    show_graph(allocation["graph"], allocation["coloring"])
    rows = []
    for variable in sorted(graph.nodes()):
        if variable in allocation["spilled"]:
            location = f"MEM[{variable}]"
        else:
            register_number = allocation["coloring"][variable] + 1
            location = f"R{register_number}"
        rows.append({"Variable": variable, "Storage": location})
    st.dataframe(rows, hide_index=True, width="stretch")
    original, rewritten = st.columns(2)
    with original:
        st.write("Original code")
        st.code(st.session_state.program_text, language="text")
    with rewritten:
        st.write("Code with register names")
        st.code("\n".join(rewrite_program(instructions, allocation["coloring"], allocation["spilled"])), language="text")
    st.caption("MEM[name] represents memory. Real load/store instructions are not generated.")
st.page_link("views/program.py", label="Return to your program", icon=":material/arrow_back:")
