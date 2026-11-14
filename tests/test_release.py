"""Output and isolation-adapter regression tests using synthetic inputs."""
import base64
from io import BytesIO
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.pdf_engine import MergeError
from app.toolkit import process_tool
from app.worker import WorkerBusy, execute, remote_execute, NoRedirect
from app.worker_service import app as worker_app
from test_merge import make_pdf


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.pdf = make_pdf([200, 300])

    def test_page_numbers_are_extractable_and_selected(self):
        result = process_tool('page-numbers', [self.pdf], {'pages': '2'})
        reader = PdfReader(BytesIO(result.data))
        self.assertNotIn('1 / 2', reader.pages[0].extract_text())
        self.assertIn('2 / 2', reader.pages[1].extract_text())

    def test_watermark_is_real_pdf_text(self):
        result = process_tool('watermark', [self.pdf], {'text': 'DRAFT'})
        self.assertTrue(all('DRAFT' in p.extract_text() for p in PdfReader(BytesIO(result.data)).pages))
        for value in ('', 'a' * 121, '\n', 'नमस्ते'):
            with self.subTest(value=value[:5]), self.assertRaises(MergeError):
                process_tool('watermark', [self.pdf], {'text': value})

    def test_crop_changes_viewport_not_media_or_content(self):
        result = process_tool('crop', [self.pdf], {'pages': '1', 'margin': '20'})
        pages = PdfReader(BytesIO(result.data)).pages
        self.assertEqual(float(pages[0].cropbox.width), 160)
        self.assertEqual(float(pages[0].mediabox.width), 200)
        self.assertEqual(float(pages[1].cropbox.width), 300)
        self.assertIn('not secure redaction', result.note)
        for margin in ('-1', '501', 'nan', 'inf', 'bad', '100'):
            with self.subTest(margin=margin), self.assertRaises(MergeError):
                process_tool('crop', [self.pdf], {'margin': margin})

    def test_overlay_dimension_guard(self):
        with self.assertRaises(MergeError):
            process_tool('page-numbers', [make_pdf([10])], {})

    def test_worker_api_and_validation(self):
        with TestClient(worker_app) as client:
            self.assertEqual(client.get('/health').json(), {'status': 'ok'})
            data = {'operation': 'extract', 'documents': [base64.b64encode(self.pdf).decode()], 'options': {'pages': '2'}}
            response = client.post('/execute', json=data)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(len(PdfReader(BytesIO(base64.b64decode(response.json()['data']))).pages), 1)
            for encoded in ('@@@', '', 'a' * (12 * 1024 * 1024)):
                data['documents'] = [encoded]
                self.assertEqual(client.post('/execute', json=data).status_code, 422)
            data['documents'] = [base64.b64encode(self.pdf).decode()]
            with patch('app.worker_service.execute', side_effect=WorkerBusy('busy')):
                self.assertEqual(client.post('/execute', json=data).status_code, 503)
            with patch('app.worker_service.MAX_TOTAL_BYTES', 1):
                self.assertEqual(client.post('/execute', json=data).status_code, 422)

    def response(self):
        return {'data': base64.b64encode(self.pdf).decode(), 'filename': 'result.pdf', 'media_type': 'application/pdf', 'pages': 2, 'note': ''}

    def test_remote_result_and_environment_routing(self):
        with patch('app.worker.build_opener') as opener:
            opener.return_value.open.return_value = BytesIO(json.dumps(self.response()).encode())
            self.assertEqual(remote_execute('http://worker:8001', 'rotate', [self.pdf], {}).data, self.pdf)
            self.assertEqual(opener.return_value.open.call_args[0][0].full_url, 'http://worker:8001/execute')
        with patch.dict(os.environ, {'PDFSTUDIO_WORKER_URL': 'http://worker:8001'}), patch('app.worker.remote_execute', return_value='remote') as remote:
            self.assertEqual(execute('rotate', [self.pdf], {}), 'remote')
            remote.assert_called_once()
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'http://external'))

    def test_remote_rejects_errors_and_never_falls_back(self):
        for error, expected in (
            (HTTPError('http://worker', 503, '', {}, BytesIO(b'{}')), WorkerBusy),
            (HTTPError('http://worker', 422, '', {}, BytesIO(b'{"detail":"bad PDF"}')), MergeError),
            (HTTPError('http://worker', 422, '', {}, BytesIO(b'bad JSON')), MergeError),
            (HTTPError('http://worker', 500, '', {}, BytesIO(b'')), MergeError),
            (URLError('offline'), MergeError), (TimeoutError(), MergeError),
        ):
            with self.subTest(error=type(error)), patch('app.worker.build_opener') as opener, self.assertRaises(expected):
                opener.return_value.open.side_effect = error
                remote_execute('http://worker:8001', 'rotate', [self.pdf], {})
        with patch('app.worker.build_opener') as opener, self.assertRaises(MergeError):
            opener.return_value.open.return_value = BytesIO(b'not json')
            remote_execute('http://worker:8001', 'rotate', [self.pdf], {})


class CapacityTests(unittest.IsolatedAsyncioTestCase):
    async def test_capacity_rejects_without_reading(self):
        from app.upload_limits import UploadLimitMiddleware
        sent = []
        async def never(*args):
            raise AssertionError('Full-capacity request must not reach the parser')
        async def send(message):
            sent.append(message)
        guard = UploadLimitMiddleware(never)
        with patch.object(guard.slots, 'acquire', return_value=False):
            await guard({'type': 'http'}, never, send)
        self.assertEqual(sent[0]['status'], 503)
