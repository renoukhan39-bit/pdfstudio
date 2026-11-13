# Initial Engineering Backlog

These are proposal tickets, not claims of progress. Create/track issues for execution; never put “all features” into one issue.

| Order | Ticket | Feature IDs | Acceptance / deliverable |
| --- | --- | --- | --- |
| 0 | Audit repository and candidate starter | PL-01 | Reproducible build and security/license/maintenance report for PDFClear; approved keep/refactor/restart decision |
| 1 | Adopt architecture and licenses | PL-10 | Approved ADRs; SBOM process; dependency import policy |
| 2 | Define synthetic PDF quality corpus | Cross-cutting | Text/scanned/tables/forms/signed/encrypted/complex fonts, stable expected outputs |
| 3 | Create web shell + tool registry | PL-01 | Responsive accessible navigation, tool metadata, placeholder states accurately labeled |
| 4 | Typed tool adapter + end-to-end example | OP-01 | Upload → merge → preview/download; output verified; isolated execution |
| 5 | Gotenberg backend spike | OP-01, CV-02 | Validate deployed service, real endpoints and license; working tests |
| 6 | Initial core tool slice | OP-02–06, CV-07–08 | Working integration and test evidence per tool |
| 7 | Workspace revision model | WF-01 | Upload once, chain operations, temporary storage, cleanup |
| 8 | Viewer and basic annotations | ED-01, ED-02, ED-07/08 | Save/reopen with correct coordinate geometry |
| 9 | Native editing engine decision | ED-03, ED-04, ED-18 | SDK evaluation, cost/licensing, layout/text extraction benchmarks |
| 10 | Form and signing roadmap spike | ED-11–13, SC-05–10 | Tests distinguish form/e-sign/certificate signature |
| 11 | OCR and structured extraction spike | CV-14, AI-04 | Searchability and table structure benchmarks |
| 12 | Conversion fidelity benchmark | CV-01–06 | Defined tests across Office docs, fonts and layouts |
| 13 | Secure redaction evaluation | SC-03 | Proof that underlying text/images are removed |
| 14 | Jobs and retention | WF-02, PL-04 | Robust retries, isolation, expiration and audits |
| 15 | AI consent/provenance framework | AI-01–07 | Grounded answers, privacy opt-in and cost metering |
| 16 | CI, security + performance gates | Cross-cutting | Required checks green on release candidate |

## Definition of ready for an issue
User story; feature ID; current behavior; solution candidates; reuse decision; license review; accepted input types and edge cases; performance budget; privacy/security concern; exact success tests.

## Definition of done
- Implemented and reviewed code.
- Tests include output validity/integrity and at least one adverse PDF case.
- Docs and feature status reflect reality.
- Error handling, privacy, retention, license obligations verified.
- Commands/results and supported/unsupported cases recorded in PR.
