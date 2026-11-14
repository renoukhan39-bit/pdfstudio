"""Synthetic fixtures and mocked HTTP; no dependency on Gotenberg for unit tests."""
from io import BytesIO
import os
import unittest
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.gotenberg import convert_docx, validate_docx
from app.main import app
from app.pdf_engine import MergeError
from app.toolkit import ToolResult


def sample_docx() -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>PDF Studio synthetic example</w:t></w:r></w:p><w:sectPr/></w:body></w:document>')
    return buffer.getvalue()


def sample_pdf() -> bytes:
    output = BytesIO()
    with PdfWriter() as writer:
        writer.add_blank_page(width=200, height=300)
        writer.write(output)
    return output.getvalue()


class GotenbergUnitTests(unittest.TestCase):
    def setUp(self):
        self.docx = sample_docx()
        self.pdf = sample_pdf()

    def test_accepts_minimal_docx(self):
        validate_docx(self.docx)

    def test_rejects_invalid_or_non_word_archives(self):
        empty_zip = BytesIO()
        with ZipFile(empty_zip, "w") as archive:
            archive.writestr("hello.txt", "not a document")
        for value in (b"", b"%PDF-not-a-docx", b"PK\x03\x04bad", empty_zip.getvalue()):
            with self.subTest(data=value[:8]), self.assertRaises(MergeError):
                validate_docx(value)

    def test_rejects_large_expanded_archive(self):
        with patch("app.gotenberg.MAX_DOCX_EXPANDED", 1), self.assertRaises(MergeError):
            validate_docx(self.docx)

    def test_fixed_route_and_no_proxy(self):
        response = MagicMock()
        response.headers = {"Content-Type": "application/pdf"}
        response.read.return_value = self.pdf
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        with patch("app.gotenberg.build_opener", return_value=opener) as factory:
            result = convert_docx(self.docx, endpoint="http://gotenberg:3000")
        self.assertEqual(result.pages, 1)
        self.assertEqual(result.data, self.pdf)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "http://gotenberg:3000/forms/libreoffice/convert")
        self.assertIn(self.docx, request.data)
        self.assertEqual(len(factory.call_args.args), 2)

    def test_rejects_wrong_content_type(self):
        response = MagicMock()
        response.headers = {"Content-Type": "text/html"}
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaises(MergeError):
            convert_docx(self.docx, endpoint="http://gotenberg:3000")

    def test_rejects_broken_pdf(self):
        response = MagicMock()
        response.headers = {"Content-Type": "application/pdf"}
        response.read.return_value = b"%PDF-broken"
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaises(MergeError):
            convert_docx(self.docx, endpoint="http://gotenberg:3000")

    def test_fails_closed_without_configuration(self):
        with patch.dict(os.environ, {"PDFSTUDIO_GOTENBERG_URL": ""}), self.assertRaises(MergeError):
            convert_docx(self.docx)

    def test_api_unconfigured_returns_503(self):
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "", "PDFSTUDIO_GOTENBERG_URL": ""}):
            with TestClient(app) as client:
                response = client.post("/api/tools/docx-to-pdf", files={"file": ("test.docx", self.docx)})
        self.assertEqual(response.status_code, 503)

    def test_api_invalid_archive_returns_422(self):
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "http://worker:8001"}):
            with TestClient(app) as client:
                response = client.post("/api/tools/docx-to-pdf", files={"file": ("test.docx", b"hello")})
        self.assertEqual(response.status_code, 422)

    def test_api_sends_valid_file_to_existing_worker(self):
        output = ToolResult(self.pdf, "pdfstudio-docx-to-pdf.pdf", pages=1)
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "http://worker:8001"}), patch(
            "app.main.execute", return_value=output
        ) as execute:
            with TestClient(app) as client:
                response = client.post("/api/tools/docx-to-pdf", files={"file": ("test.docx", self.docx)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.pdf)
        execute.assert_called_once_with("docx-to-pdf", [self.docx], {})
