import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
    # DM concept: the app presents the graph-coloring model without crashing on valid input.
    def test_app_runs_and_reacts_to_edits(self):
        # Resolve app.py from the repository root, not relative to tests/.
        repository_root = Path(__file__).resolve().parents[1]
        app_path = repository_root / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=15).run()
        self.assertEqual(len(app.exception), 0, msg=str(app.exception))

        # Changing the register budget should rerun the page without an error.
        app.slider[0].set_value(2).run()
        self.assertEqual(len(app.exception), 0, msg=str(app.exception))

        # Invalid user input should be shown as feedback, not crash the app.
        app.text_area[0].set_value("value = a + * b").run()
        self.assertEqual(len(app.exception), 0, msg=str(app.exception))
        self.assertGreater(len(app.error), 0)


if __name__ == "__main__":
    unittest.main()
