# Project Architecture

The application preserves the original compiler-analysis pipeline:

~~~text
Three-address code
       |
       v
     Parser ------> USE / DEF
       |
       v
 Liveness analysis -> LIVE-IN / LIVE-OUT and set equations
       |
       v
 Interference graph -> degree, clique, relation and complement views
       |
       v
 Greedy / exact coloring
       |
       +--> validity and CNF explanation
       |
       +--> degree-based spilling and rewritten teaching-model code
       |
       v
 Three-page Streamlit interface
~~~

## Mathematical model

Let V be the set of variables and E the set of interference edges. The graph is G = (V, E). An edge means that two variables must receive different colors. A color represents one register.

The chromatic number is the minimum number of colors in a proper coloring. Greedy algorithms provide quick valid colorings, but they do not always use the minimum number of colors. The exact search is limited to 12 vertices. For general graphs, deciding whether a 3-coloring exists is NP-complete; computing the chromatic number is NP-hard.

A clique of size m is a lower bound of m colors. If the register budget k is smaller than the clique size, the pigeonhole principle proves that allocation without spilling is impossible.

The CNF view generates at-least-one, at-most-one and adjacent-different clauses. It prints constraints but does not call a SAT solver.

## Input rules

Each non-empty line is an assignment with exactly one = sign, such as:

~~~text
t1 = a * b
t2 = t1 + c
copy = t2
answer = 42
~~~

The left side must be a variable name. The right side must be a variable or number, optionally followed by one operator (+, -, *, /, %) and another variable or number. Unsupported symbols and expressions produce line-numbered errors. A variable used before a later definition produces a line-numbered diagnostic. A name that is never assigned is treated as an external input.

## Simplifications

The liveness model analyzes straight-line instruction sequences only. The spill demonstration removes a highest-degree vertex and represents it as MEM[name]; it does not insert real load/store instructions. There are no branches, loops, machine-specific constraints, or assembly emission.
