"""Small-file PDF operations using pypdf; no proprietary editing claims."""

from dataclasses import dataclass
from io import BytesIO
import json
import re
from zipfile import ZIP_DEFLATED, ZipFile

from pypdf import PdfReader, PdfWriter

from app.pdf_engine import MAX_FILE_BYTES, MAX_TOTAL_PAGES, MergeError, merge_pdf_bytes

MAX_OUTPUT_BYTES = 40 * 1024 * 1024
TOOLS = [
    ("OP-01", "merge", "Merge PDF", "Combine 2–10 PDFs in the chosen order."),
    ("OP-02", "split", "Split PDF", "Download pages or page groups as a ZIP."),
    ("OP-03", "extract", "Extract pages", "Keep selected pages in the order you specify."),
    ("OP-04", "delete", "Delete pages", "Remove selected pages from a document."),
    ("OP-05", "reorder", "Reorder pages", "Choose a new order for every page."),
    ("OP-06", "rotate", "Rotate PDF", "Turn selected pages by 90, 180 or 270 degrees."),
    ("CV-12", "compress", "Compress PDF", "Lossless stream compression; savings vary by file."),
    ("OP-21", "metadata", "Edit metadata", "Set title, author, subject and keywords."),
    ("CV-10", "text", "PDF to text", "Extract existing text; scanned images need OCR."),
    ("SC-01", "protect", "Protect PDF", "Encrypt with an AES-256 password."),
    ("SC-02", "unlock", "Unlock PDF", "Remove encryption using a password you know."),
]
TOOL_SLUGS = {tool[1] for tool in TOOLS}


@dataclass
class ToolResult:
    data: bytes
    filename: str
    media_type: str = "application/pdf"
    pages: int = 0
    note: str = ""


def page_indices(expression: str, count: int, *, default_all=False) -> list[int]:
    """Parse bounded, one-based ranges; preserve order and reject duplicates."""
    if not isinstance(expression, str) or len(expression) > 2000:
        raise MergeError("Page selection is too long or invalid.")
    if not expression.strip():
        if default_all:
            return list(range(count))
        raise MergeError("Enter page numbers, for example 1,3-5.")
    selected = []
    for part in expression.split(","):
        match = re.fullmatch(r"\s*([0-9]{1,4})(?:\s*-\s*([0-9]{1,4}))?\s*", part)
        if not match:
            raise MergeError("Use page numbers and ascending ranges such as 1,3-5.")
        start = int(match[1])
        end = int(match[2] or start)
        if not 1 <= start <= end <= count:
            raise MergeError(f"Pages must be between 1 and {count}; ranges must ascend.")
        selected.extend(range(start - 1, end))
        if len(selected) > count or len(set(selected)) != len(selected):
            raise MergeError("Select each page at most once.")
    return selected


def _read(document: bytes, password: str, unlock: bool) -> PdfReader:
    if not document or len(document) > MAX_FILE_BYTES or not document.startswith(b"%PDF-"):
        raise MergeError("Use a valid PDF no larger than 8 MB.")
    reader = PdfReader(BytesIO(document), strict=True)
    if reader.is_encrypted:
        if not unlock:
            raise MergeError("Use Unlock PDF before processing an encrypted document.")
        if not reader.decrypt(password):
            raise MergeError("The password could not unlock this PDF.")
    elif unlock:
        raise MergeError("This PDF is not encrypted.")
    if not 1 <= len(reader.pages) <= MAX_TOTAL_PAGES:
        raise MergeError(f"Use a PDF with 1–{MAX_TOTAL_PAGES} pages.")
    return reader


def _save(writer: PdfWriter, count: int, password="") -> bytes:
    output = BytesIO()
    writer.write(output)
    data = output.getvalue()
    if len(data) > MAX_OUTPUT_BYTES:
        raise MergeError("The output exceeds the 40 MB limit.")
    check = PdfReader(BytesIO(data), strict=True)
    if password:
        if not check.is_encrypted or not check.decrypt(password):
            raise MergeError("Encrypted output failed verification.")
    if len(check.pages) != count:
        raise MergeError("Output page verification failed.")
    return data


def _selected_pdf(reader, indices):
    with PdfWriter() as writer:
        writer.append(reader, pages=indices, import_outline=False)
        return _save(writer, len(indices))


