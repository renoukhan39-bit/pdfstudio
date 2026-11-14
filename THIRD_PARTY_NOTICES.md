# Dependency notices

PDF Studio owns only its original code; upstream dependencies retain their own licenses. Original project licensing remains undecided. Do not replace upstream wheel license files when distributing the application.

| Component | Use | License / source |
| --- | --- | --- |
| pypdf 7.0.1 | PDF processing | BSD-3-Clause; https://github.com/py-pdf/pypdf |
| cryptography 50.0.0 | AES-256 encryption through pypdf | Apache-2.0 OR BSD-3-Clause; https://github.com/pyca/cryptography |
| FastAPI 0.141.1 | API | MIT; https://github.com/fastapi/fastapi |
| Starlette 1.6.0 | ASGI and upload infrastructure | BSD-3-Clause; https://github.com/Kludex/starlette |
| python-multipart 0.0.32 | Multipart parsing | Apache-2.0; https://github.com/Kludex/python-multipart |
| Uvicorn 0.48.0 | ASGI server | BSD-3-Clause; https://github.com/Kludex/uvicorn |

This register is not a replacement for packaged LICENSE/NOTICE files or a complete transitive/container licensing audit. CI exports a CycloneDX package inventory. Cryptography's wheels can bundle OpenSSL and retain its own license notices. No AGPL/proprietary editor source has been imported in this implementation.

Added processing dependencies: ReportLab 4.4.9 (BSD license; https://www.reportlab.com/opensource/) and Pillow 13.0.0 (MIT-CMU; https://github.com/python-pillow/Pillow). Built-in Helvetica is used for printable ASCII overlays; no third-party font files were copied. Browser test dependency Playwright 1.58.0 uses Apache-2.0; downloaded Chromium has separate bundled licenses. Preserve upstream notices in redistributed artifacts.
