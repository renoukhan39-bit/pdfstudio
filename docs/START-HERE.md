# START HERE — A Complete Onboarding Guide

**Welcome to PDF Studio. You do not need to read any previous chat.** This page explains what the project is, what is real today and what to do next.

## Five-minute understanding
- **Why:** Consumers and organizations often use separate applications for conversion, editing, signing, OCR, and AI. We aim to unify them.
- **Who:** Students, teachers, office workers, small businesses, document-heavy teams, developers and later enterprise customers.
- **Product:** A competitive, privacy-focused PDF website and eventual multi-platform software system.
- **Commercial goal:** Build an independent, sustainable competitor to Adobe Acrobat, iLovePDF, Sejda and Smallpdf.
- **Technical principle:** One modular monorepo and one branded UX; compose best-fit PDF engines instead of merging multiple entire applications.
- **Truth about current status:** A **sixteen-tool tested prototype** now exists with a FastAPI backend, no-build frontend, private processing worker and Gotenberg Office conversion; it is not a production service. See [Prototype](PROTOTYPE.md) and [Implementation Status](IMPLEMENTATION-STATUS.md).

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

## Current architecture and next viewer direction
The implemented product is the existing FastAPI + HTML/CSS/JavaScript application, with pypdf for working PDF utilities and a private worker/Gotenberg 9 service for Office conversion. Do not replace that working foundation merely to introduce a fashionable stack. PDF.js 6.5.438 is the selected Stage C browser viewer foundation; OCRmyPDF is a later Stage D specialist. Native existing-text editing still needs a separate technical/licensing decision. See [Top-two research](RESEARCH-TOP-2.md).

## First contributor actions
If you are an architect: run a focused evaluation of the PDFClear starter and license/compliance list.
If you are a backend engineer: extend the tested Office adapter one format at a time; XLSX-to-PDF is the next smallest conversion slice.
If you are an editor specialist: test native-text editing SDKs with font, layout and extraction checks.
If you are a QA engineer: define canonical fixtures and acceptance tests.
If you are a designer: prototype the unified upload/editor/workspace flow.
If you use Codex: follow [AGENTS.md](../AGENTS.md) and [Codex Playbook](CODEX-PLAYBOOK.md).

**The install/run/test commands are documented** in [Prototype](PROTOTYPE.md) and the [CI failure-recovery guide](CI.md). The previous prototype CI passed; the expanded contributor workflow adds matrix tests, coverage, lint, package/container checks and dependency scanning. See [Implementation Status](IMPLEMENTATION-STATUS.md) for verified evidence and outstanding checks.

