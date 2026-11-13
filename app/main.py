"""PDF Studio API and small same-origin frontend, first functional milestone."""
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.pdf_engine import (
    MAX_FILE_BYTES,
    MAX_FILES,
    MAX_TOTAL_BYTES,
    MergeError,
    merge_pdf_bytes,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(title="PDF Studio", version="0.1.0", docs_url=None, redoc_url=None)
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
    return {
        "tools": [
            {"id": "OP-01", "slug": "merge", "name": "Merge PDF", "status": "prototype", "execution": "server"},
            {"id": "OP-02", "slug": "split", "name": "Split PDF", "status": "planned"},
            {"id": "CV-12", "slug": "compress", "name": "Compress PDF", "status": "planned"},
            {"id": "ED-03", "slug": "edit-text", "name": "Edit existing text", "status": "research"},
        ]
    }


@app.post("/api/tools/merge", response_class=Response)
async def merge(files: list[UploadFile] = File(...)):
    if not 2 <= len(files) <= MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Select between 2 and {MAX_FILES} PDFs.")
    payloads = []
    total = 0
    try:
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
        result, pages = merge_pdf_bytes(payloads)
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return Response(
        content=result,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="pdfstudio-merged.pdf"',
            "X-PDF-Pages": str(pages),
        },
    )
