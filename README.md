# Compiler Register Allocation using Graph Coloring

A beginner-friendly Discrete Mathematics laboratory that demonstrates how compiler variables can be mapped to a limited set of registers using graph coloring.

## Project idea

A simplified three-address program is parsed into USE and DEF sets. Backward liveness analysis finds which values are still needed. The app builds an undirected interference graph: vertices are variables and an edge means that two variables must not share a register in this teaching model. A graph coloring assigns colors (registers) so adjacent vertices have different colors.

## Start quickly

Python 3.10 or newer is recommended.

~~~bash
python -m pip install -r requirements.txt
streamlit run app.py
~~~

Run tests from the repository root:

~~~bash
python -m unittest discover -s tests -v
~~~

## Three-page tour

1. **Program:** choose an example, edit assignments, and inspect USE/DEF.
2. **Liveness & Graph:** read the LIVE-IN/LIVE-OUT set equations, live-range timeline, interference graph, degree information, handshake lemma, adjacency matrix, connected components, relation properties, and complement graph.
3. **Coloring & Results:** compare greedy strategies, check the exact chromatic number for small graphs, step through colors, verify a coloring, see the clique/pigeonhole explanation, inspect CNF clauses, spill variables when the register budget is too small, and compare original with rewritten teaching-model code. The final tab on the results page contains a concise concept reference.

Program controls stay in the sidebar as you move between pages.

## Feature-to-Discrete-Mathematics map

| Feature | DM concept demonstrated |
|---|---|
| USE, DEF, LIVE-IN, LIVE-OUT tables | Sets, union, set difference |
| Liveness equation with actual set values | Set operations |
| Live-range timeline | Live intervals and interference |
| Interference graph | Undirected graphs and graph edges |
| Degree table and degree sequence | Vertex degree |
| Degree sum equals twice the edge count | Handshake lemma |
| Adjacency matrix | Matrix representation of a graph |
| Connected components with different outlines | Connectivity |
| Maximum clique | Clique and lower bound on coloring |
| largest_first, smallest_last, DSATUR comparison | Greedy algorithms |
| Bounded exact search | Chromatic number and backtracking |
| Step-by-step coloring | Proper graph coloring |
| Coloring validity PASS/FAIL | Logical statement checked for every edge |
| Interference relation checker | Relation, reflexivity, irreflexivity, symmetry and transitivity |
| Complement graph | Graph complement |
| Pigeonhole explanation for an undersized register budget | Pigeonhole principle |
| CNF clause display | Propositions, NOT, OR, conjunctive normal form |
| Degree-based spilling | Degree-based heuristic |
| R1, R2, MEM[name] rewritten program | Mapping mathematical colors to a compiler model |
| Theory expanders | Definitions, small examples and project connections |

## Example programs

The dropdown includes examples for a two-color graph, a three-color graph, a four-color graph, spilling at two registers, a verified case where largest_first uses more colors than the exact minimum, and disconnected components. The exact-search example is checked by a unit test so it does not rely on a guessed result.

The app distinguishes the NP-complete decision question (whether a 3-coloring exists for a general graph) from the NP-hard optimization task of computing the chromatic number.

The same programs are available as files under examples/.

## Input format

Each non-empty line should be a simple assignment such as:

~~~text
t1 = a * b
t2 = t1 + c
copy = t2
answer = 42
~~~

Supported expressions are x = a and x = a + b using one of +, -, *, /, %. The parser reports line-numbered syntax errors and checks for a variable used before a later definition. A name that is never assigned is treated as an external program input. Blank lines are ignored.

## Implementation notes and limitations

- Uses Python, Streamlit, NetworkX, Pandas and Matplotlib; no new dependency is needed.
- The UI remains split into three short, focused pages. Advanced tables and demonstrations are inside expanders.
- Exact chromatic-number search is enabled only up to 12 vertices because exhaustive backtracking can be expensive.
- CNF clauses are displayed for learning only; the app does not use a SAT solver.
- Spilling is a teaching model: it repeatedly removes a highest-degree vertex, colors the remaining graph, and rewrites spilled variables as MEM[name]. A real compiler inserts loads/stores and normally chooses spills using estimated cost.
- Liveness is for straight-line code only. Branches, loops, general expressions, machine-specific register constraints and full assembly generation are not implemented.

## Repository commands

~~~bash
python -m compileall -q app.py src tests
python -m unittest discover -s tests -v
streamlit run app.py
~~~
