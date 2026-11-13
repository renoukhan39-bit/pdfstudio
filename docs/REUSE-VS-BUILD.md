# Reuse vs Build: Credit-Efficient Integration Strategy

**This file is the antidote to unnecessary Codex development.** Evaluate maintained existing engines first, select just enough to implement measurable features, then write custom orchestration/product code.

## Build ourselves (where unique value lives)
- Cohesive PDF Studio brand, responsive tool discovery and navigation.
- One-document workspace, operation chaining and predictable editor/processing UX.
- Tool adapter APIs, capability routing, typed errors, result comparison and metadata.
- Permission/privacy UX, reliable previews, history, product analytics without document content.
- Quality/fidelity test harness, secure production operations and integration with billing/auth.
- Differentiating AI workflows and automation logic (using third-party models responsibly).

## Candidate reuse inventory (no integrations yet)

| Component | Candidate role | Decision | Caution |
| --- | --- | --- | --- |
| [PDFClear](https://github.com/aliansari22/pdfclear) | Website/toolkit starter | **EVALUATE** | Audit security, build, dependencies, maintainability and actual feature quality |
| [Folio](https://github.com/doktorigi/folio) | Editor reference/components | **EVALUATE** | Existing text replacement may be overlays; check actual semantics |
| [Gotenberg](https://github.com/gotenberg/gotenberg) | HTTP conversion and processing backend | **FIRST INTEGRATION SPIKE** | Verify version/API endpoints, dependencies and production licensing |
| [PDF.js](https://github.com/mozilla/pdf.js) | PDF rendering/search/selection | **LIKELY** | Rendering, not comprehensive PDF editor |
| [pdf-lib](https://github.com/Hopding/pdf-lib) | Browser PDF object creation/manipulation | **LIKELY** | Not general native existing-text editor |
| [qpdf](https://github.com/qpdf/qpdf) | Structural/encryption specialist | **ON DEMAND** | Avoid overlap with primary engine |
| [Apache PDFBox](https://github.com/apache/pdfbox) | Java PDF processing specialist | **ON DEMAND** | New runtime/operational cost |
| [pdfcpu](https://github.com/pdfcpu/pdfcpu) | Go PDF utility specialist | **ON DEMAND** | Don't add redundant engine |
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | OCR scanned PDFs | **SPIKE** | External tools/models have their own licenses |
| [Docling](https://github.com/docling-project/docling) | Structured document extraction | **SPIKE** | Model distribution license, compute needs |
| [pdfme](https://github.com/pdfme/pdfme) | Visual templates and generation | **EVALUATE** | Templates ≠ full native PDF editing |
| [React Konva](https://github.com/konvajs/react-konva) | Canvas manipulation UX | **OPTIONAL** | UI only; persistence engine needed |
| [pyHanko](https://github.com/MatthiasValvekens/pyHanko) | Digital signatures/verification | **FUTURE SPIKE** | Secure key custody and legal compliance |
| [BullMQ](https://github.com/taskforcesh/bullmq) | Queue/retries/progress | **CONDITIONAL** | Add only when async processing requires |
| [Yjs](https://github.com/yjs/yjs) | Collaboration primitives | **LATER** | Conflict resolution and PDF consistency hard |
| [Keycloak](https://github.com/keycloak/keycloak) | Enterprise identity | **LATER/OPTIONAL** | Heavy for initial MVP |

## Advanced native editor: explicit buy-vs-build gate
Evaluate [Nutrient](https://www.nutrient.io/sdk/web/), [Apryse](https://apryse.com/products/webviewer) and other native-content PDF editing SDKs. Obtain quotes and verify editable text, fonts, forms, redaction, PDF standard support, deployment restrictions and export fidelity. Evaluate [ONLYOFFICE DocumentServer](https://github.com/ONLYOFFICE/DocumentServer) as an editor candidate only after AGPL/commercial licensing review. None may be presented as “free white-label native editing” by default.

## Risk list / avoid unapproved combinations
- Stirling PDF includes licensing nuance in some components and commercial offerings; read **current** license files.
- PyMuPDF and some projects that depend on it have AGPL/commercial licensing choices; check transitive terms.
- GigaPDF's public code may have noncommercial terms; do not assume public equals free commercial use.
- Sejda SDK differs from Sejda's hosted editor; do not assume general public API parity.
- iLovePDF's developer API is a paid/credit-backed external service, not ownership of their implementation.

## Reuse decision checklist
- Does the tool meet the required output fidelity? (not just an API response)
- Is the license compatible with the product plan? Has a reviewer checked transitive dependencies?
- Is it maintained? Does the specific required version have security support?
- Can it operate offline/self-hosted? What input leaves our infrastructure?
- What does it cost per request or per month? Can we meter/cap usage?
- Can the UI remain consistent across engines?
- Is there a real test fixture for the feature?
- Is a fallback possible if the engine disappears or changes licensing?

## Decision rule
**One primary engine per operation**, specialist fallback only after test evidence. New dependency acceptance requires an architecture decision entry and approved license review. See [Licensing](LICENSING-AND-DEPENDENCIES.md).
