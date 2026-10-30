"""Page 1: input instructions and the USE/DEF sets."""

import streamlit as st

from frontend import format_set


analysis = st.session_state.analysis
instructions = analysis["instructions"]
graph = analysis["graph"]

st.title("Program")
st.write("Start with a short program. Identify what each instruction reads and writes.")
st.caption(f"{len(instructions)} instructions · {graph.number_of_nodes()} variables · {st.session_state.example_choice}")
source, explanation = st.columns([3, 2], gap="large")
with source:
    st.subheader("Your instructions")
    st.code(st.session_state.program_text, language="text")
with explanation:
    st.subheader("Read the sets")
    st.write("**USE** contains the variables a line reads.")
    st.write("**DEF** contains the variable a line writes.")
    st.code("c = a + b\nUSE = {a, b}\nDEF = {c}", language="text")
    st.caption("Numbers are constants, so they do not appear in USE.")

st.subheader("USE and DEF by instruction")
rows = []
for instruction in instructions:
    rows.append({
        "Line": instruction.number, "Instruction": instruction.text,
        "USE": format_set(instruction.use), "DEF": format_set(instruction.define),
    })
st.dataframe(rows, hide_index=True, width="stretch")
st.info("Next, work backward to find which values must remain available after each line.")
st.page_link("views/liveness.py", label="Continue to liveness", icon=":material/arrow_forward:")
