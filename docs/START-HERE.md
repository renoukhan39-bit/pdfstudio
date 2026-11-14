# START HERE — A Complete Onboarding Guide

**Welcome to PDF Studio. You do not need to read any previous chat.** This page explains what the project is, what is real today and what to do next.

## Five-minute understanding
- **Why:** Consumers and organizations often use separate applications for conversion, editing, signing, OCR, and AI. We aim to unify them.
- **Who:** Students, teachers, office workers, small businesses, document-heavy teams, developers and later enterprise customers.
- **Product:** A competitive, privacy-focused PDF website and eventual multi-platform software system.
- **Commercial goal:** Build an independent, sustainable competitor to Adobe Acrobat, iLovePDF, Sejda and Smallpdf.
- **Technical principle:** One modular monorepo and one branded UX; compose best-fit PDF engines instead of merging multiple entire applications.
- **Truth about current status:** An **eleven-tool working prototype** now exists with a FastAPI backend and a basic frontend; it is not security-hardened or deployed. See [Prototype](PROTOTYPE.md) and [Implementation Status](IMPLEMENTATION-STATUS.md).

## Where decisions are written
1. [Product Vision](PRODUCT-VISION.md) — positioning, audience, principles and success criteria.
2. [Competitive Benchmarks](COMPETITIVE-BENCHMARKS.md) — what we are measuring ourselves against.
3. [Feature Inventory](FEATURE-INVENTORY.md) — the intended feature set (all proposed unless tested).
4. [Architecture](ARCHITECTURE.md) — services, adapters, editor, storage and trust boundaries.
5. [Reuse vs Build](REUSE-VS-BUILD.md) — candidate codebases and engines.
6. [Licensing](LICENSING-AND-DEPENDENCIES.md) — essential before importing code.
7. [Roadmap](ROADMAP.md), [Backlog](IMPLEMENTATION-BACKLOG.md) — implementation sequence.
8. [Quality](QUALITY-AND-TESTING.md), [Operations](OPERATIONS-AND-SECURITY.md) — readiness.
9. [Codex Playbook](CODEX-PLAYBOOK.md) — safe, credit-efficient automated development.

## Non-negotiables
- Never call a visual text replacement “native text editing.”
- Never call whiteout secure redaction.
- No product completeness claims without real tests.
- No unreviewed incompatible copyleft/noncommercial dependencies in a proprietary product.
- No user PDFs in public issues, examples, fixtures or AI prompts.
- Reuse existing validated engines before creating replacements.
- Make uploading and processing safe, simple and transparent.

## Initial architecture hypothesis
A React/TypeScript web application, service adapter API, Gotenberg or other tested processing backend, OCRmyPDF for OCR, Docling for structured extraction, a proven advanced editor SDK if commercially viable, and isolated queued workers. The UI starter may be PDFClear; Folio is an editor reference. **These are candidates, not decisions to download and combine indiscriminately.**

## First contributor actions
If you are an architect: run a focused evaluation of the PDFClear starter and license/compliance list.
If you are a backend engineer: build a Gotenberg adapter proof of concept with synthetic fixtures.
If you are an editor specialist: test native-text editing SDKs with font, layout and extraction checks.
If you are a QA engineer: define canonical fixtures and acceptance tests.
If you are a designer: prototype the unified upload/editor/workspace flow.
If you use Codex: follow [AGENTS.md](../AGENTS.md) and [Codex Playbook](CODEX-PLAYBOOK.md).

**The install/run/test commands are documented** in [Prototype](PROTOTYPE.md) and the [CI failure-recovery guide](CI.md). The previous prototype CI passed; the expanded contributor workflow adds matrix tests, coverage, lint, package/container checks and dependency scanning. See [Implementation Status](IMPLEMENTATION-STATUS.md) for verified evidence and outstanding checks.

