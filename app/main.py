"""PDF Studio API and small same-origin frontend, first functional milestone."""
from pathlib import Path
import json
import os

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.pdf_engine import (
    MAX_FILE_BYTES,
    MAX_FILES,
    MAX_TOTAL_BYTES,
    MergeError,
)
from app.upload_limits import UploadLimitMiddleware
from app.toolkit import TOOLS, TOOL_SLUGS
from app.gotenberg import validate_docx
from app.worker import WorkerBusy, execute

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(title="PDF Studio", version="0.1.0", docs_url=None, redoc_url=None)
app.add_middleware(UploadLimitMiddleware)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    return response


@app.get("/", include_in_schema=False)
async def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pdfstudio", "version": "0.1.0"}


@app.get("/api/tools")
async def available_tools():
    return {"tools": [{"id": id_, "slug": slug, "name": name, "description": description,
                       "status": "prototype", "execution": "server"} for id_, slug, name, description in TOOLS]}


@app.post("/api/tools/merge", response_class=Response)
async def merge(files: list[UploadFile] = File(...)):
    payloads = []
    total = 0
    try:
        if not 2 <= len(files) <= MAX_FILES:
            raise HTTPException(status_code=400, detail=f"Select between 2 and {MAX_FILES} PDFs.")
        for upload in files:
            data = await upload.read(MAX_FILE_BYTES + 1)
            if not data or len(data) > MAX_FILE_BYTES:
                raise HTTPException(status_code=413, detail="Each PDF must be between 1 byte and 8 MB.")
            total += len(data)
            if total > MAX_TOTAL_BYTES:
                raise HTTPException(status_code=413, detail="Combined files cannot exceed 40 MB.")
            payloads.append(data)
    finally:
        for upload in files:
            await upload.close()

    try:
        result = await run_in_threadpool(execute, "merge", payloads, {})
    except WorkerBusy as exc:
        raise HTTPException(status_code=503, detail=str(exc), headers={"Retry-After": "5"}) from exc
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return Response(
        content=result.data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="pdfstudio-merged.pdf"',
            "X-PDF-Pages": str(result.pages),
        },
    )



@app.post("/api/tools/docx-to-pdf", response_class=Response)
async def docx_to_pdf(file: UploadFile = File(...)):
    """Experimental internal converter; not yet advertised among the 14 tools."""
    try:
        if not file.filename or not file.filename.lower().endswith(".docx"):
            raise HTTPException(status_code=422, detail="Choose a DOCX file.")
        data = await file.read(MAX_FILE_BYTES + 1)
        try:
            validate_docx(data)
        except MergeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await file.close()
    if not (os.environ.get("PDFSTUDIO_WORKER_URL") or os.environ.get("PDFSTUDIO_GOTENBERG_URL")):
        raise HTTPException(status_code=503, detail="Office conversion is not configured.")
    try:
        result = await run_in_threadpool(execute, "docx-to-pdf", [data], {})
    except WorkerBusy as exc:
        raise HTTPException(status_code=503, detail=str(exc), headers={"Retry-After": "5"}) from exc
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(result.data, media_type=result.media_type, headers={
        "Content-Disposition": 'attachment; filename="pdfstudio-docx-to-pdf.pdf"',
        "X-PDF-Pages": str(result.pages),
    })


@app.post("/api/tools/{operation}", response_class=Response)
async def process(operation: str, file: UploadFile = File(...), options: str = Form("{}")):
    try:
        if operation not in TOOL_SLUGS or operation == "merge":
            raise HTTPException(status_code=404, detail="Unknown PDF tool.")
        if len(options) > 8192:
            raise HTTPException(status_code=422, detail="Options exceed the size limit.")
        try:
            settings = json.loads(options)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Options must be valid JSON.") from exc
        if not isinstance(settings, dict):
            raise HTTPException(status_code=422, detail="Options must be a JSON object.")
        data = await file.read(MAX_FILE_BYTES + 1)
        if not data or len(data) > MAX_FILE_BYTES:
            raise HTTPException(status_code=413, detail="Choose a nonempty PDF no larger than 8 MB.")
    finally:
        await file.close()
    try:
        result = await run_in_threadpool(execute, operation, [data], settings)
    except WorkerBusy as exc:
        raise HTTPException(status_code=503, detail=str(exc), headers={"Retry-After": "5"}) from exc
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(result.data, media_type=result.media_type, headers={
        "Content-Disposition": f'attachment; filename="{result.filename}"',
        "X-PDF-Pages": str(result.pages), "X-PDF-Notice": result.note,
    })

