"""Small, replaceable PDF engine for the initial merge proof of concept.

The API does not depend on this implementation's internals. A tested Gotenberg
adapter can replace this code in a future milestone.
"""
from io import BytesIO
from collections.abc import Sequence

from pypdf import PdfReader, PdfWriter

MAX_FILES = 10
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 40 * 1024 * 1024
MAX_TOTAL_PAGES = 200


class MergeError(ValueError):
    """Expected user-facing error for invalid PDF inputs."""


def merge_pdf_bytes(documents: Sequence[bytes]) -> tuple[bytes, int]:
    """Merge PDFs in user-selected order; return (valid PDF bytes, page count).

    This is a small-file prototype, *not* a hardened untrusted-file sandbox.
    """
    if not 2 <= len(documents) <= MAX_FILES:
        raise MergeError(f"Choose between 2 and {MAX_FILES} PDF files.")
    if any(not document or len(document) > MAX_FILE_BYTES for document in documents):
        raise MergeError("Each PDF must be between 1 byte and 8 MB.")
    if sum(map(len, documents)) > MAX_TOTAL_BYTES:
        raise MergeError("Combined files cannot exceed 40 MB.")

    writer = PdfWriter()
    pages = 0
    try:
        for document in documents:
            if not document.startswith(b"%PDF-"):
                raise MergeError("All selected files must be valid PDFs.")
            reader = PdfReader(BytesIO(document), strict=True)
            if reader.is_encrypted:
                raise MergeError("Encrypted PDFs aren't supported in this first version.")
            count = len(reader.pages)
            if count == 0:
                raise MergeError("One of the PDFs has no pages.")
            if pages + count > MAX_TOTAL_PAGES:
                raise MergeError(f"The combined document cannot exceed {MAX_TOTAL_PAGES} pages.")
            for page in reader.pages:
                writer.add_page(page)
            pages += count

        output = BytesIO()
        writer.write(output)
        merged = output.getvalue()
        if not merged.startswith(b"%PDF-") or len(PdfReader(BytesIO(merged)).pages) != pages:
            raise MergeError("The merged PDF failed verification.")
        return merged, pages
    except MergeError:
        raise
    except Exception as exc:
        raise MergeError("At least one PDF could not be read or merged.") from exc
    finally:
        writer.close()

