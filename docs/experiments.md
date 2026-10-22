# Demo Experiments

Use these short experiments to demonstrate that the application is an interactive lab. Change one thing at a time and compare the tables, graph, and register status.

## Experiment 1: Change the register budget

1. Select **Mixed Operations**.
2. Observe the interference graph and the number of greedy colors used.
3. Move the available-register slider from 2 to 3 and then 4.

**Observe:** The source program, liveness sets, and interference graph should remain unchanged when only the slider changes. The spare-register or register-shortage status can change.

**Why:** The graph represents conflicts in the program. The register slider represents the number of colors available for the current assignment.

## Experiment 2: Make an isolated vertex

1. Select **Isolated Variable**.
2. Find the variable `unused` in the graph.

The example ends with:

```text
unused = d + c
```

No later instruction uses `unused`, and its definition is the final instruction. In this model, it should appear as an isolated vertex.

3. Add this line at the end:

```text
result = unused + a
```

**Observe:** `unused` now has a later use, so the liveness information and interference graph can change. Compare its degree and the edge list before and after the edit.

## Experiment 3: Change the program

1. Select **Custom**.
2. Remove one instruction or add a new assignment.
3. Watch the USE/DEF table, LIVE-IN/LIVE-OUT table, graph vertices, edges, and graph statistics update.

**Observe:** Program edits can change liveness and therefore the graph. The change depends on which variables are used and defined, not merely on how many lines are present.

## Experiment 4: Try invalid input

Enter an invalid line such as:

```text
value = a + * b
```

**Observe:** The app shows a readable validation message instead of trying to build a graph from malformed input. Correct the expression and continue experimenting.

## What the current model demonstrates

The app handles a straight-line sequence of simple assignments. It does not model branches or loops, eliminate dead instructions, generate machine code, or implement register spilling. Greedy coloring provides a valid coloring, but it does not guarantee the minimum number of colors for every graph.
