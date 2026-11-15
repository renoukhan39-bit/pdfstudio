> **Active instruction (2026-11-14): Implement Stages A–D only. Stages E/F are frozen until owner reauthorization.** See [Active Scope](ACTIVE-SCOPE.md).

# PDF Studio — Complete Ordered Implementation Checklist

> **Purpose:** This checklist is the execution sequence, not an assertion of completed features. Check items only after the documented acceptance gate passes. See [Implementation Status](IMPLEMENTATION-STATUS.md), [Feature Inventory](FEATURE-INVENTORY.md), [Architecture](ARCHITECTURE.md) and [Quality](QUALITY-AND-TESTING.md).

## Phase 0 — Governance and a reproducible foundation

- [x] Capture complete project goals, contributor instructions and competitive feature inventory.
- [x] Publish the ordered development checklist and clear prototype status.
- [ ] Choose license for original product code and contribution policy (owner approval).
- [ ] Audit PDFClear, Folio and alternatives for security, build quality, maintenance and commercial licensing.
- [ ] Approve framework/monorepo structure and replaceable engine-adapter contracts.
- [ ] Create a runnable app with verified fresh-install commands and reproducible dependency pins.
- [ ] Create automated tests, CI, PR review policy, dependency scanning and SBOM.
  - Progress 2026-11-14: expanded contributor workflow and [failure guide](CI.md) implemented; remote run and administrator-required branch ruleset still need verification.
- [ ] Set policy for document retention, temporary-file deletion, privacy and hosting.
- [ ] Create PDF test corpus including scans, forms, encryption, fonts and multilingual content.
- [ ] Isolate untrusted PDF processing and enforce strict global upload/compute limits.
  - Progress 2026-11-15: per-request raw-body limit, upload deadline and cleanup tests are implemented. Compose verifies a non-root/read-only private worker with blocked public egress plus CPU/memory/PID/time limits. Cross-replica/global ingress quotas and production auth/rate limits remain open.

## Phase 1 — Working online toolkit

Progress 2026-11-15: the 14 PDF operations plus CV-02 DOCX-to-PDF and CV-06 PPTX-to-PDF have prototype implementations and tests; see [Core Toolkit](CORE-TOOLKIT.md). Checkboxes remain release acceptance gates, not just code-presence markers.

- [ ] Build accessible responsive homepage and discovery/navigation.
- [ ] Build reliable multiple-file upload, ordering, validation and download UX.
- [ ] OP-01 Implement merge PDF, page-order preservation and output checks.
- [ ] Create accurate tool capability registry with status: prototype/tested/shipped.
- [ ] OP-02/03 Split and extract page ranges.
- [ ] OP-04/05 Delete and rearrange document pages.
- [ ] OP-06 Rotate pages, preserving annotations when supported.
- [ ] CV-07/08 PDF to images and images to PDF.
- [ ] CV-12 Compress PDF with quality controls and objective measurements.
- [ ] OP-16/18 Page numbers and text/image watermarks.
- [x] Integrate Gotenberg 9 through a tested private backend adapter for DOCX/PPTX, pinned to a verified 9.5.1 image digest.
- [ ] WF-01 Build continuous workspace and revision persistence/cleanup.
- [ ] Validate security, file-size limits, performance, reliability and user errors.

## Phase 2 — Sejda-grade editor

- [ ] ED-01 PDF viewer, page thumbnails, search, zoom and selection.
- [ ] ED-02 Add/format new text.
- [ ] ED-05/06 Add/replace images and hyperlinks.
- [ ] ED-07/08 Highlights, annotations, notes, shapes and freehand drawing.
- [ ] ED-09/10 Select/move/delete objects, undo/redo and revisions.
- [ ] ED-11/12/13 PDF fields, form editing, form filling and visual signatures.
- [ ] Evaluate professional native-text editing SDKs and commercial licensing.
- [ ] ED-03 Verify genuine changes to underlying PDF text rather than overlays.
- [ ] ED-04/18 Find-and-replace, fonts, reflow and complex script handling.
- [ ] Prove save/reopen correctness on multilingual and complex PDF fixtures.

