"""Shared inputs and navigation. Run with: streamlit run app.py"""

from pathlib import Path

import streamlit as st

from allocator import parse_program, analyze_liveness, build_interference_graph, color_graph


EXAMPLES = {
    "Simple register reuse": "easy_2_registers.txt",
    "More variables live together": "external_inputs.txt",
    "Medium: 3 registers": "medium_3_registers.txt",
    "Hard: 4 registers": "hard_4_registers.txt",
    "Spilling demo": "spilling_demo.txt",
    "Disconnected components": "disconnected_components.txt",
}


def load_example():
    filename = EXAMPLES[st.session_state.example_choice]
    st.session_state.program_text = (Path(__file__).parent / "examples" / filename).read_text()


st.set_page_config(page_title="Register Allocation", layout="wide")
st.html("""<style>
    .stMainBlockContainer {max-width: 1100px; padding-top: 2rem;}
    h1 {font-size: 2.25rem;}
    @media (max-width: 768px) {
        .stMainBlockContainer {padding-top: 1.5rem;}
        h1 {font-size: 1.9rem;}
    }
</style>""")

if "example_choice" not in st.session_state:
    st.session_state.example_choice = "Simple register reuse"
if "program_text" not in st.session_state:
    load_example()

with st.sidebar:
    st.header("Register allocation")
    st.caption("A Discrete Mathematics project")
    st.selectbox("Choose an example", list(EXAMPLES), key="example_choice", on_change=load_example)
    st.text_area("Program", key="program_text", height=190)
    st.number_input("Available registers", min_value=1, max_value=12, value=2, key="register_budget")
    st.caption("One assignment per line. Operators: + - * / %.")
    st.caption("Up to 100 assignments, 40 variables, and 32 characters per name.")
    st.caption("Your program and budget stay the same as you move between pages.")

page = st.navigation([
    st.Page("views/program.py", title="1 · Program", icon=":material/code:", default=True),
    st.Page("views/liveness.py", title="2 · Liveness", icon=":material/timeline:", url_path="liveness"),
    st.Page("views/graph.py", title="3 · Graph analysis", icon=":material/hub:", url_path="graph"),
    st.Page("views/allocation.py", title="4 · Register allocation", icon=":material/memory:", url_path="allocation"),
])

try:
    instructions = parse_program(st.session_state.program_text)
    live_in, live_out = analyze_liveness(instructions)
    graph = build_interference_graph(instructions, live_in, live_out)
    steps = []
    coloring = color_graph(graph, steps)
except ValueError as error:
    st.title("Check your program")
    st.error(str(error))
    st.info("Edit the program in the sidebar. Use x = 1, x = a, or x = a + b.")
    st.stop()

# Every page reads the same analysis for the current sidebar inputs.
st.session_state.analysis = {
    "instructions": instructions, "live_in": live_in, "live_out": live_out,
    "graph": graph, "coloring": coloring, "steps": steps,
}
page.run()
st.divider()
st.caption("Assignments only, with no loops or branches. Greedy coloring may use extra registers. This app finds registers; it does not run your program.")
