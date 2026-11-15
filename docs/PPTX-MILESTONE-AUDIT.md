# PPTX-to-PDF Milestone Audit

**Date:** 2026-11-15  
**Branch:** `feat/pptx-to-pdf-gotenberg`  
**Scope:** Stages A-D only; this audit precedes source-code changes for the PPTX milestone.

## A. Architecture audit

### Implemented request path

```text
Browser (app/static)
  -> FastAPI /api/tools/* (app/main.py)
  -> raw-body/concurrency guard (app/upload_limits.py)
  -> endpoint-specific input validation
  -> app.worker.execute()
     -> Compose: trusted private worker HTTP endpoint
        -> app.worker_service /execute
        -> bounded child process via app.worker.execute()
     -> local development: bounded child process directly
  -> pypdf toolkit OR Gotenberg adapter
  -> output signature/structure/page/size validation
  -> FastAPI response
  -> browser download
  -> optional "Use result in another tool" PDF chaining
```

The worker is private in Compose, has no published port, runs on the internal `processing` network, and Gotenberg is reachable only from that network. The current adapter disables environment proxies and redirects. These are implemented controls, not proposed architecture.

### Current module responsibilities

| Module | Implemented responsibility | PPTX milestone placement |
| --- | --- | --- |
| `app/main.py` | FastAPI routes, upload reading, public error/status mapping, response headers | Add one PPTX endpoint using the same Office conversion path as DOCX |
| `app/toolkit.py` | Tool catalog and pypdf operations | Register PowerPoint-to-PDF; keep PDF operations unchanged |
| `app/pdf_engine.py` | Shared byte/page limits and PDF merge validation | Reuse existing 8 MiB input and 200-page limits |
| `app/gotenberg.py` | DOCX package validation, trusted Gotenberg request, PDF output validation | Generalize to a small OOXML Office adapter; preserve DOCX wrapper |
| `app/worker.py` | Remote/private-worker routing and bounded child execution | Route both DOCX and PPTX through the same conversion mechanism |
| `app/worker_service.py` | Private worker API and base64/request bounds | Reuse unchanged contract; improve generic document wording if touched |
| `app/upload_limits.py` | Bounds raw request bytes before multipart parsing; limits active uploads | Reuse unchanged |
| `app/page_decorations.py` | Page-number/watermark/crop PDF operations | No PPTX change |
| `app/static/app.js` | Tool discovery, file selection, options, download and result chaining | Treat DOCX/PPTX as Office source tools without a framework rewrite |
| `app/static/index.html` | Branded no-build workspace | Update truthful tool count/copy |
| `compose.yaml` | API/worker/Gotenberg topology and isolation | Replace rolling Gotenberg tag after exact-image verification |
| `.github/workflows/ci.yml` | Required quality, matrix, package, audit, container, integration, guardrail and mutation jobs | Add PPTX integration smoke without removing existing checks |

### Proposed, not implemented in this milestone

PDF.js belongs in the browser workspace in Stage C as locally served, version-pinned viewer/worker assets. It should render the current browser-held/uploaded PDF and integrate with existing chaining. It does not replace the FastAPI processing architecture and does not solve native existing-text editing.

## B. Feature inventory

Status semantics follow `PLANNED -> IN_PROGRESS -> TESTED -> SHIPPED`. None of these prototype features are marked SHIPPED.

| Feature | Current status | Existing implementation | Missing functionality | Priority | Main engine | Acceptance test |
| --- | --- | --- | --- | --- | --- | --- |
| Core PDF utilities | TESTED | FastAPI + pypdf + bounded worker | Larger fidelity/security corpus and public-release controls | Existing | pypdf | Existing unit, mutation, browser and Compose checks remain green |
| DOCX-to-PDF | TESTED | Private Gotenberg route + unit/smoke/browser tests | Broader Office fidelity corpus and immutable image provenance | Existing | Gotenberg/LibreOffice | Existing DOCX text/page smoke remains green |
| PPTX-to-PDF | TESTED | Gotenberg can convert PPTX, but PDF Studio has no route/UI/tests | OOXML validation, endpoint, UI, worker route, real smoke/E2E | P0 | Gotenberg/LibreOffice | Synthetic PPTX converts to PDF, expected slide text and page count verified, result chains into another tool |
| XLSX-to-PDF | PLANNED | Upstream engine capability only | Format validation, API/UI, fidelity tests | Next Stage B | Gotenberg/LibreOffice | Synthetic workbook + tables/charts corpus |
| HTML-to-PDF | PLANNED | Upstream engine capability only | Safe controlled HTML ingestion; no arbitrary remote fetch | Stage B | Gotenberg/Chromium | Local-content-only fixtures; SSRF tests |
| PDF.js workspace | PLANNED | No PDF.js assets in product | Viewer, thumbnails, zoom, find, text layer, cleanup, keyboard/accessibility | Stage C | PDF.js | Synthetic mixed-size/rotated/searchable PDFs in browser |
| Native existing-text modification | PLANNED | None | Real content-edit engine/license decision | Stage C research | Undecided | Extracted underlying text changes; no hidden overlay substitute |
| OCR | PLANNED | None | OCRmyPDF integration and multilingual corpus | Stage D | OCRmyPDF | Searchable output with measured multilingual accuracy |
| Secure redaction | PLANNED | Visual crop is explicitly not redaction | Content-removing implementation + forensic checks | Stage D | Undecided | Text/object recovery checks fail to recover redacted data |
| Certificate signature | PLANNED | Password protection only | PKI signing/validation | Stage D | pyHanko candidate | Independent cryptographic validation succeeds |

