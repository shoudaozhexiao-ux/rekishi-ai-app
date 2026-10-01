import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from history_ai import ServiceError


class FakeStreamlit(types.ModuleType):
    def __init__(self):
        super().__init__('streamlit')
        self.sidebar = self
        self.secrets = {'OPENAI_API_KEY': 'test-key'}
        self.session_state = {}
        self.year = 2026
        self.refresh = False
        self.displayed = []
        self.errors = types.SimpleNamespace(StreamlitSecretNotFoundError=FileNotFoundError)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __getattr__(self, name):
        if name == 'text_input':
            return lambda *a, **k: k['value']
        if name == 'select_slider':
            return lambda *a, **k: k['value']
        if name == 'button':
            return lambda *a, **k: self.refresh
        if name == 'spinner':
            return lambda *a, **k: self
        return lambda *a, **k: self.displayed.append((name, a))


class AppTests(unittest.TestCase):
    def setUp(self):
        self.st = FakeStreamlit()
        component = types.ModuleType('streamlit.components.v1')
        component.declare_component = lambda *a, **k: lambda **kw: self.st.year
        components = types.ModuleType('streamlit.components')
        components.v1 = component
        self.st.components = components
        self.modules = {
            'streamlit': self.st, 'streamlit.components': components,
            'streamlit.components.v1': component, 'feedparser': types.ModuleType('feedparser'),
        }
        self.history = {
            'year': 1966, 'events': ['1966年の出来事'], 'revision': 1,
            'revision_url': 'https://example.com/source', 'retrieved_at': '2026-01-01T00:00:00Z',
        }

    def execute(self):
        with patch.dict(sys.modules, self.modules), patch.dict('os.environ', {}, clear=True), \
                patch('urllib.request.urlopen', side_effect=URLError('offline')):
            runpy.run_path(str(Path(__file__).parents[1] / 'app.py'))

    @patch('history_ai.generate_prediction', return_value='AIの予言')
    @patch('history_ai.fetch_history')
    def test_reuse_prediction_but_refetch_history_then_force_regeneration(self, fetch, generate):
        fetch.return_value = self.history
        self.execute()
        self.execute()
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(generate.call_count, 1)
        self.st.refresh = True
        self.execute()
        self.assertEqual(generate.call_count, 2)

    @patch('history_ai.generate_prediction', return_value='AIの予言')
    @patch('history_ai.fetch_history')
    def test_year_rollover_changes_selected_history_and_ai_target(self, fetch, generate):
        fetch.return_value = self.history
        self.execute()
        self.st.year = 2027
        fetch.return_value = {**self.history, 'year': 1967}
        self.execute()
        self.assertEqual(fetch.call_args.args[0], 1967)
        self.assertEqual(generate.call_args.args[0], 2027)
        self.assertEqual(generate.call_count, 2)

    @patch('history_ai.generate_prediction')
    @patch('history_ai.fetch_history')
    def test_missing_key_still_displays_history(self, fetch, generate):
        self.st.secrets = {}
        fetch.return_value = self.history
        self.execute()
        generate.assert_not_called()
        self.assertTrue(any(args == ('[1] 1966年の出来事',) for _, args in self.st.displayed))

    @patch('history_ai.generate_prediction')
    @patch('history_ai.fetch_history', side_effect=ServiceError('取得失敗'))
    def test_history_failure_never_generates_prediction(self, fetch, generate):
        self.execute()
        generate.assert_not_called()
        self.assertIn(('error', ('取得失敗',)), self.st.displayed)


if __name__ == '__main__':
    unittest.main()
