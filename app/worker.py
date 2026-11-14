"""Bounded child-process execution. This is not a network/filesystem sandbox."""

import base64
import json
import subprocess
import sys
from threading import BoundedSemaphore

from app.pdf_engine import MergeError
from app.toolkit import ToolResult, process_tool

_slots = BoundedSemaphore(2)


class WorkerBusy(MergeError):
    pass


def execute(operation, documents, options):
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
