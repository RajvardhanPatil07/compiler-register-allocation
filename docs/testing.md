# Run the checks

Use the same virtual environment as the app:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests cover assignment syntax and bounds, live values, conflict edges,
coloring, graph summaries, clique bounds, spilling, and storage rewriting.
They also render each Streamlit page and parse every text file in `examples/`.
Add a regression test when changing an algorithm or fixing an input error.

For a manual check, run `streamlit run app.py`, choose Spilling demo, and set
Available registers to 1. Open Register allocation and check that spilling
fits the budget. Change examples and visit all four pages to verify that
inputs stay consistent. This checks interactions beyond the automated page tests.
