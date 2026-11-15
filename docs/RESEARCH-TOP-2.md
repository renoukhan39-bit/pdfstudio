# Research: Top Two Primary Repositories

**Reviewed:** 2026-11-15  
**Decision:** Keep exactly two primary upstream repositories: **Gotenberg** for server-side conversion/processing and **Mozilla PDF.js** for the Stage C browser viewer/workspace foundation.

This document records a technical selection, not a blanket license approval for every bundled component.

## 1. Gotenberg

- **Repository:** https://github.com/gotenberg/gotenberg
- **Selected release:** `v9.5.1`
- **Tag commit:** `2a025609d36eb7a970c31397e652ee439a7214fe`
- **Release date:** 2026-11-14
- **Project license:** MIT; preserve the copyright/license notice when redistributing project code or substantial portions.
- **Role in PDF Studio:** private server-side Office/document conversion. It is already integrated for DOCX-to-PDF.

### Why it remains the strongest primary conversion choice

Gotenberg 9 exposes one stable HTTP boundary for the converters we need and its LibreOffice route supports Word, Excel and PowerPoint, including `.docx`, `.xlsx` and `.pptx`. The existing product already has a tested adapter, private worker topology and real DOCX conversion, so extending this path has substantially lower integration risk than adding another converter service.

Official Gotenberg guidance says the `9` tag tracks the latest 9.x release and recommends an exact production release pin. PDF Studio must therefore move away from the rolling `:9` tag. For this PR, CI will first resolve and exercise the exact `9.5.1` image; an immutable digest is accepted only after that image passes both existing DOCX and new PPTX conversion tests.

### Upstream/runtime dependencies that matter

Gotenberg 9's release notes identify these material runtime components: Debian 13, Chromium 156 (146 on ppc64le at the 9.0.0 release), LibreOffice 26.8 from Debian backports, Go 1.27, `lok` for supervised LibreOfficeKit and `litho` as the PDF engine. `v9.5.1` updates litho to `v0.0.12`. The actual container also includes fonts/system packages whose licenses and vulnerabilities must be taken from the exact tested image/SBOM rather than inferred from the Gotenberg MIT license.

### Reuse

Reuse only the service API and container:
- `POST /forms/libreoffice/convert` for one locally uploaded Office document.
- LibreOffice conversion for DOCX/PPTX now; XLSX after its own validation/fidelity slice.
- Existing PDF Studio timeout, byte/page/output validation, private networking and worker controls.

### Do not import/use

- Do not copy the Gotenberg Go server into PDF Studio.
- Do not expose Gotenberg publicly.
- Do not accept user-supplied Gotenberg URLs.
- Do not use `downloadFrom`, arbitrary URL conversion, webhooks or remote document retrieval for Office conversion.
- Do not duplicate pypdf operations already working unless a measured fidelity gap justifies it.

### Security findings

Gotenberg's 2026 advisory history includes SSRF in LibreOffice processing, multipart body-limit ordering and outbound-policy bypasses. Version 9 incorporates the late-v8 security work and changed substantial internals, but the lesson remains: treat Office input as hostile, upgrade deliberately, and do not rely on application-level URL filtering alone.

PDF Studio's defense is architectural: only uploaded bytes are sent; the Gotenberg URL is trusted operator configuration; environment proxies and redirects are disabled by the adapter; the worker/Gotenberg network is private and internal; the Gotenberg route is not published; input/output sizes and time are bounded.

### Performance/resource risks

LibreOffice startup/rendering and complex presentations can consume substantial CPU/RAM. Fonts and charts can change fidelity. ZIP-based OOXML can expand far beyond upload size. Therefore keep the current 8 MiB input, 32 MiB OOXML expansion budget, 40 MiB PDF output, 200-page output and container CPU/RAM limits until benchmarks justify a reviewed change.

### Fallback

If a Gotenberg patch regresses Office conversion, roll back the exact image reference to the previously tested immutable image while keeping the PDF Studio API contract. Do not silently route documents to a third-party hosted converter.

### Integration complexity

**Low-medium for PPTX** because the network/service path already exists. The work is format-aware OOXML validation, shared adapter cleanup, API/UI registration and tests—not a new service.

## 2. Mozilla PDF.js

- **Repository:** https://github.com/mozilla/pdf.js
- **Selected release:** `v6.5.438`
- **Tag commit:** `0a4153349dc473ba950fc17941c5ca7eda43c1de`
- **Release date:** 2026-11-01
- **Project license:** Apache-2.0.
- **Official modern distribution artifact:** `pdfjs-6.5.438-dist.zip`
- **Artifact SHA-256:** `fcbe9ba21d9911843e3502adc178a7f549a524a4055f887bedc942e5490c6ba1`
- **Role in PDF Studio:** Stage C browser PDF rendering/workspace foundation. It is not implemented in this PPTX PR.

### Why it remains the strongest viewer choice

PDF.js is Mozilla's general-purpose web PDF parsing/rendering platform and provides mature display and viewer layers. The selected release includes viewer, accessibility, annotation-rendering/editing, performance and text/search-related fixes. It directly matches PDF Studio's next viewer requirements without forcing a React migration or a server-side renderer.

### Reuse

For the initial Stage C slice, reuse audited production distribution assets for:
- page rendering;
- thumbnails;
- zoom and page navigation;
- text layer/selection;
- find/search;
- rotated and mixed-size page display;
- keyboard/accessibility behavior already implemented by viewer components;
- dedicated worker execution.

Self-host the assets from PDF Studio so browser-local preview bytes are not sent to a CDN or third party.

### Do not import/use

