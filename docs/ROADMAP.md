> **Current freeze (2026-11-14): Only Stages A–D active. All Phase 4/5 work below is historical/future scope and must not be implemented now.** See [Active Scope](ACTIVE-SCOPE.md).

# Phased Product Roadmap

No deadlines promised. Complete phases using measurable release gates rather than claiming “everything built” after a single Codex run.

## Phase 0 — Governance + reproducible foundation
**Deliver:** audited source starter decision, dependency/SBOM and license checklist, architecture ADRs, accepted feature map, synthetic test corpus, repo structure, verified local run/build/test commands, PR CI and security scan.
**Exit criteria:** a fresh developer can reproduce a green build; no unresolved critical license blockers.

## Phase 1 — Credible core PDF toolkit (MVP)
**Deliver:** consistent upload-to-download experience; merge, split, extract, organize, rotate, JPG↔PDF, compress, page numbers, watermark, basic viewer and basic form filling (validated via real engines).
**Exit criteria:** end-to-end tests, correct PDF parsing, downloadable output, cleanup and safe resource limits.

## Phase 2 — Professional editing differentiation
**Deliver:** robust editor UI, annotations, shapes, images, signatures, links, undo/redo, forms, working-draft revisions. Resolve **native existing text editing** through a licensed SDK or a technically sound proven implementation.
**Exit criteria:** no mislabeling of overlays as native editing; layouts/fonts/extraction verified on a defined corpus.

## Phase 3 — Broad tool parity + quality
**Deliver:** Word/Excel/PPT conversions, OCR, PDF/A, repair, split by bookmark/text/size, Bates, metadata, N-up, compare, secure redaction, digital signatures.
**Exit criteria:** tool-by-tool fidelity thresholds, failure handling, accessibility/security/retention policies.

## Phase 4 — AI and workflow platform
**Deliver:** structured extraction, document-grounded chat, summaries, translation, human-reviewed smart-redaction/split, batch operations, workflow builder and public API (scope dependent on economics).
**Exit criteria:** quality evaluation, AI privacy consent, cost limits, opt-out/local-only support where feasible.

## Phase 5 — Commercial scale / multi-platform
**Deliver:** billing, accounts, team workspaces, audit logs, organization roles, collaboration, desktop packaging, mobile capture, enterprise deployment.
**Exit criteria:** load tests, disaster recovery, observability, secure defaults, support and privacy readiness.

## Parallel workstreams
- **Design:** tool directory, workspace, error/progress and editor flows.
- **Engineering:** adapter APIs, PDF engines, web UI, queue, storage.
- **Security/legal:** licenses, sandbox, data retention, privacy statements and signature policy.
- **Quality:** synthetic documents, output comparison, performance baselines.
- **Business:** pricing economics, support model, market benchmarks.

## Feature priority rules
P0 = required for credible first release; P1 = broad parity/advantage; P2 = later power user/enterprise. The actual scope can change after research. Reference stable IDs in [Feature Inventory](FEATURE-INVENTORY.md) and developer-sized tasks in [Backlog](IMPLEMENTATION-BACKLOG.md).
