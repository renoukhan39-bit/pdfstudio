"""Bound raw uploads before multipart parsing; this is not a PDF sandbox."""

import asyncio
from tempfile import SpooledTemporaryFile

from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.pdf_engine import MAX_TOTAL_BYTES

# Includes multipart boundaries and headers in addition to the 40 MiB file budget.
MAX_REQUEST_BYTES = MAX_TOTAL_BYTES + 1024 * 1024


class UploadLimitMiddleware:
    """Spool a bounded request, then replay it only after ingress validation.

    Counting actual bytes also covers chunked requests and dishonest length
    headers. The context manager removes temporary data on all exit paths.
    Global concurrency, reverse-proxy limits and isolated workers remain needed.
    """

    def __init__(self, app: ASGIApp, max_bytes=MAX_REQUEST_BYTES, timeout_seconds=30):
        self.app = app
        self.max_bytes = max_bytes
        self.timeout_seconds = timeout_seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def reject(status, detail):
            await JSONResponse({"detail": detail}, status_code=status)(scope, receive, send)

        lengths = [v for k, v in scope.get("headers", []) if k.lower() == b"content-length"]
        declared = None
        if lengths:
            try:
                if len(lengths) != 1 or not lengths[0].isdigit():
                    raise ValueError
                declared = int(lengths[0])
            except ValueError:
                await reject(400, "Invalid Content-Length header.")
                return
            if declared > self.max_bytes:
                await reject(413, "Upload request exceeds the size limit.")
                return

        with SpooledTemporaryFile(max_size=256 * 1024, mode="w+b") as buffer:
            total = 0
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    while True:
                        message = await receive()
                        if message["type"] == "http.disconnect":
                            return
                        chunk = message.get("body", b"")
                        total += len(chunk)
                        if total > self.max_bytes:
                            await reject(413, "Upload request exceeds the size limit.")
                            return
                        await run_in_threadpool(buffer.write, chunk)
                        if not message.get("more_body", False):
                            break
            except TimeoutError:
                await reject(408, "Upload took too long. Please try again.")
                return

            if declared is not None and total != declared:
                await reject(400, "Request body does not match Content-Length.")
                return
            await run_in_threadpool(buffer.seek, 0)
            remaining = total
            finished = False

            async def replay():
                nonlocal remaining, finished
                if finished:
                    return await receive()
                body = await run_in_threadpool(buffer.read, 64 * 1024)
                remaining -= len(body)
                finished = remaining == 0
                return {"type": "http.request", "body": body, "more_body": not finished}

            await self.app(scope, replay, send)
