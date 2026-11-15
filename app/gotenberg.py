"""Internal Gotenberg 9 adapter (no user-controlled URL, no public endpoint)."""
from io import BytesIO
import os
import secrets
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader

from app.pdf_engine import MAX_FILE_BYTES, MAX_TOTAL_PAGES, MergeError
from app.toolkit import MAX_OUTPUT_BYTES, ToolResult

MAX_DOCX_EXPANDED = 32 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_docx(data: bytes) -> None:
    """Bound DOCX uploads without extracting the archive on our server."""
    if not data or len(data) > MAX_FILE_BYTES or not data.startswith(b"PK\x03\x04"):
        raise MergeError("Choose a valid DOCX no larger than 8 MB.")
    try:
        with ZipFile(BytesIO(data)) as source:
            entries = source.infolist()
            names = {part.filename for part in entries}
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise MergeError("This file is not a Word DOCX document.")
            if len(entries) > 256 or sum(part.file_size for part in entries) > MAX_DOCX_EXPANDED:
                raise MergeError("The DOCX exceeds processing limits.")
            if any(part.flag_bits & 1 for part in entries):
                raise MergeError("Encrypted DOCX archives are unsupported.")
    except (BadZipFile, EOFError, OSError) as exc:
        raise MergeError("The DOCX archive is damaged.") from exc


def convert_docx(data: bytes, endpoint: str | None = None) -> ToolResult:
    """Convert DOCX through a trusted internal service, validate resulting PDF."""
    validate_docx(data)
    base = endpoint if endpoint is not None else os.environ.get("PDFSTUDIO_GOTENBERG_URL", "")
    if not base or not base.startswith(("http://", "https://")):
        raise MergeError("DOCX conversion is not configured.")

    boundary = "pdfstudio-" + secrets.token_hex(12)
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="files"; filename="document.docx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    request = Request(
        base.rstrip("/") + "/forms/libreoffice/convert",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/pdf",
        },
    )
    try:
        # Do not leak private documents to process-wide proxies or follow redirects.
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(request, timeout=22) as response:
            content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if content_type != "application/pdf":
                raise MergeError("The converter returned an unexpected format.")
            result = response.read(MAX_OUTPUT_BYTES + 1)
    except HTTPError as exc:
        raise MergeError("The document converter rejected this DOCX.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise MergeError("The conversion service is unavailable.") from exc

    if len(result) > MAX_OUTPUT_BYTES or not result.startswith(b"%PDF-"):
        raise MergeError("The converter produced an invalid or oversized PDF.")
    try:
        page_count = len(PdfReader(BytesIO(result), strict=True).pages)
    except Exception as exc:
        raise MergeError("Converted PDF could not be opened.") from exc
    if not 1 <= page_count <= MAX_TOTAL_PAGES:
        raise MergeError("Converted PDF exceeds page limits.")
    return ToolResult(result, "pdfstudio-docx-to-pdf.pdf", pages=page_count)
