# Implementation Status and Blockers

**Updated:** 2026-11-15. This file records what is implemented and verified; it is not the long-term feature wishlist.

## Current verified state

PDF Studio has **16 tested prototype tools**: 14 pypdf-based PDF operations plus DOCX-to-PDF (CV-02) and PPTX-to-PDF (CV-06). The Office conversions use the existing FastAPI -> private worker -> bounded child -> Gotenberg/LibreOffice path; there is no parallel conversion backend.

The PPTX milestone was validated in [GitHub Actions CI #51](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43745076741). That run passed lint/syntax, Python 3.11/3.12/3.13 tests, package/install smoke, dependency audit, container smoke, CI-contract guardrails, mutation probes, Compose isolation, Chromium end-to-end testing, the existing DOCX smoke and the new PPTX smoke. Python 3.12 reported **80 passed, 76 subtests and 91.73% branch-inclusive coverage** with the unchanged 85% minimum.

The exact tested Gotenberg image is **9.5.1**, repository digest `sha256:a0f596c2aeee6391c24ccf2953737971f13976b14d4240525a447f209185e2c8`. Compose pins `gotenberg/gotenberg:9.5.1@sha256:a0f596c2aeee6391c24ccf2953737971f13976b14d4240525a447f209185e2c8`; rollback is a one-line image-reference revert to the previous tested digest followed by the same DOCX/PPTX integration suite.

## Implemented architecture

```text
Browser
  -> FastAPI routes + raw upload/concurrency limits
  -> format-aware input validation
  -> trusted private worker HTTP service
  -> bounded child process
  -> pypdf toolkit OR trusted Gotenberg Office adapter
  -> strict output type/signature/structure/page/size validation
  -> browser download
  -> optional PDF result chaining into another tool
```

Compose keeps the worker and Gotenberg off host ports on the internal `processing` network. CI verifies non-root identity, read-only code filesystem and blocked public egress. Private HTTP adapters disable environment proxies and redirects. The Gotenberg URL is operator configuration only; users cannot supply converter URLs.

## Feature status

| Feature | Status | Evidence / limitation |
| --- | --- | --- |
| 14 core PDF operations | TESTED | Unit/mutation/browser checks; still a prototype, not a public commercial release |
| DOCX-to-PDF | TESTED | Real private Gotenberg conversion, extracted text verified |
| PPTX-to-PDF | TESTED | Real private Gotenberg conversion, one synthetic slide text/page count verified, browser result chained into Extract |
| XLSX-to-PDF | PLANNED | Next smallest Stage B slice |
| Controlled HTML-to-PDF | PLANNED | Must not become an arbitrary URL-fetch/SSRF surface |
| PDF.js workspace | PLANNED | Stage C; version 6.5.438 selected, not yet bundled |
| Native existing-PDF text editing | PLANNED | Separate engine/license research; overlays are not an acceptable substitute |
| OCR / secure redaction / certificate signatures | PLANNED | Stage D specialist work |

No feature is marked SHIPPED by this milestone.

## PPTX milestone controls

- One PPTX, maximum 8 MiB, through the existing upload/worker limits.
- Server validates a bounded OOXML ZIP package, required PowerPoint part and exact main content type; a renamed ZIP/DOCX is rejected.
- Archive entry count, declared expansion, per-entry expansion and compression ratio are bounded; unsafe/duplicate paths and encrypted OOXML archives are rejected.
- Converter calls use the fixed Gotenberg LibreOffice route, no environment proxy, no redirect and no user-provided URL.
- Gotenberg 5xx/network failures become sanitized temporary-unavailable responses; malformed inputs/conversion rejections remain 422-class errors.
- Output must be PDF MIME, start with the PDF signature, parse strictly, be unencrypted, contain 1-200 pages and stay within 40 MiB.
- The browser supports upload -> convert -> download -> reopen/validate -> use result in another tool, including mobile-width smoke coverage.

## Licensing and supply-chain state

Original PDF Studio code still has **no owner-approved project-wide license**; public visibility does not grant reuse rights. This PR does not choose a product license.

Gotenberg project code is MIT, but its image contains separately licensed LibreOffice, Chromium, Debian packages, fonts, lok/litho and other runtime material. The pinned image and future SBOM/container scan need production redistribution review. PDF.js 6.5.438 is Apache-2.0 and is selected only for a future Stage C integration; its distributed third-party license assets must be retained and reviewed when bundled. No AGPL, noncommercial or paid SDK was added here.

## Remaining production blockers

1. Owner decision on original-code license/contribution terms.
2. Production TLS, authentication, per-user/rate limits and cross-replica quotas.
3. Explicit retention/deletion/privacy policy and operational monitoring.
4. Broader hostile-document sandbox/container hardening and container-image vulnerability/SBOM review.
5. Real Office fidelity corpus covering fonts, themes, charts, tables, multilingual text, embedded media and malformed documents.
6. PDF fidelity/accessibility corpus for existing pypdf tools.
7. Native text-editing engine/license decision.
8. Stage D OCR, secure redaction and signing security designs.

## Next smallest task

Implement **XLSX-to-PDF** through the same bounded Office adapter in one focused PR. Acceptance: validate the correct OOXML workbook content type/parts, reject renamed ZIP/DOCX/PPTX inputs and ZIP abuse, reuse the worker/Gotenberg path, add a synthetic workbook smoke with expected cell text/page count, add browser result chaining, preserve DOCX/PPTX regressions, and keep every current CI gate green.
