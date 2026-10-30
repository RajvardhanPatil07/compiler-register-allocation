# Register allocation using graph coloring

A Discrete Mathematics project that shows which variables can share a register.
It uses sets, liveness analysis, and graph coloring, with four pages for the demo.

## Start the app

Use Python 3.10 or newer. From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Read the code

1. `allocator.py`: the four main steps: read the code, find live values, build
   the graph, and choose colors.
2. `graph_tools.py`: graph details, color checks, cliques, and spilling.
3. `app.py`: shared inputs and page navigation.
4. `views/`: one short file per page. `frontend.py` holds shared display helpers.

Start with [the code and teacher guide](docs/code_walkthrough.md).

## The four pages

| Page | What it shows |
| --- | --- |
| Program | The input and USE/DEF sets |
| Liveness | Live sets, set equations, and a live-range chart |
| Graph analysis | The graph, degrees, handshake lemma, matrix, components, and clique |
| Register allocation | Registers, color checks, saved steps, method comparison, spilling, and rewritten code |

The sidebar keeps your program and register count when you change pages.
This version keeps 15 of the original README's 20 feature groups. Component
lists replace colored component outlines. Exact search, CNF, relation checks,
and the complement graph remain outside this simpler version.

## Input rules

```text
a = 1
b = a
c = a + b
d = a + c
```

Use one assignment per line. The right side can be a name, an unsigned number,
or two values joined by one operator: `+`, `-`, `*`, `/`, `%`.
Spaces around operators are optional. Blank lines are ignored.

Names never assigned anywhere are outside inputs. A name that is assigned
must get its first value before it is read. For example, `a=a+1` needs an
earlier line such as `a=1`.

The bounds are 100 assignments, 40 variables, 32 characters per name, and
10,000 characters of text. The app explains input errors in the page.

## What to explain to your teacher

- A vertex is a variable. An edge means two values need different registers.
- Variables can share a register if their values do not conflict.
- Greedy coloring is a quick method; it may use more registers than needed.
- A clique gives a lower bound. The app finds it only for graphs with up to 20 vertices.
- Spilling moves variables to memory until our coloring fits. It may move more
  variables than needed. `MEM[name]` is a memory marker, not real machine code.
- The model handles assignments only, with no loops or branches. It does not
  run arithmetic. Each name is one vertex, even when assigned again.
- The last LIVE-OUT is empty. Live-range bars merge gaps; the live sets decide edges.

## Development

Install test dependencies and run the checks:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

See [testing](docs/testing.md), [input format](docs/input-format.md), and
[contributing](CONTRIBUTING.md) for more detail.