def process_tool(operation: str, documents: list[bytes], options: dict) -> ToolResult:
    """Return validated bytes; errors never include document text or passwords."""
    if operation not in TOOL_SLUGS:
        raise MergeError("Unknown PDF operation.")
    if not isinstance(options, dict) or len(json.dumps(options)) > 8192:
        raise MergeError("Invalid or oversized options.")
    allowed = {"pages", "angle", "password", "title", "author", "subject", "keywords"}
    if set(options) - allowed:
        raise MergeError("Unsupported option.")
    if any(not isinstance(v, str) or len(v) > 2000 for v in options.values()):
        raise MergeError("Options must be text no longer than 2000 characters.")
    if operation == "merge":
        data, pages = merge_pdf_bytes(documents)
        if len(data) > MAX_OUTPUT_BYTES:
            raise MergeError("The output exceeds the 40 MB limit.")
        return ToolResult(data, "pdfstudio-merged.pdf", pages=pages)
    if len(documents) != 1:
        raise MergeError("Choose exactly one PDF for this tool.")
    password = options.get("password", "")
    if len(password) > 256:
        raise MergeError("Passwords cannot exceed 256 characters.")
    try:
        reader = _read(documents[0], password, operation == "unlock")
        count = len(reader.pages)
        selection = options.get("pages", "")
        if operation in {"extract", "delete", "reorder"}:
            indices = page_indices(selection, count)
            if operation == "delete":
                indices = [i for i in range(count) if i not in set(indices)]
                if not indices:
                    raise MergeError("Keep at least one page.")
            if operation == "reorder" and len(indices) != count:
                raise MergeError("Reorder must include every page exactly once.")
            return ToolResult(_selected_pdf(reader, indices), f"pdfstudio-{operation}.pdf", pages=len(indices))
        if operation == "split":
            groups = selection.split(";") if selection.strip() else [str(i + 1) for i in range(count)]
            if len(groups) > MAX_TOTAL_PAGES:
                raise MergeError("Too many split groups.")
            parsed = [page_indices(group, count) for group in groups]
            if sum(map(len, parsed)) > MAX_TOTAL_PAGES:
                raise MergeError("Split output cannot exceed 200 pages in total.")
            output = BytesIO()
            uncompressed = 0
            with ZipFile(output, "w", ZIP_DEFLATED) as archive:
                for number, indices in enumerate(parsed, 1):
                    data = _selected_pdf(reader, indices)
                    uncompressed += len(data)
                    if uncompressed > MAX_OUTPUT_BYTES:
                        raise MergeError("Split output exceeds 40 MB.")
                    archive.writestr(f"part-{number:03}.pdf", data)
            return ToolResult(output.getvalue(), "pdfstudio-split.zip", "application/zip", sum(map(len, parsed)))
        if operation == "text":
            chunks = []
            size = 0
            indices = page_indices(selection, count, default_all=True)
            for i in indices:
                text = f"--- Page {i + 1} ---\n{reader.pages[i].extract_text() or ''}\n"
                encoded = text.encode("utf-8")
                size += len(encoded)
                if size > MAX_OUTPUT_BYTES:
                    raise MergeError("Extracted text exceeds 40 MB.")
                chunks.append(encoded)
            return ToolResult(b"\n".join(chunks), "pdfstudio-text.txt", "text/plain", len(indices),
                              "Scanned pages require OCR; extraction order depends on the PDF.")
        with PdfWriter() as writer:
            writer.clone_document_from_reader(reader)
            note = ""
            if operation == "rotate":
                angle = options.get("angle", "90")
                if angle not in {"90", "180", "270"}:
                    raise MergeError("Choose 90, 180 or 270 degrees.")
                for index in page_indices(selection, count, default_all=True):
                    writer.pages[index].rotate(int(angle))
            elif operation == "compress":
                for page in writer.pages:
                    page.compress_content_streams()
                writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
            elif operation == "metadata":
                writer.add_metadata({f"/{key.title()}": options[key] for key in
                                     ("title", "author", "subject", "keywords") if key in options})
                note = "Edits document-info fields only; this does not sanitize hidden data or XMP."
            elif operation == "protect":
                if len(password) < 8:
                    raise MergeError("Choose a password of at least 8 characters.")
                writer.encrypt(password, algorithm="AES-256")
            data = _save(writer, count, password if operation == "protect" else "")
            if operation == "compress" and len(data) >= len(documents[0]):
                data = documents[0]
                note = "Already optimized: the original PDF was returned without increasing its size."
            return ToolResult(data, f"pdfstudio-{operation}.pdf", pages=count, note=note)
    except MergeError:
        raise
    except Exception as exc:
        raise MergeError("This PDF could not be processed. Check the file and options.") from exc