- Do not copy the entire PDF.js development repository/toolchain into PDF Studio.
- Do not use a CDN for production viewer assets.
- Do not claim PDF.js provides arbitrary high-fidelity rewriting of existing PDF text.
- Do not enable unrelated scripting/editor functionality until the exact distribution assets, CSP needs and persistence semantics are reviewed.
- Do not replace the existing PDF Studio brand/workspace with the stock viewer UI wholesale.

### Licensing/dependency obligations

Apache-2.0 requires distribution of the license and preservation of applicable notices; modified files need change notices. The repository has no root `NOTICE` at this tag, but the release includes separately licensed third-party components/assets (the 6.5 release notes specifically mention shipping QuickJS license files with the sandbox). Before bundling, inventory the exact distribution ZIP, retain its license files, and include applicable third-party notices.

The upstream source development dependency graph is not a reason to import its full build system. Prefer the official verified distribution for the first spike, or introduce a minimal build step only if a concrete integration requirement demands it.

### Security/performance risks

PDF parsing/rendering happens in the browser and can consume large amounts of memory/CPU for complex pages. Worker/version mismatches can break rendering. Object URLs and document/worker instances must be destroyed on file replacement. CSP and scripting behavior require review. Keep assets same-origin and test malformed PDFs, cancellation and cleanup.

### Fallback

The existing download/tool-chaining flow remains functional even if the viewer fails to initialize. Stage C should treat preview as a replaceable UI component, not make core server processing depend on PDF.js.

### Integration complexity

**Medium.** The current frontend is intentionally no-build HTML/CSS/JS. A small same-origin ES-module integration may be sufficient, but the official viewer has multiple assets (worker, maps/fonts/localization/UI). A minimal build/copy step is justified only if it materially reduces safe asset management; a React/Next.js rewrite is not justified.

## Why not choose a different primary pair

- `pdf-lib`, Konva and pdfme may become targeted Stage C helpers, but none replaces PDF.js as the renderer or Gotenberg as the already-integrated Office converter.
- qpdf/PDFBox/pdfcpu would duplicate working pypdf/Gotenberg capabilities without evidence of a present gap.
- OCRmyPDF and pyHanko are strong later Stage D specialists, not primary engines for this milestone.
- PDFClear/Folio are useful study references but importing an entire application would conflict with the working PDF Studio architecture.
- PyMuPDF/Sejda/ONLYOFFICE and other restrictive/commercially nuanced candidates are not introduced without owner/license approval.

## Integration diagrams

### Implemented/current conversion path

```text
Browser
  -> PDF Studio FastAPI
  -> validation + upload limits
  -> private worker
  -> bounded child
  -> PDF Studio Gotenberg adapter
  -> internal Gotenberg 9 / LibreOffice
  -> strict PDF validation
  -> browser download / next-tool chaining
```

### Planned Stage C viewer path

```text
Browser PDF Studio workspace
  |-- same-origin, version-pinned PDF.js display/viewer assets
  |-- same-origin PDF.js worker
  |-- current browser-held PDF Blob/Object URL
  |
  +-> thumbnails / canvas pages / text layer / find / navigation
  +-> existing PDF Studio server tools only when user invokes a server operation
```

No preview document needs to be sent to Mozilla or another third party.

## Existing code paths affected

PPTX milestone:
- `app/gotenberg.py`
- `app/main.py`
- `app/worker.py`
- `app/worker_service.py` only if error typing/wording is improved
- `app/toolkit.py`
- `app/static/app.js`
- `app/static/index.html`
- `compose.yaml`
- `tests/test_gotenberg.py`
- `scripts/gotenberg_smoke.py` remains DOCX regression evidence
- new PPTX smoke coverage
- `scripts/browser_smoke.py`
- CI/docs

PDF.js later:
- new locally served viewer assets/module under the existing frontend or a narrowly justified asset-build step;
- CSP/static package-data updates;
- browser tests for rendering/search/navigation/cleanup.

## Feature-by-feature acceptance criteria

| Feature | Engine | Test criteria |
| --- | --- | --- |
| DOCX-to-PDF regression | Gotenberg | Existing synthetic DOCX converts, expected text extracted, 1 sensible page, API/worker path unchanged |
| PPTX package acceptance | PDF Studio + Gotenberg | Correct OOXML content type + `ppt/presentation.xml`; renamed/non-PPTX ZIP rejected |
| ZIP abuse bounds | PDF Studio | input >8 MiB, too many entries, excessive declared expansion/suspicious expansion ratio rejected before Gotenberg |
| PPTX conversion output | Gotenberg | HTTP PDF only; signature, strict parse, 1-200 pages and <=40 MiB |
| Gotenberg outage | Adapter/worker | sanitized temporary-unavailable response; no fallback to arbitrary/local external service |
| Browser PPTX flow | Current UI | upload -> convert -> download -> reopen -> expected text/page count -> reuse result in another existing tool |
| Viewer render | PDF.js later | synthetic PDF canvases match page count/sizes/rotation; no external requests |
| Thumbnails/navigation | PDF.js later | thumbnails and keyboard page navigation stay synchronized |
| Zoom | PDF.js later | bounded zoom preserves responsiveness and rendering |
| Search/text selection | PDF.js later | known synthetic text is selectable and found; highlights mapped to correct pages |
| Resource cleanup | PDF.js later | old object URLs/doc/worker resources released on replacement/navigation |
| Accessibility | PDF.js later | keyboard controls/focus labels and automated browser accessibility checks pass |

## Image provenance and rollback rule

The currently deployed Compose tag `gotenberg/gotenberg:9` is intentionally **not** accepted as an immutable production pin. The branch will first test `9.5.1`, resolve its registry digest in CI, and only then update Compose to the exact verified tag+digest. The PR must record that digest and keep rollback instructions to the prior tested reference. A registry digest found only in third-party mirrors is not sufficient evidence.
