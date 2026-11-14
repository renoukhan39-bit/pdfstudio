"""Synthetic round-trip, option-validation and API acceptance tests."""
import json
from io import BytesIO, StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.pdf_engine import MergeError
from app.toolkit import TOOLS, page_indices, process_tool
from app import worker
from test_merge import make_pdf


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.document = make_pdf([100, 200, 300])

    def process(self, slug, **options):
        return process_tool(slug, [self.document], options)

    def widths(self, data):
        return [int(page.mediabox.width) for page in PdfReader(BytesIO(data)).pages]

    def test_extract_preserves_selected_order(self):
        self.assertEqual(self.widths(self.process('extract', pages='3,1').data), [300, 100])

    def test_delete_retains_other_pages(self):
        self.assertEqual(self.widths(self.process('delete', pages='2').data), [100, 300])
        with self.assertRaises(MergeError):
            self.process('delete', pages='1-3')

    def test_reorder_requires_complete_permutation(self):
        self.assertEqual(self.widths(self.process('reorder', pages='3,2,1').data), [300, 200, 100])
        with self.assertRaises(MergeError):
            self.process('reorder', pages='2,1')

    def test_split_zip_reopens_every_output(self):
        result = self.process('split', pages='1-2;3')
        self.assertEqual(result.media_type, 'application/zip')
        with ZipFile(BytesIO(result.data)) as archive:
            self.assertEqual(archive.namelist(), ['part-001.pdf', 'part-002.pdf'])
            self.assertEqual(self.widths(archive.read('part-001.pdf')), [100, 200])
            self.assertEqual(self.widths(archive.read('part-002.pdf')), [300])
        with ZipFile(BytesIO(self.process('split').data)) as archive:
            self.assertEqual(len(archive.namelist()), 3)

    def test_split_bounds_amplification(self):
        for pages in ('1;' * 201, ';'.join(['1-3'] * 67)):
            with self.subTest(pages=pages[:10]), self.assertRaises(MergeError):
                self.process('split', pages=pages)
        with patch('app.toolkit.MAX_OUTPUT_BYTES', len(self.document) + 50):
            with self.assertRaises(MergeError):
                self.process('split')

    def test_rotate_only_selected_page(self):
        result = self.process('rotate', pages='2', angle='270')
        self.assertEqual([p.rotation for p in PdfReader(BytesIO(result.data)).pages], [0, 270, 0])
        with self.assertRaises(MergeError):
            self.process('rotate', angle='45')

    def test_compression_never_increases_size_or_changes_page_order(self):
        result = self.process('compress')
        self.assertLessEqual(len(result.data), len(self.document))
        self.assertEqual(self.widths(result.data), [100, 200, 300])

    def test_metadata_round_trip(self):
        result = self.process('metadata', title='Synthetic title', author='QA', subject='Test', keywords='one,two')
        metadata = PdfReader(BytesIO(result.data)).metadata
        self.assertEqual(metadata.title, 'Synthetic title')
        self.assertEqual(metadata.author, 'QA')
        self.assertIn('does not sanitize', result.note)

    def test_text_export_and_limit(self):
        result = self.process('text', pages='3,1')
        self.assertEqual(result.media_type, 'text/plain')
        self.assertLess(result.data.index(b'Page 3'), result.data.index(b'Page 1'))
        self.assertNotIn(b'Page 2', result.data)
        with patch('app.toolkit.MAX_OUTPUT_BYTES', 1), self.assertRaises(MergeError):
            self.process('text')

    def test_aes256_protect_and_authorized_unlock(self):
        encrypted = self.process('protect', password='synthetic-password')
        reader = PdfReader(BytesIO(encrypted.data))
        self.assertTrue(reader.is_encrypted)
        self.assertEqual(reader.trailer['/Encrypt']['/V'], 5)
        self.assertEqual(reader.decrypt('wrong-password'), 0)
        self.assertTrue(reader.decrypt('synthetic-password'))
        self.assertEqual(len(reader.pages), 3)
        unlocked = process_tool('unlock', [encrypted.data], {'password': 'synthetic-password'})
        self.assertFalse(PdfReader(BytesIO(unlocked.data)).is_encrypted)
        self.assertEqual(self.widths(unlocked.data), [100, 200, 300])
        with self.assertRaises(MergeError):
            process_tool('unlock', [encrypted.data], {'password': 'wrong'})
        with self.assertRaises(MergeError):
            process_tool('rotate', [encrypted.data], {})

    def test_password_validation(self):
        for options in ({'password': 'short'}, {'password': 'x' * 257}):
            with self.subTest(options=options), self.assertRaises(MergeError):
                self.process('protect', **options)
        with self.assertRaises(MergeError):
            self.process('unlock', password='any-password')

    def test_invalid_ranges(self):
        for value in ('', '0', '4', '2-1', '1,1', '1-2,2', 'a', '1,,2', '1-' , '1' * 2001):
            with self.subTest(value=value[:20]), self.assertRaises(MergeError):
                page_indices(value, 3)
        self.assertEqual(page_indices(' 1, 2-3 ', 3), [0, 1, 2])
        self.assertEqual(page_indices('', 3, default_all=True), [0, 1, 2])

    def test_options_and_input_validation(self):
        for operation, documents, options in (
            ('missing', [self.document], {}), ('rotate', [], {}),
            ('rotate', [self.document], []), ('rotate', [self.document], {'bogus': '1'}),
            ('rotate', [self.document], {'angle': 90}), ('rotate', [self.document], {'title': 'a' * 2001}),
            ('metadata', [self.document], {'title': 'a' * 9000}),
            ('rotate', [b'not pdf'], {}), ('rotate', [b'%PDF-1.7 truncated'], {}),
            ('rotate', [make_pdf([])], {}),
        ):
            with self.subTest(operation=operation, options=str(options)[:40]), self.assertRaises(MergeError):
                process_tool(operation, documents, options)
        with patch('app.toolkit.MAX_OUTPUT_BYTES', 1), self.assertRaises(MergeError):
            self.process('rotate')
        with patch('app.toolkit.MAX_OUTPUT_BYTES', 1), self.assertRaises(MergeError):
            process_tool('merge', [self.document, self.document], {})

    def test_api_tools_and_round_trip(self):
        with TestClient(app) as client:
            self.assertEqual(len(client.get('/api/tools').json()['tools']), len(TOOLS))
            response = client.post('/api/tools/extract', files={'file': ('sample.pdf', self.document)}, data={'options': json.dumps({'pages': '2'})})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(self.widths(response.content), [200])
            self.assertEqual(response.headers['x-pdf-pages'], '1')
            self.assertEqual(response.headers['cache-control'], 'no-store')
            self.assertIn('attachment', response.headers['content-disposition'])

    def test_api_rejects_bad_requests(self):
        with TestClient(app) as client:
            for operation, options, data, expected in (
                ('not-a-tool', '{}', self.document, 404),
                ('rotate', 'bad-json', self.document, 422),
                ('rotate', '[]', self.document, 422),
                ('rotate', 'x' * 8193, self.document, 422),
                ('rotate', '{}', b'', 413),
                ('rotate', '{"angle":"45"}', self.document, 422),
            ):
                with self.subTest(operation=operation, expected=expected):
                    response = client.post('/api/tools/' + operation, files={'file': ('a.pdf', data)}, data={'options': options})
                    self.assertEqual(response.status_code, expected, response.text)
            with patch('app.main.execute', side_effect=worker.WorkerBusy('Busy')):
                response = client.post('/api/tools/rotate', files={'file': ('a.pdf', self.document)})
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.headers['retry-after'], '5')

    def test_worker_errors_and_capacity(self):
        with patch('app.worker._slots') as slots:
            slots.acquire.return_value = False
            with self.assertRaises(worker.WorkerBusy):
                worker.execute('rotate', [self.document], {})
        with patch('app.worker.subprocess.run', return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(MergeError):
                worker.execute('rotate', [self.document], {})
        import subprocess
        with patch('app.worker.subprocess.run', side_effect=subprocess.TimeoutExpired('worker', 25)):
            with self.assertRaises(MergeError):
                worker.execute('rotate', [self.document], {})

    def test_child_protocol_without_setting_process_limits(self):
        import base64
        payload = {'operation': 'rotate', 'documents': [base64.b64encode(self.document).decode()], 'options': {}}
        for request, error in ((json.dumps(payload), False), ('{}', True), (json.dumps(dict(payload, operation='unknown')), True)):
            output = StringIO()
            with patch('app.worker.sys.platform', 'test'), patch('app.worker.sys.stdin', StringIO(request)), patch('app.worker.sys.stdout', output):
                worker.main()
            result = json.loads(output.getvalue())
            self.assertEqual('error' in result, error)
