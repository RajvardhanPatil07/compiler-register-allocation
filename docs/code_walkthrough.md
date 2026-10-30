# Understand the code and explain it to your teacher

This project answers one question: **which variables can share a register?**
A register is a small storage slot used by the CPU.

The app reads a small program, finds which values are needed at each line,
and uses a graph to choose registers. It does not run the arithmetic.

## Start with four calls

```python
instructions = parse_program(program)
live_in, live_out = analyze_liveness(instructions)
graph = build_interference_graph(instructions, live_in, live_out)
coloring = color_graph(graph)
```

Read these functions in `allocator.py`, in this order. The names describe
what each one does.

## The Python ideas you need

| Code idea | Plain meaning |
| --- | --- |
| Set, such as `{"a", "b"}` | A group with no repeated items |
| List | Items kept in order |
| Dictionary, such as `{"a": 0}` | A name linked to a value |
| `Instruction` record | One line, its number, its USE set, and its DEF set |
| `.union()` | Combine sets |
| `.difference()` | Remove one set's items from another |
| `enumerate()` | Read an item and its position |
| `sorted()` | Put names in order |
| `.copy()` | Make a separate copy so later changes do not change the old result |

## 1. Read the program

`parse_program()` reads one line at a time. It splits at `=`.

For `c = a + b`:

- The left side is the name being written: `c`.
- The right side reads `a` and `b`.
- USE is `{a, b}` and DEF is `{c}`.

`is_variable()` checks names. A name starts with a letter or underscore;
letters, digits, and underscores may follow. `is_value()` checks whether a
piece of text is a name or an unsigned number.

`re.split()` splits an expression around its operator. For `a + b`, it gives
`["a", "+", "b"]`. `parts[::2]` takes the values at positions 0 and 2.

Blank lines are skipped, but source line numbers stay the same. Invalid input
shows an error. A name that is never written in the program is an outside input.
If a name is written, it must get its first value before a line reads it.
For example, `a = a + 1` needs an earlier line such as `a = 1`.

## 2. Find live values

A value is **live** when it will be read later before being replaced.

- LIVE-IN: values needed before a line.
- LIVE-OUT: values needed after a line.

```text
LIVE-OUT[i] = LIVE-IN[i + 1]
LIVE-IN[i] = USE[i] union (LIVE-OUT[i] minus DEF[i])
```

The code works backward. It removes the old value replaced by this line,
then adds the values this line reads. The last LIVE-OUT is empty because
there is no later instruction in this model.

## 3. Build the graph

Each variable is a vertex. A link, called an **edge**, means two variables
need different registers.

The code adds edges between:

- Each pair of values needed before a line.
- A value being written and the other values needed after that line.

`combinations(names, 2)` gives each pair once. The graph has no direction:
if a conflicts with b, b also conflicts with a.

## 4. Choose registers

`color_graph()` visits names in alphabetical order. For each name, it:

1. Looks at colors already used by its neighbors.
2. Starts at color zero.
3. Tries the next color until one is free.
4. Saves the choice.

This is **greedy coloring**. It makes one choice at a time. It gives a valid
coloring for the graphs built by this project, but may use more colors than
needed. Color 0 is shown as R1, color 1 as R2, and so on.

## Work through this example

```text
a = 1
b = a
c = a + b
d = a + c
```

| Line | USE | DEF | LIVE-IN | LIVE-OUT |
| --- | --- | --- | --- | --- |
| 1 | empty | {a} | empty | {a} |
| 2 | {a} | {b} | {a} | {a, b} |
| 3 | {a, b} | {c} | {a, b} | {a, c} |
| 4 | {a, c} | {d} | {a, c} | empty |

For line 3: `{a,b} union ({a,c} minus {c}) = {a,b}`.

The edges are a-b and a-c. The result is a=R1, b=R2, c=R2, d=R1.
The old value of b is no longer needed when c is written, so they can share R2.
The final value of d is not read again, so d has no edges in this model.

“This assignment uses 2 of the 2 registers you allowed” means this particular
assignment fits without moving any variables to memory. For this example,
an edge proves at least two are needed, and our assignment shows two are enough.

## The extra features

The short functions in `graph_tools.py` add these lessons:

| Feature | Plain meaning |
| --- | --- |
| Degree | How many edges meet a vertex |
| Degree sequence | The degrees, largest first |
| Handshake lemma | The degree sum equals twice the edge count |
| Adjacency matrix | A table with 1 for an edge and 0 for no edge |
| Connected component | A group joined by paths |
| Live-range chart | A simple first-to-last span for each variable |
| Coloring check | Every variable has a valid color; linked variables differ |
| Clique | A group in which every pair is linked |
| Strategy comparison | Try different orders for choosing colors |
| Spilling | Move a variable to memory so the rest fit in registers |

A clique of size three needs at least three registers. With only two,
the pigeonhole principle forces a linked pair to share a register.
A small clique does not prove that the whole graph fits.

Spilling copies the graph, removes a variable with the most edges, and colors
again. It repeats until our coloring fits. Names break degree ties in
alphabetical order. This simple rule may spill more than needed.

`rewrite_program()` replaces whole names with `R1`, `R2`, or `MEM[name]`.
It uses a name-to-storage dictionary. It does not insert real loads or stores.

## Where each page lives

`app.py` keeps the shared inputs, runs the four main calls, and opens the
chosen page. `st.session_state` keeps the text and results while the app is open.

| File | What it displays |
| --- | --- |
| `views/program.py` | Input and USE/DEF sets |
| `views/liveness.py` | Live sets, equations, and timeline |
| `views/graph.py` | Graph, degrees, matrix, components, and clique |
| `views/allocation.py` | Registers, steps, comparisons, and spilling |
| `frontend.py` | Shared set formatting and graph drawing |

A `steps` list saves a copy of the colors after each choice. The step control
reads that list. The final step is the same as the full assignment.

## A short explanation for your teacher

“Our project uses sets and graph coloring to assign registers. First, we find
what each line reads and writes. We work backward to find which values are
still needed. We connect variables that need different registers. We then
color the graph, with each color standing for one register. Variables whose
values do not conflict can share a register. We also check the result and
show a simple way to move variables to memory when our coloring does not fit.”

Show the worked example first. Then open Graph analysis for the handshake
lemma and Register allocation for the coloring steps and spilling demo.

## What to say about limits

This is a teaching model for straight-line assignments. It has no loops,
branches, real machine instructions, or exact minimum-color search. One name
is one vertex, even when written more than once. A live-range bar may merge
separate uses. Graph edges use the live sets, not the bars.

The app accepts up to 100 instructions, 40 variables, 32 characters per name,
and 10,000 characters of input. Clique search runs only up to 20 vertices.
These bounds keep the examples small enough to display and explain.

The project was checked with automated tests before sharing. Those checks do
not prove that every possible input is correct.
