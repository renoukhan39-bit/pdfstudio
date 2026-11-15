"""Synthetic fixtures and mocked HTTP; no dependency on Gotenberg for unit tests."""
import base64
from io import BytesIO
import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError
from zipfile import ZipFile

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.gotenberg import (
    ConversionUnavailable,
    convert_docx,
    convert_pptx,
    validate_docx,
    validate_pptx,
)
from app.main import app
from app.pdf_engine import MAX_FILE_BYTES, MergeError
from app.toolkit import ToolResult
from app.worker import execute, remote_execute
from app.worker_service import app as worker_app
from scripts.office_fixtures import make_docx, make_pptx


def sample_pdf() -> bytes:
    output = BytesIO()
    with PdfWriter() as writer:
        writer.add_blank_page(width=200, height=300)
        writer.write(output)
    return output.getvalue()


class GotenbergUnitTests(unittest.TestCase):
    def setUp(self):
        self.docx = make_docx("PDF Studio synthetic DOCX example")
        self.pptx = make_pptx()
        self.pdf = sample_pdf()

    def pdf_response(self):
        response = MagicMock()
        response.headers = {"Content-Type": "application/pdf"}
        response.read.return_value = self.pdf
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        return opener

    def test_accepts_minimal_docx_and_pptx(self):
        validate_docx(self.docx)
        validate_pptx(self.pptx)

    def test_rejects_invalid_or_wrong_ooxml_archives(self):
        empty_zip = BytesIO()
        with ZipFile(empty_zip, "w") as archive:
            archive.writestr("hello.txt", "not a document")
        invalid = (b"", b"%PDF-not-office", b"PK\x03\x04bad", empty_zip.getvalue())
        for value in invalid:
            with self.subTest(data=value[:8]), self.assertRaises(MergeError):
                validate_pptx(value)
        with self.assertRaises(MergeError):
            validate_pptx(self.docx)
        with self.assertRaises(MergeError):
            validate_docx(self.pptx)

    def test_rejects_large_expanded_or_high_ratio_archive(self):
        with patch("app.gotenberg.MAX_OOXML_EXPANDED", 1), self.assertRaises(MergeError):
            validate_pptx(self.pptx)
        with patch("app.gotenberg.MAX_OOXML_COMPRESSION_RATIO", 1), self.assertRaises(MergeError):
            validate_pptx(self.pptx)

    def test_rejects_unsafe_archive_paths(self):
        archive_data = BytesIO()
        with ZipFile(archive_data, "w") as archive:
            archive.writestr("[Content_Types].xml", "x")
            archive.writestr("ppt/presentation.xml", "x")
            archive.writestr("../escape.xml", "x")
        with self.assertRaisesRegex(MergeError, "unsafe"):
            validate_pptx(archive_data.getvalue())

    def test_fixed_route_no_proxy_and_valid_pdf_for_both_formats(self):
        for converter, document, extension in (
            (convert_docx, self.docx, ".docx"),
            (convert_pptx, self.pptx, ".pptx"),
        ):
            opener = self.pdf_response()
            with self.subTest(extension=extension), patch(
                "app.gotenberg.build_opener", return_value=opener
            ) as factory:
                result = converter(document, endpoint="http://gotenberg:3000")
                self.assertEqual(result.pages, 1)
                self.assertEqual(result.data, self.pdf)
                request = opener.open.call_args.args[0]
                self.assertEqual(request.full_url, "http://gotenberg:3000/forms/libreoffice/convert")
                self.assertIn(document, request.data)
                self.assertIn(f"document{extension}".encode(), request.data)
                self.assertEqual(len(factory.call_args.args), 2)

    def test_rejects_wrong_content_type(self):
        response = MagicMock()
        response.headers = {"Content-Type": "text/html"}
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaises(MergeError):
            convert_pptx(self.pptx, endpoint="http://gotenberg:3000")

    def test_rejects_corrupt_pdf_output(self):
        response = MagicMock()
        response.headers = {"Content-Type": "application/pdf"}
        response.read.return_value = b"%PDF-broken"
        context = MagicMock()
        context.__enter__.return_value = response
        opener = MagicMock()
        opener.open.return_value = context
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaises(MergeError):
            convert_pptx(self.pptx, endpoint="http://gotenberg:3000")

    def test_unavailable_gotenberg_is_typed_and_sanitized(self):
        opener = MagicMock()
        opener.open.side_effect = URLError("secret upstream detail")
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaisesRegex(
            ConversionUnavailable, "^The conversion service is unavailable"
        ):
            convert_pptx(self.pptx, endpoint="http://gotenberg:3000")

        error = HTTPError(
            "http://gotenberg:3000/forms/libreoffice/convert",
            503,
            "private detail",
            {},
            BytesIO(b"private response"),
        )
        opener.open.side_effect = error
        with patch("app.gotenberg.build_opener", return_value=opener), self.assertRaisesRegex(
            ConversionUnavailable, "^The conversion service is unavailable"
        ):
            convert_pptx(self.pptx, endpoint="http://gotenberg:3000")

    def test_fails_closed_without_configuration_or_with_unsafe_base_shape(self):
        with patch.dict(os.environ, {"PDFSTUDIO_GOTENBERG_URL": ""}), self.assertRaises(
            ConversionUnavailable
        ):
            convert_docx(self.docx)
        for endpoint in (
            "ftp://gotenberg:3000",
            "http://user:secret@gotenberg:3000",
            "http://gotenberg:3000/path",
            "http://gotenberg:3000?next=http://example.test",
        ):
            with self.subTest(endpoint=endpoint), self.assertRaises(ConversionUnavailable):
                convert_pptx(self.pptx, endpoint=endpoint)

    def test_api_unconfigured_returns_503_for_docx_and_pptx(self):
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "", "PDFSTUDIO_GOTENBERG_URL": ""}):
            with TestClient(app) as client:
                docx = client.post("/api/tools/docx-to-pdf", files={"file": ("test.docx", self.docx)})
                pptx = client.post("/api/tools/pptx-to-pdf", files={"file": ("test.pptx", self.pptx)})
        self.assertEqual(docx.status_code, 503)
        self.assertEqual(pptx.status_code, 503)

    def test_api_rejects_invalid_non_pptx_and_oversized_input(self):
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "http://worker:8001"}):
            with TestClient(app) as client:
                invalid = client.post(
                    "/api/tools/pptx-to-pdf",
                    files={"file": ("renamed.pptx", self.docx)},
                )
                oversized = client.post(
                    "/api/tools/pptx-to-pdf",
                    files={"file": ("large.pptx", b"PK\x03\x04" + b"x" * MAX_FILE_BYTES)},
                )
                wrong_extension = client.post(
                    "/api/tools/pptx-to-pdf",
                    files={"file": ("slides.zip", self.pptx)},
                )
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(oversized.status_code, 422)
        self.assertEqual(wrong_extension.status_code, 422)

    def test_api_sends_pptx_to_existing_worker_and_preserves_docx(self):
        output = ToolResult(self.pdf, "ignored.pdf", pages=1)
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": "http://worker:8001"}), patch(
            "app.main.execute", return_value=output
        ) as worker_execute:
            with TestClient(app) as client:
                pptx = client.post(
                    "/api/tools/pptx-to-pdf",
                    files={"file": ("slides.pptx", self.pptx)},
                )
                docx = client.post(
                    "/api/tools/docx-to-pdf",
                    files={"file": ("document.docx", self.docx)},
                )
        self.assertEqual(pptx.status_code, 200)
        self.assertEqual(pptx.content, self.pdf)
        self.assertEqual(pptx.headers["x-pdf-pages"], "1")
        self.assertEqual(docx.status_code, 200)
        self.assertEqual(
            worker_execute.call_args_list[0].args,
            ("pptx-to-pdf", [self.pptx], {}),
        )
        self.assertEqual(
            worker_execute.call_args_list[1].args,
            ("docx-to-pdf", [self.docx], {}),
        )

    def test_existing_child_worker_transport_is_reused_for_pptx(self):
        response = {
            "data": base64.b64encode(self.pdf).decode(),
            "filename": "pdfstudio-pptx-to-pdf.pdf",
            "media_type": "application/pdf",
            "pages": 1,
            "note": "",
        }
        child = SimpleNamespace(returncode=0, stdout=json.dumps(response), stderr="")
        with patch.dict(os.environ, {"PDFSTUDIO_WORKER_URL": ""}), patch(
            "app.worker.subprocess.run", return_value=child
        ) as run:
            result = execute("pptx-to-pdf", [self.pptx], {})
        self.assertEqual(result.data, self.pdf)
        payload = json.loads(run.call_args.kwargs["input"])
        self.assertEqual(payload["operation"], "pptx-to-pdf")
        self.assertEqual(base64.b64decode(payload["documents"][0]), self.pptx)

    def test_private_worker_marks_converter_unavailability_and_remote_restores_type(self):
        request = {
            "operation": "pptx-to-pdf",
            "documents": [base64.b64encode(self.pptx).decode()],
            "options": {},
        }
        with patch("app.worker_service.execute", side_effect=ConversionUnavailable("unavailable")):
            with TestClient(worker_app) as client:
                response = client.post("/execute", json=request)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["x-pdfstudio-error"], "converter-unavailable")

        error = HTTPError(
            "http://worker:8001/execute",
            503,
            "unavailable",
            {"X-PDFStudio-Error": "converter-unavailable"},
            BytesIO(b'{"detail":"unavailable"}'),
        )
        with patch("app.worker.build_opener") as opener, self.assertRaises(ConversionUnavailable):
            opener.return_value.open.side_effect = error
            remote_execute("http://worker:8001", "pptx-to-pdf", [self.pptx], {})


if __name__ == "__main__":
    unittest.main()
