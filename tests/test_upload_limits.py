"""Exercise raw ASGI input so HTTP clients cannot normalize invalid headers."""

import asyncio
import unittest
from tempfile import SpooledTemporaryFile
from unittest.mock import patch

from app.upload_limits import UploadLimitMiddleware


class UploadLimitsTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, chunks, headers=(), limit=8, disconnect=False, delay=0):
        sent, received, buffers = [], [], []
        calls = 0
        queue = list(chunks)

        def spool(*args, **kwargs):
            result = SpooledTemporaryFile(*args, **kwargs)
            buffers.append(result)
            return result

        async def receive():
            nonlocal calls
            calls += 1
            if delay:
                await asyncio.sleep(delay)
            if disconnect:
                return {"type": "http.disconnect"}
            body = queue.pop(0)
            return {"type": "http.request", "body": body, "more_body": bool(queue)}

        async def send(message):
            sent.append(message)

        async def downstream(scope, receive, send):
            while True:
                message = await receive()
                received.append(message.get("body", b""))
                if not message.get("more_body", False):
                    break
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b""})

        guard = UploadLimitMiddleware(downstream, max_bytes=limit, timeout_seconds=0.03)
        with patch("app.upload_limits.SpooledTemporaryFile", spool):
            await guard({"type": "http", "headers": list(headers)}, receive, send)
        assert all(buffer.closed for buffer in buffers)
        status = next((m["status"] for m in sent if m["type"] == "http.response.start"), None)
        return status, b"".join(received), calls

    async def test_declared_oversize_rejected_without_reading(self):
        self.assertEqual(await self.exercise([b"unused"], [(b"content-length", b"9")]), (413, b"", 0))

    async def test_chunked_oversize_never_reaches_parser(self):
        status, body, _ = await self.exercise([b"12345", b"6789"])
        self.assertEqual((status, body), (413, b""))

    async def test_dishonest_length_does_not_bypass_actual_limit(self):
        status, body, _ = await self.exercise([b"123456789"], [(b"content-length", b"1")])
        self.assertEqual((status, body), (413, b""))

    async def test_exact_limit_preserves_all_chunks(self):
        status, body, _ = await self.exercise([b"1234", b"5678"])
        self.assertEqual((status, body), (204, b"12345678"))

    async def test_declared_length_matches(self):
        status, body, _ = await self.exercise([b"ok"], [(b"content-length", b"2")])
        self.assertEqual((status, body), (204, b"ok"))

    async def test_mismatched_length_rejected(self):
        status, body, _ = await self.exercise([b"ok"], [(b"content-length", b"3")])
        self.assertEqual((status, body), (400, b""))

    async def test_invalid_or_duplicate_lengths_rejected(self):
        for value in (b"-1", b"+2", b"abc", b"", b"2, 2", b"9" * 5000):
            with self.subTest(value=value[:20]):
                status, body, calls = await self.exercise([b"ok"], [(b"content-length", value)])
                self.assertEqual((status, body, calls), (400, b"", 0))
        status, _, calls = await self.exercise([b"ok"], [(b"content-length", b"2")] * 2)
        self.assertEqual((status, calls), (400, 0))

    async def test_empty_request(self):
        self.assertEqual((await self.exercise([b""]))[:2], (204, b""))

    async def test_disconnect_cleans_up_without_parsing(self):
        self.assertEqual((await self.exercise([], disconnect=True))[:2], (None, b""))

    async def test_slow_upload_times_out(self):
        self.assertEqual((await self.exercise([b"ok"], delay=0.1))[:2], (408, b""))

    async def test_large_body_spools_and_replays(self):
        body = b"a" * 300_000
        self.assertEqual((await self.exercise([body], limit=len(body)))[:2], (204, body))

    async def test_non_http_scope_passes_through(self):
        scopes = []

        async def downstream(scope, receive, send):
            scopes.append(scope)

        scope = {"type": "lifespan"}
        await UploadLimitMiddleware(downstream)(scope, None, None)
        self.assertEqual(scopes, [scope])
