# Quality, Fidelity and Testing Plan

A PDF tool is not done merely because an endpoint returned HTTP 200. Verify **the output PDF and user-visible result**.

## Synthetic fixture matrix (never use real customer documents)
1. Standard text PDFs: selectable, multiple fonts, ligatures and styles.
2. Scanned, skewed, low-contrast and mixed OCR/non-OCR documents.
3. English, Hindi and Punjabi scripts; mixed RTL/LTR and complex shaping where applicable.
4. Tables, images, charts, vector drawings, layers/transparency.
5. Rotated, cropped, non-A4 and extremely large/many-page documents.
6. Form PDFs: text, checkboxes, radio, dropdown and signatures.
7. Password-protected/permission-limited PDFs used with authorization.
8. Bookmarks, internal/external links, annotations, embedded attachments and metadata.
9. Digitally signed PDFs (signatures invalidate when content changes; warn users).
10. PDF/A and tagged/accessibility PDFs.
11. Malformed, truncated, oversized and maliciously structured PDFs.
12. Realistic conversion sources: DOCX/XLSX/PPTX/HTML with nontrivial layouts.

## Test layers
- **Unit:** tool options, validation, MIME checks, job state, error mapping.
- **Contract:** adapter capabilities/version and request/response guarantees.
- **Integration:** actual engine with synthetic fixtures, timeouts and cancellation.
- **E2E:** browser upload, tool run, preview, download, reopen and workflow chaining.
- **Fidelity:** pixel/structural diff with tolerances; extract text, hyperlinks, fonts and forms.
- **Security:** sandbox, SSRF, zip/pdf bombs, injection, malicious HTML, rate limits.
- **Accessibility:** keyboard/navigation, focus, contrast, labels, screen reader UX.
- **Performance:** time, memory, CPU and cost by file size/page count and concurrency.
- **License:** SBOM and notices in output artifacts/containers.

## Special non-negotiable checks
**Native editing:** after a text edit, inspect extracted text, underlying drawing operators/objects where feasible and re-rendered pages. A hidden original string plus visible overlay is a failed native-editing test.

**Redaction:** after redaction, verify the removed information cannot be recovered by copy/paste, text extraction, object inspection, thumbnails or metadata. A colored rectangle is a failure.

**OCR:** verify searchable text positioning and accuracy on multilingual and mixed documents. Document supported languages.

**Digital signature:** explicitly test certificate and cryptographic validation; visually placing a signature image is not proof of digital signing.

**Conversions:** compare content, layout and structural semantics, not only file extension.

## Status progression
PLANNED → IN_PROGRESS → TESTED → SHIPPED. Only move to TESTED with recorded fixtures, commands, CI evidence and known limitations. SHIPPED adds deployment, monitoring, security and documentation.

## Release gate
All required acceptance checks pass, there are no known critical vulnerabilities or unapproved license conflicts, a rollback exists, input retention/deletion is tested, and the user-facing feature list matches reality.
