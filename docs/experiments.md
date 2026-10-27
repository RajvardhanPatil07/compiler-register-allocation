# Demo Experiments

Use one example at a time and change only one control so the graph changes are easier to explain.

## 1. Two-color graph

1. Choose **Easy: 2 registers**.
2. Open **Coloring & Results**.
3. Observe the exact minimum and the assigned registers.

**DM concept:** chromatic number and proper graph coloring.

## 2. Clique and pigeonhole principle

1. Choose **Spilling demo: try 2 registers**. The register slider moves to two.
2. Open **Coloring & Results**.
3. Read the clique lower bound and the pigeonhole explanation.
4. Expand **Allocation with spilling and rewritten code**.

**DM concept:** a clique of size three cannot fit into two colors; spilling removes a vertex from the graph until the remaining graph fits.

## 3. Greedy is not always optimal

1. Choose **Greedy vs exact minimum**.
2. Compare the largest_first strategy result with the exact minimum.

**Observe:** this example is unit-tested to make sure largest-first uses six colors while the exact chromatic number is five.

**DM concept:** greedy heuristics versus exact search/backtracking.

## 4. Disconnected components and complement graph

1. Choose **Disconnected components**.
2. Inspect the different component outlines.
3. Expand **Advanced graph details** and **Relation properties and complement graph**.

**DM concept:** connected components, relation properties and graph complement.

## 5. Understand one liveness equation

1. Choose **Medium: 3 registers**.
2. Open **Liveness & Graph**.
3. Pick one instruction and read the equation LIVE-IN = USE ∪ (LIVE-OUT − DEF).

**Observe:** blank lines do not shift the source line numbers shown on the live-range chart.

**DM concept:** set union and set difference.

## 6. Deliberately invalid coloring

1. Choose any program with interference edges.
2. Open **Coloring & Results**.
3. Use **Demonstrate a wrong coloring**.

**Observe:** the validity checker reports the edge whose endpoints share a color.

**DM concept:** a universal condition over every edge: color(u) ≠ color(v).
