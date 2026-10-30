# Working on the allocator

Install Python 3.10 or newer and follow the setup in [README](README.md).
Install test dependencies with `python -m pip install -r requirements-dev.txt`.
Run `python -m pytest -q` before pushing an algorithm or page change.
See [testing](docs/testing.md) for the manual demo check.

Keep parsing, liveness, graph construction, and alphabetical coloring in
`allocator.py`. Put derived graph demonstrations in `graph_tools.py` and
page rendering in `views/`. Share display helpers through `frontend.py`.

Examples contain assignments only. Add new cases to `examples/`; the test
suite discovers every `.txt` file there. Consult the [input format](docs/input-format.md)
when adding an example. Describe teaching-model limitations whenever a change
could suggest exact register minimization or executable machine code.

Keep generated `output/` reports, virtual environments, and local credentials
out of commits. The original repository history remains available for reference.
