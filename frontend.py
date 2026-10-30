"""Shared display helpers. The mathematical algorithms stay in allocator.py."""

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st


def format_set(values):
    return "{" + ", ".join(sorted(values)) + "}"


def show_graph(graph, coloring):
    figure, axis = plt.subplots(figsize=(6, 4))
    nodes = sorted(graph.nodes())
    palette = plt.get_cmap("tab20")
    color_count = max(coloring.values(), default=0) + 1
    if color_count > 20:
        palette = plt.get_cmap("hsv", color_count)
    colors = []
    labels = {}
    for variable in nodes:
        if variable in coloring:
            colors.append(palette(coloring[variable]))
            labels[variable] = f"{variable}\nR{coloring[variable] + 1}"
        else:
            colors.append("lightgray")
            labels[variable] = variable
    if nodes:
        nx.draw_networkx(
            graph, pos=nx.circular_layout(graph), nodelist=nodes, labels=labels,
            node_color=colors, node_size=1100, font_size=10, ax=axis,
        )
    else:
        axis.text(0, 0, "No variables to draw.", ha="center", va="center")
    axis.set_xlim(-1.25, 1.25)
    axis.set_ylim(-1.25, 1.25)
    axis.set_axis_off()
    st.pyplot(figure, width=640)
    plt.close(figure)
