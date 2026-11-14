# PDF Studio

> **Project status: early prototype.** The repository now contains an initial runnable web/API implementation of **Merge PDF**. Everything else remains a planned feature unless explicitly tested; no outside application is imported by listing it here.

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

## Current work scope: A–D only

Stage E/F implementation is **on hold**. We are preserving the existing 14-tool prototype and selectively integrating tested public engines. [Active Scope and Upstream Decisions](docs/ACTIVE-SCOPE.md).

DOCX-to-PDF is now available in the prototype interface using an internal Gotenberg 9 service. The Docker Compose CI verifies a real conversion. This is **not yet production-ready**; more complex Office documents need a larger fidelity corpus.

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

## Prototype: get it running

This repository now has a small **FastAPI + pypdf merge tool** and responsive no-build frontend. It is **not production-ready**. It deliberately avoids importing entire third-party PDF apps. See [Detailed prototype instructions](docs/PROTOTYPE.md).

~~~bash
git clone https://github.com/renoukhan39-bit/pdfstudio.git
cd pdfstudio
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
# open http://127.0.0.1:8000
~~~

Run tests: `python -m pytest -q`. **Fifteen PDF tools are now implemented as prototypes:** merge, split, extract, delete, reorder, rotate, compress, edit metadata, extract text, AES-256 protection known-password unlock, page numbers, text watermarks and visual cropping. [Toolkit guide](docs/CORE-TOOLKIT.md). The merge API is `POST /api/tools/merge`; merge 2–10 PDFs, 8 MB each, 200 pages maximum. Raw uploads are limited before multipart parsing. See [CI and contributor checks](docs/CI.md) for matrix tests, coverage, lint, packaging and security scans, and [Implementation Status](docs/IMPLEMENTATION-STATUS.md) for exact verification evidence. **This remains a prototype; production worker isolation is not implemented.**

**Plan before coding more:** [Complete Ordered Checklist](docs/IMPLEMENTATION-CHECKLIST.md) · [Live Implementation Status](docs/IMPLEMENTATION-STATUS.md) · [Known Blockers](docs/IMPLEMENTATION-STATUS.md#blockers-requiring-ownercodex-follow-up).


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

[Implementation Checklist](docs/IMPLEMENTATION-CHECKLIST.md) · [Implementation Status](docs/IMPLEMENTATION-STATUS.md) · [Prototype](docs/PROTOTYPE.md) · [Start Here](docs/START-HERE.md) · [Vision](docs/PRODUCT-VISION.md) · [Competitive Benchmarks](docs/COMPETITIVE-BENCHMARKS.md) · [Feature Inventory](docs/FEATURE-INVENTORY.md) · [Architecture](docs/ARCHITECTURE.md) · [Reuse vs Build](docs/REUSE-VS-BUILD.md) · [Licenses](docs/LICENSING-AND-DEPENDENCIES.md) · [Roadmap](docs/ROADMAP.md) · [Backlog](docs/IMPLEMENTATION-BACKLOG.md) · [UX](docs/UX-BLUEPRINT.md) · [Quality](docs/QUALITY-AND-TESTING.md) · [API/Data](docs/API-AND-DATA-CONTRACTS.md) · [Operations](docs/OPERATIONS-AND-SECURITY.md) · [Codex](docs/CODEX-PLAYBOOK.md) · [Research Links](docs/RESEARCH-REFERENCES.md) · [Decisions](docs/DECISIONS.md).

