"""Page 2: backward liveness analysis and live-range timeline."""

import matplotlib.pyplot as plt
import streamlit as st

from frontend import format_set
from graph_tools import live_ranges


analysis = st.session_state.analysis
instructions = analysis["instructions"]
live_in, live_out = analysis["live_in"], analysis["live_out"]

st.title("Liveness")
st.write("Which values are still needed? Work backward through the program to find out.")
st.subheader("The set equation")
st.code("LIVE-OUT[i] = LIVE-IN[i + 1]\nLIVE-IN[i] = USE[i] union (LIVE-OUT[i] minus DEF[i])", language="text")
st.caption("Remove the old value written by this line, then add the values it reads. The final LIVE-OUT is empty.")
rows = []
for index, instruction in enumerate(instructions):
    rows.append({
        "Line": instruction.number, "Instruction": instruction.text,
        "LIVE-IN": format_set(live_in[index]), "LIVE-OUT": format_set(live_out[index]),
        "Calculation": f"{format_set(instruction.use)} union "
                       f"({format_set(live_out[index])} minus {format_set(instruction.define)}) "
                       f"= {format_set(live_in[index])}",
    })
st.dataframe(rows, hide_index=True, width="stretch")

st.subheader("Live-range timeline")
ranges = live_ranges(instructions, live_in, live_out)
figure, axis = plt.subplots(figsize=(8, max(2.5, len(ranges) * 0.35)))
for row in ranges:
    axis.barh(row["Variable"], row["End"] - row["Start"] + 0.8, left=row["Start"] - 0.4)
axis.set_xlabel("Source line number")
axis.set_xticks([instruction.number for instruction in instructions])
figure.tight_layout()
st.pyplot(figure)
plt.close(figure)
st.caption("Bars summarize each variable's span. Gaps and repeated definitions are merged; liveness sets determine interference.")
st.page_link("views/graph.py", label="Continue to graph analysis", icon=":material/arrow_forward:")
