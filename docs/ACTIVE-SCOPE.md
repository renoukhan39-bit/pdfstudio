# Active project scope — A–D only (14 November 2026)

**Only Stages A, B, C and D are authorized for active engineering.** These cover foundation, core PDF tools/conversions, a professional editor, and advanced PDF processing/OCR/signing. **Stages E and F are frozen:** AI chat/summaries/translation, advanced workflows, billing, accounts, teams, public API, cloud history and desktop/enterprise expansion. Preserve their earlier roadmap descriptions as future ideas only. Do not add E/F dependencies, scaffolding, endpoints or implementation until the owner explicitly changes this decision.

## Reuse-first, no big-bang repo merge

The main product remains [this repository](https://github.com/renoukhan39-bit/pdfstudio), with 14 existing prototype tools and strong CI. Do not replace it with another complete website. Source from each upstream only after checking its exact commit, transitive licenses, security, activity, maintenance and output tests.

| Source | Decision | A–D use | Not for |
| --- | --- | --- | --- |
| [Gotenberg 9](https://github.com/gotenberg/gotenberg) | **INTEGRATE first** | Internal Office/HTML-to-PDF and other missing PDF operations | Copying its server or replacing working pypdf features |
| [PDF.js](https://github.com/mozilla/pdf.js) | **INTEGRATE for C** | PDF viewer, text selection, zoom, thumbnails/search | Native existing-text rewrite |
| [pdf-lib](https://github.com/Hopding/pdf-lib) | **EVALUATE for C** | Browser-based new text/image/form/annotation operations | General existing-text rewriting |
| [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF) | **INTEGRATE for D** | OCR/deskew/scanned-page text layer | Native text editing |
| [pyHanko](https://github.com/MatthiasValvekens/pyHanko) | **LATE D** | Certificate-backed digital signatures | Visual signatures |
| [pdfme](https://github.com/pdfme/pdfme) | **OPTIONAL** | Templates/forms only if needed after editor design | Arbitrary PDF native editing |
| [PDFClear](https://github.com/aliansari22/pdfclear) | **STUDY, DO NOT MERGE** | Local-first UX patterns, comparison benchmarks | Full frontend replacement |
| [Folio](https://github.com/doktorigi/folio) | **STUDY, DO NOT MERGE** | Editor interaction and annotations | Claiming overlays are native text editing |

**No current need to import:** Stirling PDF, S-PDF, GigaPDF, ONLYOFFICE, pdfcpu/PDFBox, Yjs, Keycloak, BullMQ, Docling. Reevaluate only if an active A–D feature demonstrates a specific gap. Some have licensing or complexity concerns. A public repo is not automatically free of licensing obligations.

**Native text editor exception:** Professional underlying-PDF-text editing requires an evaluated engine. Research Nutrient/Apryse and genuinely compatible alternatives; don't buy, copy, or integrate a restricted commercial or AGPL SDK without owner approval.

## Ordered actions

1. **A:** Protect current main branch; settle original-code licensing, lock dependencies, maintain security and regression coverage.
2. **B:** Complete Gotenberg DOCX-to-PDF spike with real isolated Compose conversion tests. Keep current 14 tools unchanged.
3. **B:** Add successful conversion to the interface; expand to PPTX/XLSX/HTML only after tests.
4. **B:** Finish missing image and page tools; use existing pypdf first, Gotenberg for demonstrated gaps.
5. **C:** Build PDF.js-based viewer and editing shell, then annotations, forms and signatures.
6. **C:** Choose the licensed native-content editor approach and prove text actually changes.
7. **D:** Integrate OCRmyPDF, archival/repair, secure redaction, signing/verification and high-fidelity reverse conversions.
8. **A–D release gate:** verify output fidelity, accessibility, isolated workers, licenses, retention and production security.

## Who handles each work item

- **ChatGPT:** code changes, repository research, architecture, synthetic tests, reviewable PRs, CI log analysis; no claim of autonomous long-running work or ownership of the business.
- **Codex Cloud/Astra:** use only for a narrow blocker that requires Docker/large dependency installation, multi-service integration testing or complex native editor adaptation. Return one PR/fix and exact failure evidence.
- **GitHub Actions:** authoritative clean-install matrix, Docker Compose, Chromium and PDF-integrity tests.
- **Owner:** source-code license, SDK expenses, hosting, privacy/retention decisions, PR review and production release.

## Cost rules

Do not ask Codex to finish the project in one prompt. Ask for one failing check or clear integration requirement. Preserve existing tests, don't lower coverage, don't disable CI, don't import entire other applications and don't add Stage E/F work.
