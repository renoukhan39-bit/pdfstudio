# PDF Studio Feature Inventory and Target Matrix

**Status disclaimer:** This is an aspirational **product backlog**, not an assertion that these tools are built. With the exception of **OP-01 (merge PDF), which has a locally tested early PROTOTYPE**, all items remain **PLANNED**. OP-01 is **not yet SHIPPED**. The feature ID remains stable as we implement. P0 = first launch candidate; P1 = competitive expansion; P2 = later/enterprise/advanced.

After implementation, record: owner, engine adapter, supported platforms, limitations, fixture IDs, test evidence, status (PLANNED / IN_PROGRESS / TESTED / SHIPPED).

## Professional editor — highest-value differentiator

| ID | Target feature | Priority | Notes / acceptance focus |
| --- | --- | --- | --- |
| ED-01 | Open/render/search PDF with thumbnails and zoom | P0 | Fast display, preserve page coordinates |
| ED-02 | Add/move/resize/format new text | P0 | Fonts, color, size, rotation |
| ED-03 | **Edit existing underlying PDF text** | P0 research gate | Verify extractable content changed, no cover-up |
| ED-04 | Find and replace across pages | P1 | Real content update, bounded scope |
| ED-05 | Insert/replace/resize/delete images | P1 | Image persistence and quality |
| ED-06 | Add/edit website and internal-page hyperlinks | P1 | Link targets survive save |
| ED-07 | Highlight/underline/strikeout/comments | P0 | Annotation round trips |
| ED-08 | Freehand drawing, lines, arrows, rectangles, ellipses | P0 | Undo and scaling |
| ED-09 | Move/select/delete objects and layer order | P1 | Real object scope documented |
| ED-10 | Undo/redo and revision history | P0 | Predictable save behavior |
| ED-11 | Add/edit/fill text fields, multiline fields, dropdowns, checkboxes, radio buttons | P1 | AcroForm compatibility |
| ED-12 | Signature fields and simple e-signatures | P1 | Distinguish drawn vs digital |
| ED-13 | Field names, defaults and tab order | P1 | Validate form structure |
| ED-14 | Whiteout / visual overlays (clearly labeled) | P1 | NOT secure redaction |
| ED-15 | Page thumbnail drag reorder, insert, duplicate, remove | P0 | Preserve annotations/forms |
| ED-16 | Content copy/paste, align, guides | P2 | Accessible controls |
| ED-17 | Optional real-time multi-user review | P2 | Auth, versions, conflict handling |
| ED-18 | Font substitution/reflow and multilingual complex scripts | P1 research | High-fidelity stress tests |

## Everyday document operations

| ID | Target feature | Priority |
| --- | --- | --- |
| OP-01 | Merge PDFs | P0 |
| OP-02 | Split by selected pages/ranges | P0 |
| OP-03 | Extract pages | P0 |
| OP-04 | Delete pages | P0 |
| OP-05 | Reorder/organize pages | P0 |
| OP-06 | Rotate pages | P0 |
| OP-07 | Crop pages/change margins | P1 |
| OP-08 | Resize/page format | P1 |
| OP-09 | Alternate & mix pages from two PDFs | P1 |
| OP-10 | Split by bookmarks/chapters | P1 |
| OP-11 | Split by file size | P1 |
| OP-12 | Split by matching text | P2 |
| OP-13 | Split double-page scans / split in half | P1 |
| OP-14 | N-up / multiple pages per sheet | P1 |
| OP-15 | Flip/mirror pages | P1 |
| OP-16 | Add page numbers | P0 |
| OP-17 | Headers/footers | P1 |
| OP-18 | Watermark (text/image) | P0 |
| OP-19 | Bates numbering | P1 |
| OP-20 | Create/edit bookmarks | P1 |
| OP-21 | Edit PDF metadata | P1 |
| OP-22 | Extract embedded images | P1 |
| OP-23 | Rename by embedded document text | P2 |
| OP-24 | Remove annotations in bulk | P2 |
| OP-25 | Grayscale conversion | P1 |
| OP-26 | Compare document versions | P1 |

## Conversion, optimization and scanning