## Phase 3 — Advanced and professional operations

- [ ] Office → PDF: Word and PowerPoint are TESTED prototypes; Excel and controlled HTML remain.
- [ ] PDF → Office: editable Word, Excel and PowerPoint, fidelity tested.
- [ ] PDF → PNG/JPG/TIFF, text and Markdown.
- [ ] OCRmyPDF integration for searchable scans, deskew and multilingual OCR.
- [ ] Repair PDFs, grayscale, PDF/A and accessibility workflows.
- [ ] Crop, resize, flip, N-up and split double-page scans.
- [ ] Advanced splitting: by bookmark, size, text, page group; alternate/mix.
- [ ] Bates numbering, headers/footers, metadata, bookmarks and image extraction.
- [ ] Secure redaction (remove content, not just whiteout overlays).
- [ ] Password protect and authorized unlock.
- [ ] Flatten, fill and create PDF forms.
- [ ] Digital signatures and verification, distinct from visual e-signatures.
- [ ] Compare PDF versions with clear output and quality validation.

## Phase 4 — AI and automation

- [ ] Integrate and license-check Docling or another document extraction engine.
- [ ] Build PDF chat with grounded source references and hallucination tests.
- [ ] Build summarization and translation with document privacy controls.
- [ ] Implement entity/table extraction and smart document classification/splitting.
- [ ] Add human-reviewed AI redaction suggestions.
- [ ] Build batch queue, worker retries, cancellation and per-job cost caps.
- [ ] Build workflow builder, reusable sequences, schedules and versioned APIs.
- [ ] Add privacy consent, per-user quotas, monitoring and independent quality evaluations.

## Phase 5 — Commercial release and market competition

- [ ] User accounts, roles, private document storage and retention controls.
- [ ] Subscriptions, fair-use limits, billing and cost models.
- [ ] Teams, collaboration, sharing and tenant isolation.
- [ ] Production monitoring, vulnerability scans, support and incident response.
- [ ] Desktop packaging, offline operations and mobile experiences if justified.
- [ ] Accessibility, keyboard, localization and multilingual audits.
- [ ] Load, stress and fidelity benchmarks versus market leaders.
- [ ] Privacy policy, third-party notices, license compliance and security assessment.
- [ ] Staged release, backups, rollback and continuous updates.

## Required blockers and decisions

1. **Original-code license/contribution policy:** repo is public but original code has no approved license. Obtain owner decision before accepting broad third-party contributions.
2. **Native PDF editing engine:** commercial SDK decision or substantial independent R&D. PDF.js, pdf-lib and drawing new text over old text are insufficient.
3. **Imported starter code:** audit PDFClear/Folio before importing; do not blindly combine full repositories or incompatible copyleft/noncommercial projects.
4. **Public deployment safety:** Compose isolates the processing worker/Gotenberg and enforces ingress/body/resource limits, but this is not a perfect hostile-document sandbox. Add production TLS, auth/rate limiting, cross-replica quotas, retention controls, image scanning and abuse controls before broad exposure.
5. **Hosting and policy:** domain, cloud provider, credentials, storage and document deletion/privacy policy are not approved.
6. **Clean dependency validation:** run CI with the pinned releases and review vulnerabilities before deploying.

## Proof required to mark an item complete

Each feature must have: real code, passed tests on synthetic PDFs including edge cases, verified output content and page structure, privacy/security and license review, updated docs and a measured limitation statement. **PROTOTYPE ≠ PRODUCTION READY.** Do not check “entire PDF toolset” just because one engine supports an operation.

## Codex workflow

Pick the next incomplete item, read [AGENTS.md](../AGENTS.md), inspect existing code first, choose existing libraries if compatible, implement the smallest complete vertical slice, run tests, and submit a focused PR with exact evidence. Do not regenerate the application or claim tools are finished without successful output checks.

