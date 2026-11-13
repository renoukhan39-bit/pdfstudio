# Architecture Decision Register

Decision statuses: **PROPOSED** = discussed but not final; **ACCEPTED** = explicitly authorized and documented; **SUPERSEDED** = replaced with a newer ADR.

## ADR-0001 — Modular single-repository product (PROPOSED)
**Context:** Multiple open-source PDF applications overlap and use different stacks. Directly merging whole apps risks incompatible dependencies, licenses and fragmented UX.

**Proposal:** Use one product monorepo with an engine-agnostic adapter layer, browser editor and isolated backend tools. Integrate selected compatible modules, not full codebases. Product owns original brand and orchestration, upstream retains ownership of reused components.

**Acceptance criteria:** Reproducible build, clear module contracts, per-engine license register, tests proving at least one end-to-end tool.

## ADR-0002 — Reuse-first backend and quality gate (PROPOSED)
**Proposal:** Evaluate Gotenberg as primary server-side PDF processing HTTP service; bring qpdf/PDFBox/pdfcpu only for gaps proven by tests. Use OCRmyPDF/Docling for specialist OCR/layout operations. Never add multiple engines for the same feature without benchmark evidence.

**Open questions:** Gotenberg API/version suitability, transitive license obligations, sandboxing, cost/performance, PDF fidelity.

## ADR-0003 — Native text editing decision (OPEN)
**Problem:** PDF.js/pdf-lib and canvas overlays do not provide arbitrary high-fidelity modification of existing PDF text. This is a competitive blocker.

**Options:** License advanced PDF content-editor SDK (e.g. Nutrient/Apryse), use an approved commercially licensed alternative, or fund substantial proprietary engine R&D.

**Decision gate:** Proof of edited underlying text via extraction/object inspection, typography/layout benchmarks, licensed commercial deployment, pricing and vendor lock-in. Do not ship overlays under a “native editing” label.

## ADR-0004 — Privacy-first processing (PROPOSED)
**Proposal:** Offer browser-local processing for eligible tasks, isolate server work, make AI/external processors opt-in, use short-lived storage and support automatic deletion.

**Open questions:** Precise retention times, supported regions, storage vendor, regulatory needs, cost and logging.

## ADR-0005 — Product licensing (OPEN)
The repository is public but original source-code licensing has not been chosen. Evaluate proprietary, open-source or dual-license model; align contributor policy and code imports. Do not assume public access grants rights to redistribute.

## How to add ADRs
Record date, context, decision alternatives, exact chosen option, affected licenses, security, cost, performance, owner approval, implementation consequences and reversal plan. Avoid recording unapproved proposals as facts.

## ADR-0006 — Minimal Python merge prototype (IMPLEMENTED FOR DEVELOPMENT ONLY)

**Context:** The initial repository was documents-only. Building every tool or importing PDFClear without due diligence would be expensive and risky.

**Implementation:** A small FastAPI API + HTML/JS frontend with a `pypdf` merge operation, tests and a Dockerfile. No persistent document storage is intentionally used.

**Not a final product architecture decision:** The Python PDF parser operates inside the API process, without a hostile-file sandbox. Do **not** deploy publicly. PDFClear and Gotenberg remain candidates pending audit; high-fidelity native editing is still undecided.

**Evidence:** `tests/test_merge.py`, `docs/IMPLEMENTATION-STATUS.md`, `docs/PROTOTYPE.md`. Dependency license is BSD-3-Clause for pypdf and MIT for FastAPI (version-specific recheck required).