## C. Code quality and security audit

### Existing strengths

- Raw request bytes are bounded before multipart parsing, including chunked bodies and dishonest `Content-Length`.
- Per-document and combined byte limits, page limits, processing slots, wall timeout and Linux child limits are present.
- Compose keeps the worker and Gotenberg off public host ports; `processing` is an internal network.
- Worker and Gotenberg roots are read-only with bounded tmpfs/resources and dropped capabilities.
- Private HTTP adapters disable environment proxies and redirects.
- The Gotenberg URL is operator configuration, not a user-supplied request field; the adapter also rejects public converter hostnames and accepts only the service name/localhost/private literal addresses.
- PDF outputs are checked for MIME/signature, strict readability, page count and size before returning them.
- Browser results can be chained without server-side document history.

### Gaps to address in this milestone

1. `app/gotenberg.py` is DOCX-specific. PPTX must reuse one bounded Office abstraction rather than duplicate HTTP code.
2. Office validation currently checks ZIP magic, required DOCX parts, entry count and total declared expanded size. The shared validator should also verify the OOXML main content type, reject suspicious archive paths, bound individual entries/compression expansion, and require the PPTX package part `ppt/presentation.xml`.
3. File extensions in `app/main.py` and the browser are only a first filter. Server validation must reject a renamed ZIP/non-PPTX archive.
4. Converter-unavailable errors are sanitized, but worker serialization currently loses error categories. The public endpoint should distinguish temporary service unavailability (503) from bad input/conversion rejection (422) without leaking converter internals.
5. `compose.yaml` uses rolling `gotenberg/gotenberg:9`, creating supply-chain/reproducibility drift.
6. Several docs still say 14 tools or that worker/Gotenberg integration is only planned; they no longer match source.
7. `worker_service.py` calls all bounded inputs “PDF” even though it already transports DOCX.
8. Conversion fidelity is currently one minimal DOCX fixture. PPTX needs a real private-Gotenberg smoke test that inspects extracted text/page count, plus browser download/reopen/reuse coverage.

### Remaining risks after this milestone

- Office documents can reference external resources. Gotenberg/LibreOffice has had SSRF advisories; the private no-egress processing network is a critical control and must remain.
- Container isolation shares the host kernel and is not a perfect hostile-document sandbox.
- Font availability, charts, animations, embedded media, SmartArt, complex scripts and presentation theme fidelity require a larger corpus.
- There is no reverse proxy TLS/auth/per-user quota layer for public production.
- Temporary multipart spooling exists by design; production retention/deletion policy still needs owner approval.
- Password-bearing Office conversion is not introduced here; do not log document content or passwords.

## D. Existing CI audit

The authoritative workflow is `.github/workflows/ci.yml`. The latest `main` run before this branch was **CI #50 / run 43712747983**, commit `5fc186c8817bc7719b543e029e7ee0b20386e91f`, and completed successfully.

Required jobs are:

- `quality`: Ruff, Python compile, JavaScript syntax.
- `tests`: Python 3.11/3.12/3.13 matrix, branch coverage >=85%, JUnit/coverage evidence and collection guard.
- `package`: build wheel/sdist and installed-app smoke.
- `dependencies`: `pip-audit` and CycloneDX artifact.
- `container`: image build, non-root runtime and static asset checks.
- `integration`: isolated Compose worker, Chromium journey, Gotenberg smoke.
- `guardrails`: validates the CI contract itself.
- `mutations`: proves tests reject known regressions.
- `CI required`: fails if any required job fails/skips/cancels.

This milestone may add assertions and smoke coverage. It must not lower coverage, remove critical test IDs, skip failing checks, add advisory exclusions or weaken the aggregate gate.

## E. Licensing audit

- PDF Studio's original code has **no approved project-wide software license**. That remains an owner/legal decision and this PR must not choose one.
- Gotenberg project code is MIT, but its full image includes separately licensed runtime components such as LibreOffice, Chromium, fonts, Debian packages, `lok` and `litho). Container/SBOM and redistribution obligations still need review before production distribution.
- Mozilla PDF.js is Apache-2.0. A future bundled distribution must retain required license/attribution material and audit its shipped third-party assets/sandbox licenses.
- No AGPL, noncommercial, source-available or paid SDK dependency is added by the PPTX milestone.
- LibreOffice is consumed inside the upstream Gotenberg image; no LibreOffice source is copied into this repository.

## Implementation gap report

The PPTX slice is now implemented and TESTED in [CI #51](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43745076741): shared Office adapter, package validation, `POST /api/tools/pptx-to-pdf`, existing-worker routing, current no-build UI, unit/integration/browser tests and immutable Gotenberg 9.5.1 pin `sha256:a0f596c2aeee6391c24ccf2953737971f13976b14d4240525a447f209185e2c8`. It is not marked SHIPPED; broader fidelity and production controls remain. No parallel backend, frontend rewrite, account/AI/billing work, or native-text-editing claim is in scope.
