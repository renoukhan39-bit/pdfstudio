"""Real private-Gotenberg DOCX conversion smoke test; synthetic document only."""
from io import BytesIO
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile

from pypdf import PdfReader


def make_docx():
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>',
        )
        archive.writestr(
            "_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="word/document.xml"/></Relationships>',
        )
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>PDF Studio conversion smoke test</w:t></w:r></w:p>'
            '<w:sectPr/></w:body></w:document>',
        )
    return output.getvalue()


def main():
    docx = make_docx()
    boundary = "pdfstudio-smoke-test"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="synthetic.docx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    ).encode() + docx + f"\r\n--{boundary}--\r\n".encode()
    request = Request(
        "http://127.0.0.1:8000/api/tools/docx-to-pdf",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    for attempt in range(20):
        try:
            with urlopen(request, timeout=30) as response:
                assert response.status == 200
                assert response.headers.get_content_type() == "application/pdf"
                result = response.read(40 * 1024 * 1024 + 1)
            pdf = PdfReader(BytesIO(result), strict=True)
            assert len(pdf.pages) == 1
            extracted = pdf.pages[0].extract_text() or ""
            assert "PDF Studio conversion smoke test" in extracted, repr(extracted)
            print("Private Gotenberg DOCX-to-PDF conversion succeeded; PDF text verified.")
            return
        except HTTPError as exc:
            if exc.code != 503:
                detail = exc.read(4096).decode("utf-8", "replace")
                raise AssertionError(f"Conversion failed (HTTP {exc.code}): {detail}") from exc
        except URLError:
            pass
        if attempt < 19:
            time.sleep(2)
    raise AssertionError("DOCX conversion did not become ready within smoke-test retries.")


if __name__ == "__main__":
    main()
