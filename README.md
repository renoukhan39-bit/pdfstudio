# PDF Studio

> **Project status: planning / architecture.** This repository is currently a documentation-first blueprint, **not yet a working PDF application**. No external projects or services described below are integrated merely because they are listed here.

**Mission:** Build an independently branded, reliable, privacy-conscious, affordable, all-in-one PDF platform capable of competing on quality with Adobe Acrobat, iLovePDF, Sejda, Smallpdf and other leading PDF products.

**Product promise:** One upload, one workspace, every major PDF workflow—from editing existing text and filling forms to OCR, conversion, organization, signing, secure redaction, automation and AI-assisted document work.

**Guiding strategy:** **Reuse proven components, don't rebuild mature engines.** Own the original product experience and integration architecture; respect the copyright and licenses of all third-party software.

## Start here

| I am... | Read this first |
| --- | --- |
| New developer or reviewer | [Start Here](docs/START-HERE.md) and [Contributing](CONTRIBUTING.md) |
| Product designer | [Product Vision](docs/PRODUCT-VISION.md) and [UX Blueprint](docs/UX-BLUEPRINT.md) |
| Engineer | [Architecture](docs/ARCHITECTURE.md) and [Reuse vs Build](docs/REUSE-VS-BUILD.md) |
| PDF specialist | [Feature Inventory](docs/FEATURE-INVENTORY.md) and [Quality Plan](docs/QUALITY-AND-TESTING.md) |
| License reviewer | [Licensing and Dependencies](docs/LICENSING-AND-DEPENDENCIES.md) |
| Project manager | [Roadmap](docs/ROADMAP.md) and [Implementation Backlog](docs/IMPLEMENTATION-BACKLOG.md) |
| Codex contributor | [AGENTS.md](AGENTS.md) and [Codex Playbook](docs/CODEX-PLAYBOOK.md) |

## What we intend to build

- **Professional PDF editor:** genuinely modify existing text (not merely paint over it), add text/images/shapes/links, annotate, work with forms and signatures, edit pages, undo/redo.
- **Everyday PDF toolkit:** merge, split, compress, convert, extract, rotate, crop, reorder, repair, watermark, add page numbers, protect, redact, OCR.
- **Power-user features:** bookmarks, Bates numbers, metadata, N-up, deskew, alternate/mix, split by bookmarks/text/size, bulk jobs, PDF/A, accessibility workflows.
- **Document intelligence:** PDF chat, summary, translation, structured extraction, table extraction and document classification (with accuracy and privacy guardrails).
- **Long-term platform:** user workspace, APIs, integrations, optional offline processing, collaboration, desktop/mobile experiences, enterprise administration.

The [Feature Inventory](docs/FEATURE-INVENTORY.md) records goals and priorities. **Listed features are not implemented until marked complete with tests.**

## Proposed technical direction (not a final selection)

| Layer | Candidates | Why |
| --- | --- | --- |
| Web base | [PDFClear](https://github.com/aliansari22/pdfclear), subject to audit | UI and toolkit starting point |
| Editor UI references | [Folio](https://github.com/doktorigi/folio), [PDF.js](https://github.com/mozilla/pdf.js), [pdf-lib](https://github.com/Hopding/pdf-lib), [Konva](https://github.com/konvajs/konva) | Rendering, annotations and form operations |
| Advanced PDF editing | Licensed native-content editor SDK, or dedicated R&D | True text editing and fidelity are hard |
| PDF processing | [Gotenberg](https://github.com/gotenberg/gotenberg); [qpdf](https://github.com/qpdf/qpdf) and other specialist engines as needed | Avoid implementing converters from scratch |
| OCR | [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | Searchable scanned PDFs |
| Intelligent extraction | [Docling](https://github.com/docling-project/docling) | Layout and structured extraction |
| PDF templates | [pdfme](https://github.com/pdfme/pdfme) | Visual templates and generation |
| Digital signatures | [pyHanko](https://github.com/MatthiasValvekens/pyHanko) | Certificate signatures and validation |
| Async jobs | [BullMQ](https://github.com/taskforcesh/bullmq) | Durable processing jobs |

**No vendor choice is approved by this README.** Validate APIs, versions, source quality, commercial terms, transitive licenses, deployment cost and actual outputs first. Do not combine entire applications blindly.

## Current state and first milestone

The repository began as a README-only repository. This documentation establishes shared direction; it does not add a working application. The first coding milestone is **a reproducible web shell plus one end-to-end tested PDF tool**, after a license, architecture and dependency audit. See [Roadmap](docs/ROADMAP.md).

## What makes this different

1. **Editor accuracy first:** don't call overlays “native PDF text editing.”
2. **Continuous workflow:** operate on a document repeatedly without reuploading after every tool.
3. **Privacy by design:** local-first where feasible; explicit consent for server processing and AI.
4. **Testable quality:** compare output integrity across real PDFs, not just successful API calls.
5. **Credit-efficient delivery:** integrate mature engines, keep Codex tasks small, verify every change.
6. **Transparent feature claims:** planned, in progress, tested, and shipped are different states.

## Contribution and governance

Read [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), [Code of Conduct](CODE_OF_CONDUCT.md) and [Codex guidance](AGENTS.md). Propose engine or license decisions before introducing major dependencies. Keep secrets and real user documents out of commits.

**Ownership / licensing:** This is intended as the owner's independent brand and original product; reused open-source code remains under its original owners' licenses. No project-wide license has been selected for new original code yet—**public visibility alone does not grant reuse rights**. Contributors should not assume this is an open-source software release until a license is explicitly chosen. The documentation is provided for planning and contribution discussion.

## Documentation index

[Start Here](docs/START-HERE.md) · [Vision](docs/PRODUCT-VISION.md) · [Competitive Benchmarks](docs/COMPETITIVE-BENCHMARKS.md) · [Feature Inventory](docs/FEATURE-INVENTORY.md) · [Architecture](docs/ARCHITECTURE.md) · [Reuse vs Build](docs/REUSE-VS-BUILD.md) · [Licenses](docs/LICENSING-AND-DEPENDENCIES.md) · [Roadmap](docs/ROADMAP.md) · [Backlog](docs/IMPLEMENTATION-BACKLOG.md) · [UX](docs/UX-BLUEPRINT.md) · [Quality](docs/QUALITY-AND-TESTING.md) · [API/Data](docs/API-AND-DATA-CONTRACTS.md) · [Operations](docs/OPERATIONS-AND-SECURITY.md) · [Codex](docs/CODEX-PLAYBOOK.md) · [Research Links](docs/RESEARCH-REFERENCES.md) · [Decisions](docs/DECISIONS.md).
