"""Internal Gotenberg 9 Office adapter (trusted operator URL only)."""

from dataclasses import dataclass
from io import BytesIO
from ipaddress import ip_address
import os
import re
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from pypdf import PdfReader

from app.pdf_engine import MAX_FILE_BYTES, MAX_TOTAL_PAGES, MergeError
from app.toolkit import MAX_OUTPUT_BYTES, ToolResult

MAX_OOXML_EXPANDED = 32 * 1024 * 1024
MAX_OOXML_ENTRIES = 256
MAX_OOXML_COMPRESSION_RATIO = 200
MAX_CONTENT_TYPES_BYTES = 256 * 1024


@dataclass(frozen=True)
class OfficeFormat:
    label: str
    extension: str
    media_type: str
    required_part: str
    main_content_type: str
    output_filename: str


OFFICE_FORMATS = {
    "docx": OfficeFormat(
        label="DOCX",
        extension=".docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        required_part="word/document.xml",
        main_content_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
        ),
        output_filename="pdfstudio-docx-to-pdf.pdf",
    ),
    "pptx": OfficeFormat(
        label="PPTX",
        extension=".pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        required_part="ppt/presentation.xml",
        main_content_type=(
            "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
        ),
        output_filename="pdfstudio-pptx-to-pdf.pdf",
    ),
}


class ConversionUnavailable(MergeError):
    """The configured internal converter could not serve the request."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _unsafe_archive_name(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return (
        not normalized
        or "\x00" in normalized
        or normalized.startswith("/")
        or re.match(r"^[A-Za-z]:", normalized) is not None
        or any(part == ".." for part in normalized.split("/"))
    )


def validate_office_ooxml(data: bytes, kind: str) -> None:
    """Validate a bounded OOXML package without extracting it to the filesystem."""
    spec = OFFICE_FORMATS[kind]
    if not data or len(data) > MAX_FILE_BYTES or not data.startswith(b"PK\x03\x04"):
        raise MergeError(f"Choose a valid {spec.label} no larger than 8 MB.")
    try:
        with ZipFile(BytesIO(data)) as source:
            entries = source.infolist()
            names = [part.filename for part in entries]
            if len(entries) > MAX_OOXML_ENTRIES:
                raise MergeError(f"The {spec.label} exceeds processing limits.")
            if len(names) != len(set(names)) or any(_unsafe_archive_name(name) for name in names):
                raise MergeError(f"The {spec.label} archive contains unsafe or duplicate paths.")
            if "[Content_Types].xml" not in names or spec.required_part not in names:
                if kind == "pptx":
                    raise MergeError("This file is not a PowerPoint PPTX document.")
                raise MergeError("This file is not a Word DOCX document.")

            expanded = 0
            for part in entries:
                if part.flag_bits & 1:
                    raise MergeError(f"Encrypted {spec.label} archives are unsupported.")
                expanded += part.file_size
                if part.file_size > MAX_OOXML_EXPANDED or expanded > MAX_OOXML_EXPANDED:
                    raise MergeError(f"The {spec.label} exceeds processing limits.")
                if part.file_size and (
                    part.compress_size <= 0
                    or part.file_size > part.compress_size * MAX_OOXML_COMPRESSION_RATIO
                ):
                    raise MergeError(f"The {spec.label} archive expands too aggressively.")

            info = source.getinfo("[Content_Types].xml")
            if info.file_size > MAX_CONTENT_TYPES_BYTES:
                raise MergeError(f"The {spec.label} content manifest is too large.")
            with source.open(info) as manifest:
                content_types = manifest.read(MAX_CONTENT_TYPES_BYTES + 1)
            if len(content_types) > MAX_CONTENT_TYPES_BYTES:
                raise MergeError(f"The {spec.label} content manifest is too large.")
            try:
                root = ElementTree.fromstring(content_types)
            except ElementTree.ParseError as exc:
                raise MergeError(f"The {spec.label} content manifest is damaged.") from exc
            expected_part = "/" + spec.required_part
            if not any(
                element.tag.rsplit("}", 1)[-1] == "Override"
                and element.attrib.get("PartName") == expected_part
                and element.attrib.get("ContentType") == spec.main_content_type
                for element in root.iter()
            ):
                if kind == "pptx":
                    raise MergeError("This file is not a PowerPoint PPTX document.")
                raise MergeError("This file is not a Word DOCX document.")
    except MergeError:
        raise
    except (BadZipFile, EOFError, OSError, KeyError, RuntimeError) as exc:
        raise MergeError(f"The {spec.label} archive is damaged.") from exc


def validate_docx(data: bytes) -> None:
    validate_office_ooxml(data, "docx")


def validate_pptx(data: bytes) -> None:
    validate_office_ooxml(data, "pptx")


def _trusted_gotenberg_base(endpoint: str | None) -> str:
    base = endpoint if endpoint is not None else os.environ.get("PDFSTUDIO_GOTENBERG_URL", "")
    try:
        parsed = urlsplit(base)
    except ValueError as exc:
        raise ConversionUnavailable("Office conversion is not configured.") from exc
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ConversionUnavailable("Office conversion is not configured.")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname not in {"gotenberg", "localhost"}:
        try:
            address = ip_address(hostname)
        except ValueError as exc:
            raise ConversionUnavailable("Office conversion must use an internal service.") from exc
        if not (address.is_private or address.is_loopback or address.is_link_local):
            raise ConversionUnavailable("Office conversion must use an internal service.")
    return base.rstrip("/")


def convert_office(data: bytes, kind: str, endpoint: str | None = None) -> ToolResult:
    """Convert one validated OOXML file through the trusted internal Gotenberg service."""
    spec = OFFICE_FORMATS[kind]
    validate_office_ooxml(data, kind)
    base = _trusted_gotenberg_base(endpoint)

    boundary = "pdfstudio-" + secrets.token_hex(12)
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files"; filename="document{spec.extension}"\r\n'
        f"Content-Type: {spec.media_type}\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    request = Request(
        base + "/forms/libreoffice/convert",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/pdf",
        },
    )
    try:
        # Private documents must not use process-wide proxies or redirects.
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(request, timeout=22) as response:
            content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if content_type != "application/pdf":
                raise MergeError("The document converter returned an unexpected format.")
            result = response.read(MAX_OUTPUT_BYTES + 1)
    except HTTPError as exc:
        if 500 <= exc.code <= 599:
            raise ConversionUnavailable("The conversion service is unavailable.") from exc
        raise MergeError(f"The document converter rejected this {spec.label}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ConversionUnavailable("The conversion service is unavailable.") from exc

    if len(result) > MAX_OUTPUT_BYTES or not result.startswith(b"%PDF-"):
        raise MergeError("The converter produced an invalid or oversized PDF.")
    try:
        reader = PdfReader(BytesIO(result), strict=True)
        if reader.is_encrypted:
            raise MergeError("Converted PDF output is unexpectedly encrypted.")
        page_count = len(reader.pages)
    except MergeError:
        raise
    except Exception as exc:
        raise MergeError("Converted PDF could not be opened.") from exc
    if not 1 <= page_count <= MAX_TOTAL_PAGES:
        raise MergeError("Converted PDF exceeds page limits.")
    return ToolResult(result, spec.output_filename, pages=page_count)


def convert_docx(data: bytes, endpoint: str | None = None) -> ToolResult:
    return convert_office(data, "docx", endpoint)


def convert_pptx(data: bytes, endpoint: str | None = None) -> ToolResult:
    return convert_office(data, "pptx", endpoint)
