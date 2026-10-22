# Compiler Register Allocation using Graph Coloring

A Discrete Mathematics project demonstrating how graph theory can be applied to a simplified compiler register-allocation problem.

## Project idea

Variables in a program are represented as vertices of an interference graph. An edge connects two variables that must not use the same register in this simplified model. Registers are represented by colors, so register allocation becomes a graph-coloring problem.

## Features

- Editable simplified three-address code
- Instruction parsing with USE and DEF sets
- Backward liveness analysis
- Interference graph construction and visualization
- Graph statistics and an edge-inspection table
- Greedy graph coloring with register labels
- Register-count slider and allocation status
- Example programs for experimenting with different inputs
- Basic automated tests

## Discrete Mathematics concepts

- Sets: USE, DEF, LIVE-IN, LIVE-OUT
- Undirected graphs: interference graph
- Vertex degree and connected components
- Graph coloring and register assignment

## Technology

- Python
- Streamlit
- NetworkX
- Pandas
- Matplotlib

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

## How to experiment

1. Select an example program or enter your own code.
2. Observe the USE/DEF and LIVE-IN/LIVE-OUT tables.
3. Inspect the interference graph and its edges.
4. Change the available register count and observe the allocation status.
5. Add or remove an instruction, then compare the resulting graph.

## Important limitations

This is an educational model, not a complete compiler. The current liveness analysis assumes a straight-line sequence, without branches or loops. The parser accepts simplified assignment expressions, not arbitrary C or Python syntax. The application uses NetworkX's greedy `largest_first` coloring strategy. It produces a valid coloring but does not guarantee the minimum possible number of colors. Therefore, the app reports the number of greedy colors used rather than claiming to calculate the exact chromatic number.

The current insufficient-register warning compares the available register count with the colors used by this greedy coloring. It does not implement register spilling or prove that no alternative coloring could fit in fewer registers.
