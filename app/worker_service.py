"""Private worker API; publish only on the internal processing network."""

import base64
import binascii

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.pdf_engine import MAX_FILE_BYTES, MAX_TOTAL_BYTES, MergeError
from app.upload_limits import UploadLimitMiddleware
from app.worker import WorkerBusy, execute

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(UploadLimitMiddleware, max_bytes=57 * 1024 * 1024)


class WorkRequest(BaseModel):
    operation: str = Field(max_length=32)
    documents: list[str] = Field(min_length=1, max_length=10)
    options: dict[str, str] = Field(default_factory=dict)


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.post('/execute')
async def run(request: WorkRequest):
    documents = []
    total = 0
    try:
        for encoded in request.documents:
            if len(encoded) > ((MAX_FILE_BYTES + 2) // 3) * 4:
                raise MergeError('Input PDF exceeds the size limit.')
            decoded = base64.b64decode(encoded, validate=True)
            total += len(decoded)
            if not decoded or len(decoded) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
                raise MergeError('Input PDF size limit exceeded.')
            documents.append(decoded)
        result = await run_in_threadpool(execute, request.operation, documents, request.options)
    except WorkerBusy as exc:
        raise HTTPException(503, str(exc), headers={'Retry-After': '5'}) from exc
    except (MergeError, binascii.Error) as exc:
        raise HTTPException(422, str(exc)) from exc
    return {'data': base64.b64encode(result.data).decode(), 'filename': result.filename,
            'media_type': result.media_type, 'pages': result.pages, 'note': result.note}
