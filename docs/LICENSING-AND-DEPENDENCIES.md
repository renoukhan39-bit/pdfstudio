# Third-Party Licensing and Dependency Register

**IMPORTANT: This is a preliminary research checklist, NOT legal advice or a verified legal audit.** Recheck each repository's current LICENSE, NOTICE, dependencies, bundled models and product terms before importing, deploying, or commercially redistributing software. Versions and terms may change.

## Ownership model
The business should own **its original branding, application code, infrastructure and original designs**, not claim ownership of independent upstream libraries. Public repositories can be read but cannot necessarily be copied, white-labeled or commercially redistributed without conditions. This repository's own new code license has **not yet been selected**; maintainer must decide before accepting major outside code contributions.

## Preliminary register

| Component | Indicative upstream terms (reverify) | Notes before use |
| --- | --- | --- |
| PDFClear | Apache-2.0 | Preserve license/notices; audit all dependencies |
| Folio | MIT | Preserve copyright/license; clarify overlay editing limits |
| Mozilla PDF.js | Apache-2.0 | Check assets/fonts bundled in build |
| pdf-lib | MIT | Confirm version and transitive dependencies |
| pdfme | MIT | Check packages/fonts/assets |
| React Konva | MIT | Check assets and transitive dependencies |
| Gotenberg | MIT project code | Engine bundles other software; audit separately |
| qpdf | Apache-2.0 | Verify package and linked dependency licenses |
| Apache PDFBox | Apache-2.0 | Audit libraries and crypto providers |
| pdfcpu | Apache-2.0 | Verify release and dependencies |
| OCRmyPDF | MPL-2.0 project code | OCR/rendering dependencies and model licenses differ |
| Docling | MIT project code | Downloaded model weights/data may differ |
| pyHanko | MIT | Verify PKI components and crypto dependencies |
| BullMQ | MIT | Redis and hosting have distinct terms |
| Yjs | MIT | Provider integrations may be commercial |
| Keycloak | Apache-2.0 | Operational and identity review |
| ONLYOFFICE DocumentServer | AGPL and potentially additional provisions | Commercial/white-label license decision necessary |
| Nutrient/Apryse | Proprietary commercial terms | Obtain license, pricing, feature rights and deployment scope |
| PyMuPDF | AGPL or commercial license | Do not silently embed in proprietary closed-source product |
| Stirling PDF ecosystem | Mixed/open-core component-specific terms | Do not assume unrestricted production use |
| GigaPDF | May include noncommercial terms | Verify actual license before any code reuse |
| iLovePDF API | Commercial service terms | API integration is not source code ownership |
| Sejda SDK | Open-source/commercial options | Hosted Sejda editor is not automatically embeddable |

## Required artifact for every imported dependency
- Name, exact version/commit, source URL, package scope.
- SPDX expression for direct + transitive packages.
- LICENSE, NOTICE and attribution obligations.
- Whether it is used at build time, server-side, client-side, bundled or redistributed.
- Commercial SaaS and desktop-distribution permission analysis.
- Patent, trademark, model-weight, font, image and cloud/API restrictions.
- Known vulnerabilities, maintenance cadence and replacement plan.
- Approval owner/date and distribution notice location.

## Proposed compliance process
1. Build SBOMs (e.g. CycloneDX/SPDX) from lockfiles/containers.
2. Run dependency and license scanners; manually review material/high-risk packages.
3. Maintain THIRD_PARTY_NOTICES once components are actually imported.
4. Block production deployment of unreviewed AGPL/noncommercial/source-available SDK components.
5. Seek qualified legal advice for commercial release and contribution agreements where necessary.

**Never put a blanket MIT/Apache license at the repo root without explicit owner approval.**
