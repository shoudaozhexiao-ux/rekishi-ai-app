import json
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

from history_ai import EventParser, ServiceError, fetch_history, generate_prediction, read_json


class HistoryTests(unittest.TestCase):
    def test_extract_only_events_and_keep_month(self):
        parser = EventParser()
        parser.feed('''<h2>概要</h2><ul><li>無関係の概要</li></ul>
            <div class="mw-heading"><h2>できごと</h2></div>
            <h3>1月</h3><ul><li>1月1日 - 最初の出来事<sup>[1]</sup></li>
            <li>2月<ul><li>2日 - 次の出来事</li></ul></li></ul>
            <h2>誕生</h2><ul><li>無関係の誕生情報</li></ul>''')
        self.assertEqual(parser.events, ['1月1日 - 最初の出来事', '2月 2日 - 次の出来事'])

    @patch('history_ai.read_json')
    def test_latest_revision_fetched_each_time_and_sample_whole_year(self, read):
        html = '<h2>出来事</h2><ul>' + ''.join(
            f'<li>出来事番号{i:03d} - 内容の説明</li>' for i in range(100)
        ) + '</ul><h2>死去</h2><ul><li>除外する項目</li></ul>'
        read.side_effect = [
            {'parse': {'text': html, 'revid': 1}},
            {'parse': {'text': html, 'revid': 2}},
        ]
        first, second = fetch_history(1966), fetch_history(1966)
        self.assertEqual(read.call_count, 2)
        self.assertIn('page=1966', read.call_args.args[0].full_url)
        self.assertEqual(len(first['events']), 36)
        self.assertIn('000', first['events'][0])
        self.assertIn('099', first['events'][-1])
        self.assertEqual(second['revision'], 2)
        self.assertTrue(second['revision_url'].endswith('oldid=2'))

    @patch('history_ai.read_json', return_value={'error': {'code': 'missingtitle'}})
    def test_missing_history_is_error_not_invented(self, read):
        with self.assertRaises(ServiceError):
            fetch_history(1966)

    @patch('history_ai.urlopen')
    def test_connection_error_does_not_leak_raw_response(self, open_url):
        open_url.side_effect = HTTPError('url', 401, 'secret-key', {}, None)
        with self.assertRaises(ServiceError) as error:
            read_json('request')
        self.assertNotIn('secret-key', str(error.exception))


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.history = {'year': 1966, 'events': ['1966年の取得済み出来事'], 'revision_url': 'https://example.com/source'}

    @patch('history_ai.read_json')
    def test_prompt_uses_browser_year_and_fetched_facts(self, read):
        read.return_value = {'status': 'completed', 'output': [
            {'type': 'reasoning', 'content': []},
            {'type': 'message', 'content': [{'type': 'output_text', 'text': '生成した予言'}]},
        ]}
        result = generate_prediction(2026, self.history, '人工知能', 'test-key', 'test-model')
        request = read.call_args.args[0]
        payload = json.loads(request.data)
        evidence = json.loads(payload['input'])
        self.assertEqual(evidence['prediction_year'], 2026)
        self.assertEqual(evidence['events'][0]['text'], self.history['events'][0])
        self.assertEqual(payload['model'], 'test-model')
        self.assertFalse(payload['store'])
        self.assertNotIn('test-key', request.data.decode())
        self.assertEqual(result, '生成した予言')

    @patch('history_ai.read_json')
    def test_rollover_and_range_limits(self, read):
        read.return_value = {'status': 'completed', 'output': [
            {'type': 'message', 'content': [{'type': 'output_text', 'text': '予言'}]},
        ]}
        for year in (2026, 2027):
            generate_prediction(year, self.history, '', 'test-key', 'test-model')
            payload = json.loads(read.call_args.args[0].data)
            self.assertEqual(json.loads(payload['input'])['prediction_year'], year)
        with self.assertRaises(ServiceError):
            generate_prediction(2025, self.history, '', 'test-key', 'test-model')

    @patch('history_ai.read_json')
    def test_missing_key_does_not_make_api_call(self, read):
        with self.assertRaises(ServiceError):
            generate_prediction(2026, self.history, '', '', 'test-model')
        read.assert_not_called()

    @patch('history_ai.read_json', return_value={'status': 'incomplete', 'output': []})
    def test_incomplete_generation_is_not_displayed(self, read):
        with self.assertRaises(ServiceError):
            generate_prediction(2026, self.history, '', 'test-key', 'test-model')


if __name__ == '__main__':
    unittest.main()
