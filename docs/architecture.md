# Project Architecture

```text
Three-Address Code
        |
        v
     Parser
        |
        +----> USE / DEF
        |
        v
 Liveness Analysis
        |
        +----> LIVE-IN / LIVE-OUT
        |
        v
 Interference Graph
        |
        +----> Graph Statistics
        |
        v
   Graph Coloring
        |
        v
 Register Allocation
        |
        v
 Streamlit Dashboard
```

## Mathematical interpretation

Let `V` be the set of program variables. The interference graph is `G = (V, E)`.

A vertex represents a variable. An edge represents a conflict between variables that cannot share a register in the simplified model. A color represents one register. A valid coloring gives different colors to adjacent vertices.

The project uses NetworkX's greedy `largest_first` strategy. It produces a valid coloring and an upper bound on the minimum number of colors needed; it does not always calculate the exact chromatic number.

## Supported input

Each non-empty line must be an assignment with exactly one `=` sign, for example:

```text
t1 = a * b
t2 = t1 + c
copy = t2
answer = 42
```

The left side must be a variable name. The right side must be a variable or number, optionally followed by one operator (`+`, `-`, `*`, `/`, or `%`) and another variable or number. Each line contains at most one operator because the app expects simplified three-address code. Parentheses, function calls, comparisons, branches, and loops are not supported.

## Current simplification

The application analyzes a straight-line sequence. Variables used before being assigned are treated as inputs to the program. The final result variable is not automatically treated as an observable output or kept live after the last instruction.

The project does not currently implement control-flow graphs, branches, loops, register spilling, assembly generation, or machine-specific register constraints. Those are separate extensions, not requirements of the current model.