| ID | Target feature | Priority | Notes |
| --- | --- | --- | --- |
| CV-01 | PDF to Word | P1 | High-fidelity output, not just text dump |
| CV-02 | Word/DOCX to PDF | P0 | Layout validation |
| CV-03 | PDF to Excel/CSV | P1 | Table semantics |
| CV-04 | Excel to PDF | P1 | Sheet/scaling options |
| CV-05 | PDF to PowerPoint | P1 | Editable-vs-image limitations clear |
| CV-06 | PowerPoint to PDF | P1 | Layout validation |
| CV-07 | PDF to JPG/PNG/TIFF | P0 | DPI/page selection |
| CV-08 | JPG/PNG/images to PDF | P0 | Sorting/orientation |
| CV-09 | HTML/URL to PDF | P1 | SSRF/sandbox control |
| CV-10 | PDF to plain text | P1 | Reading order expectations |
| CV-11 | PDF to Markdown | P1 | Tables/headings/citations |
| CV-12 | Compress PDF | P0 | Quality-size tradeoffs |
| CV-13 | Repair damaged PDFs | P1 | Best-effort and no silent corruption |
| CV-14 | OCR scanned PDFs | P1 | Searchable text layer |
| CV-15 | Deskew/clean scans | P1 | Preserve readable text |
| CV-16 | Convert to PDF/A | P1 | Validate conformance |
| CV-17 | Scan-to-PDF mobile capture | P2 | Camera and edge detection |
| CV-18 | OCR-assisted Office conversion | P2 | Extractability vs fidelity |
| CV-19 | PDF/UA accessibility output/workflows | P2 | Standards validation, human review |

## Security, forms and signing

| ID | Target feature | Priority | Notes |
| --- | --- | --- | --- |
| SC-01 | Password-protect/encrypt PDF | P0 | Authorized operations only |
| SC-02 | Unlock known-password PDF | P1 | No bypass of unauthorized access |
| SC-03 | **Secure content redaction** | P1 | Remove underlying bytes, verify with extraction |
| SC-04 | Flatten annotations or forms | P1 | Clearly explain effects |
| SC-05 | Fill existing PDF forms | P0 | Round-trip test |
| SC-06 | Build interactive fillable forms | P1 | Field compatibility |
| SC-07 | Add typed/drawn/uploaded e-signature | P1 | No cryptographic claim |
| SC-08 | Certificate-backed digital signatures/PAdES | P2 | Key handling and validity verification |
| SC-09 | Request signatures and status tracking | P2 | Auditability and jurisdiction review |
| SC-10 | Validate signatures/certificates | P2 | Distinguish validity states |

## AI, collaboration, workflows and platform

| ID | Target feature | Priority |
| --- | --- | --- |
| AI-01 | PDF chat with document-grounded citations | P1 |
| AI-02 | Summarize long PDFs | P1 |
| AI-03 | Translate PDFs with layout caveats | P1 |
| AI-04 | Extract structured tables/entities | P1 |
| AI-05 | Classify/smart split documents | P2 |
| AI-06 | Assisted sensitive-data suggestions + human-approved redaction | P2 |
| AI-07 | PDF-to-Markdown for AI pipelines | P1 |
| WF-01 | Multiple tools in one continuous workspace | P0 |
| WF-02 | Batch processing of multiple documents | P1 |
| WF-03 | Visual workflow builder | P2 |
| WF-04 | Scheduled/triggered workflows | P2 |
| WF-05 | Public REST API with rate limiting/webhooks | P2 |
| PL-01 | Responsive browser experience | P0 |
| PL-02 | Optional local-only processing for eligible tools | P1 |
| PL-03 | User accounts and project history | P1 |
| PL-04 | Private cloud storage and file expiration | P1 |
| PL-05 | Subscription/billing and usage meters | P2 |
| PL-06 | Teams, roles, organization admin and audit logs | P2 |
| PL-07 | Desktop packaging and offline experience | P2 |
| PL-08 | Mobile experience and scan capture | P2 |
| PL-09 | Accessibility and internationalization | P0 |
| PL-10 | Open integration interface for engines and SDKs | P0 |

## Acceptance rule
An entry may be SHIPPED only after end-to-end integration tests, output integrity tests and relevant safety/privacy/license reviews pass. The exact implemented scope must be documented (e.g. direct editing available for selectable text only, not scanned images). See [Quality](QUALITY-AND-TESTING.md).

## Notes
This catalog intentionally aggregates iLovePDF-style utilities, Sejda-style editing, Acrobat-style professional workflows and original workspace/AI capabilities. Competitor names describe benchmark categories, not licensed or endorsed integrations.
