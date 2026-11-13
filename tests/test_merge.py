"""Synthetic fixtures only: no user or copyrighted documents."""
from io import BytesIO
import asyncio
from unittest.mock import patch

from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter

from app.main import app, merge
from app.pdf_engine import MAX_FILE_BYTES, MAX_FILES, MAX_TOTAL_PAGES, MergeError, merge_pdf_bytes

client = TestClient(app)


def make_pdf(page_widths=(200,)):
    writer = PdfWriter()
    for width in page_widths:
        writer.add_blank_page(width=width, height=300)
    output = BytesIO()
    writer.write(output)
    writer.close()
    return output.getvalue()


def multipart(*documents):
    return [("files", (f"file-{i}.pdf", blob, "application/pdf")) for i, blob in enumerate(documents)]


def test_home_and_tool_registry():
    home = client.get("/")
    assert home.status_code == 200
    assert "PDF Studio" in home.text
    response = client.get("/api/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert [t for t in tools if t["status"] == "prototype"][0]["slug"] == "merge"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_merges_in_requested_order_and_verifies_pages():
    response = client.post("/api/tools/merge", files=multipart(make_pdf([200, 201]), make_pdf([400])))
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["x-pdf-pages"] == "3"
    assert response.headers["content-disposition"] == 'attachment; filename="pdfstudio-merged.pdf"'
    pdf = PdfReader(BytesIO(response.content))
    assert [int(p.mediabox.width) for p in pdf.pages] == [200, 201, 400]


def test_rejects_single_file():
    response = client.post("/api/tools/merge", files=multipart(make_pdf()))
    assert response.status_code == 400


def test_rejects_invalid_pdf():
    response = client.post("/api/tools/merge", files=multipart(make_pdf(), b"not a pdf"))
    assert response.status_code == 422


def test_rejects_oversized_file():
    response = client.post("/api/tools/merge", files=multipart(make_pdf(), b"%PDF-" + b"0" * MAX_FILE_BYTES))
    assert response.status_code == 413


def test_rejects_too_many_files():
    response = client.post("/api/tools/merge", files=multipart(*([make_pdf()] * (MAX_FILES + 1))))
    assert response.status_code == 400


def test_rejects_encrypted_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=300)
    writer.encrypt("example-password")
    data = BytesIO()
    writer.write(data)
    writer.close()
    response = client.post("/api/tools/merge", files=multipart(make_pdf(), data.getvalue()))
    assert response.status_code == 422
    assert "Encrypted" in response.json()["detail"]


def test_rejects_page_limit():
    many = make_pdf([200] * MAX_TOTAL_PAGES)
    try:
        merge_pdf_bytes((many, make_pdf()))
    except MergeError as exc:
        assert "pages" in str(exc)
    else:
        raise AssertionError("Expected page limit rejection")


def test_input_is_not_mutated():
    pdf1, pdf2 = make_pdf([111]), make_pdf([333])
    merged, pages = merge_pdf_bytes([pdf1, pdf2])
    assert pages == 2
    assert pdf1.startswith(b"%PDF-") and pdf2.startswith(b"%PDF-")
    assert merged != pdf1 and merged != pdf2


def test_rejects_empty_pdf_and_truncated_structure():
    for document in (make_pdf([]), b"%PDF-1.7\ntruncated"):
        response = client.post("/api/tools/merge", files=multipart(make_pdf(), document))
        assert response.status_code == 422


def test_engine_cannot_bypass_file_size_limit():
    with patch("app.pdf_engine.MAX_FILE_BYTES", 1):
        try:
            merge_pdf_bytes([make_pdf(), make_pdf()])
        except MergeError as exc:
            assert "Each PDF" in str(exc)
        else:
            raise AssertionError("Expected file-size rejection")


def test_engine_cannot_bypass_total_size_limit():
    with patch("app.pdf_engine.MAX_TOTAL_BYTES", 1):
        try:
            merge_pdf_bytes([make_pdf(), make_pdf()])
        except MergeError as exc:
            assert "Combined" in str(exc)
        else:
            raise AssertionError("Expected aggregate-size rejection")


def test_api_rejects_total_size_limit():
    with patch("app.main.MAX_TOTAL_BYTES", 1):
        response = client.post("/api/tools/merge", files=multipart(make_pdf(), make_pdf()))
    assert response.status_code == 413


def test_oversized_raw_request_retains_security_headers():
    from app.upload_limits import MAX_REQUEST_BYTES

    response = client.post("/api/tools/merge", content=b"small", headers={"Content-Length": str(MAX_REQUEST_BYTES + 1)})
    assert response.status_code == 413
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_invalid_file_count_closes_uploads():
    upload = UploadFile(file=BytesIO(make_pdf()), filename="synthetic.pdf")
    try:
        asyncio.run(merge([upload]))
    except HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("Expected file-count rejection")
    assert upload.file.closed


def test_merge_preserves_extractable_text_and_order():
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    documents = []
    for text in ("First synthetic page", "Second synthetic page"):
        with PdfWriter() as writer:
            page = writer.add_blank_page(width=200, height=300)
            font = DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            })
            page[NameObject("/Resources")] = DictionaryObject({
                NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})
            })
            stream = DecodedStreamObject()
            stream.set_data(f"BT /F1 12 Tf 20 200 Td ({text}) Tj ET".encode())
            page[NameObject("/Contents")] = writer._add_object(stream)
            output = BytesIO()
            writer.write(output)
            documents.append(output.getvalue())
    merged, count = merge_pdf_bytes(documents)
    assert count == 2
    pages = PdfReader(BytesIO(merged)).pages
    assert [page.extract_text() for page in pages] == ["First synthetic page", "Second synthetic page"]

