"""Bounded child-process execution. This is not a network/filesystem sandbox."""

import base64
import json
import os
import subprocess
import sys
from threading import BoundedSemaphore
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from app.pdf_engine import MergeError
from app.toolkit import ToolResult, process_tool

_slots = BoundedSemaphore(2)


class WorkerBusy(MergeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def remote_execute(url, operation, documents, options):
    """Only a trusted operator configures this endpoint; clients cannot set it."""
    payload = json.dumps({"operation": operation, "documents": [base64.b64encode(d).decode() for d in documents], "options": options}).encode()
    request = Request(url.rstrip('/') + '/execute', data=payload, headers={"Content-Type": "application/json"})
    try:
        # Never route private PDF contents through environment-configured proxies.
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(request, timeout=30) as response:
            data = response.read(57 * 1024 * 1024 + 1)
        if len(data) > 57 * 1024 * 1024:
            raise MergeError("Worker response exceeds the size limit.")
        result = json.loads(data)
        return ToolResult(base64.b64decode(result['data'], validate=True), result['filename'], result['media_type'], result['pages'], result['note'])
    except HTTPError as exc:
        if exc.code == 503:
            raise WorkerBusy("Processing is busy. Please try again shortly.") from exc
        if exc.code == 422:
            try:
                detail = json.loads(exc.read(8192)).get('detail', 'The worker rejected this document.')
            except ValueError:
                detail = 'The worker rejected this document.'
            raise MergeError(detail if isinstance(detail, str) else 'Invalid document.') from exc
        raise MergeError("The processing service is unavailable.") from exc
    except (URLError, TimeoutError, ValueError, KeyError) as exc:
        raise MergeError("The processing service did not return a valid result.") from exc


def execute(operation, documents, options):
    endpoint = os.environ.get("PDFSTUDIO_WORKER_URL")
    if endpoint:
        return remote_execute(endpoint, operation, documents, options)
    if not _slots.acquire(blocking=False):
        raise WorkerBusy("Both processing slots are busy. Please try again shortly.")
    try:
        payload = json.dumps({"operation": operation, "documents": [base64.b64encode(d).decode() for d in documents], "options": options})
        try:
            child = subprocess.run([sys.executable, "-m", "app.worker"], input=payload,
                                   text=True, capture_output=True, timeout=25, check=False)
        except subprocess.TimeoutExpired as exc:
            raise MergeError("Processing exceeded the 25-second time limit.") from exc
        if child.returncode:
            raise MergeError("Processing stopped because the worker failed or exceeded a resource limit.")
        result = json.loads(child.stdout)
        if "error" in result:
            raise MergeError(result["error"])
        return ToolResult(base64.b64decode(result["data"]), result["filename"], result["media_type"], result["pages"], result["note"])
    finally:
        _slots.release()


def main():
    if sys.platform == "linux":
        import resource

        resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (20, 20))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    try:
        payload = json.load(sys.stdin)
        result = process_tool(payload["operation"], [base64.b64decode(d) for d in payload["documents"]], payload["options"])
        response = {"data": base64.b64encode(result.data).decode(), "filename": result.filename,
                    "media_type": result.media_type, "pages": result.pages, "note": result.note}
    except MergeError as exc:
        response = {"error": str(exc)}
    except Exception:
        response = {"error": "The processing worker could not complete this operation."}
    sys.stdout.write(json.dumps(response))


if __name__ == "__main__":
    main()
