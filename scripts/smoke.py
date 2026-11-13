"""Run with the installed wheel's interpreter from outside the checkout."""

from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter

from app.main import app


def main():
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        assert client.get("/").status_code == 200
        for asset in ("app.js", "styles.css"):
            assert client.get(f"/static/{asset}").status_code == 200
        files = []
        for width in (200, 400):
            with PdfWriter() as writer:
                writer.add_blank_page(width=width, height=300)
                output = BytesIO()
                writer.write(output)
                files.append(("files", ("sample.pdf", output.getvalue(), "application/pdf")))
        response = client.post("/api/tools/merge", files=files)
        assert response.status_code == 200, response.text
        assert [int(p.mediabox.width) for p in PdfReader(BytesIO(response.content)).pages] == [200, 400]
    print("Installed app: health, homepage, static assets, PDF merge and output order passed.")


if __name__ == "__main__":
    main()
