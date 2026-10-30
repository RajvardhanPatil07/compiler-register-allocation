from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from allocator import parse_program, analyze_liveness, build_interference_graph, color_graph
from graph_tools import check_coloring

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize("example", sorted((ROOT / "examples").glob("*.txt")), ids=lambda path: path.stem)
def test_shipped_examples_produce_valid_assignments(example):
    instructions = parse_program(example.read_text())
    graph = build_interference_graph(instructions, *analyze_liveness(instructions))
    assert check_coloring(graph, color_graph(graph))["valid"]

def test_app_loads_and_reports_invalid_program():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not app.exception
    assert app.title[0].value == "Program"
    app.text_area(key="program_text").set_value("a = a + 1").run()
    assert not app.exception
    assert any("before its definition" in item.value for item in app.error)

@pytest.mark.parametrize("page,title", [("liveness", "Liveness"), ("graph", "Graph analysis"), ("allocation", "Register allocation")])
def test_pages_render_with_shared_analysis(page, title):
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    app.switch_page(f"views/{page}.py").run()
    assert not app.exception
    assert app.title[0].value == title
