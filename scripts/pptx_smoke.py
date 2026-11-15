"""Real private-Gotenberg PPTX conversion smoke test; synthetic presentation only."""

from io import BytesIO
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pypdf import PdfReader

from office_fixtures import make_pptx


def main():
    pptx = make_pptx()
    boundary = "pdfstudio-pptx-smoke-test"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="synthetic.pptx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation\r\n\r\n"
    ).encode() + pptx + f"\r\n--{boundary}--\r\n".encode()
    request = Request(
        "http://127.0.0.1:8000/api/tools/pptx-to-pdf",
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
            assert "PDF Studio PowerPoint smoke test" in extracted, repr(extracted)
            print("Private Gotenberg PPTX-to-PDF conversion succeeded; slide text and page count verified.")
            return
        except HTTPError as exc:
            if exc.code != 503:
                detail = exc.read(4096).decode("utf-8", "replace")
                raise AssertionError(f"Conversion failed (HTTP {exc.code}): {detail}") from exc
        except URLError:
            pass
        if attempt < 19:
            time.sleep(2)
    raise AssertionError("PPTX conversion did not become ready within smoke-test retries.")


if __name__ == "__main__":
    main()
