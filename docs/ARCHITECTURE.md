# Reference Architecture (Proposed, Not Yet Implemented)

## Architectural stance
**One branded monorepo, modular services and interchangeable engines.** Prefer adapter packages to tightly coupling the UI to any vendor. Document all untrusted-data boundaries.

~~~text
Browser
  ├─ Marketing + Tool Discovery UI
  ├─ PDF Workspace (upload once, chain actions)
  ├─ PDF Viewer/Editor (PDF.js + canvas/UI layer)
  └─ Local PDF processing where feasible
         │ authenticated TLS, scoped file handles
         ▼
API Gateway / BFF (auth, validation, quotas, job creation)
         │
         ├─ Job Queue + Status/Progress
         ├─ Document Metadata and Revision Store
         ├─ Private Temporary Object Storage
         └─ Typed Engine Adapter Interface
                   ├─ Gotenberg (conversion/processing candidate)
                   ├─ qpdf/PDFBox/pdfcpu specialist tools as validated
                   ├─ OCRmyPDF (scans)
                   ├─ Docling (layout/table extraction)
                   ├─ pyHanko (digital signatures)
                   ├─ Commercial native PDF editor SDK (evaluation)
                   └─ AI service (opt-in and audited)
         ▼
Temporary sandbox workers / downloaded output / expiration
~~~

## Logical monorepo layout (future, not created yet)

~~~text
apps/
  web/                     # React/TypeScript website & workspace
  admin/                   # Optional operations console
packages/
  ui/                      # Design system
  pdf-contracts/           # Typed tool/engine API contracts
  pdf-editor/              # Editor integration and UI
  pdf-local-tools/         # Browser-local operations
services/
  api/                     # Auth, job/asset orchestration
  workers/                 # Isolated async execution
  ai/                      # Optional doc intelligence
infra/
  docker/                  # Dev compose, images, sandbox configs
  deploy/                  # Infrastructure templates
tests/
  fixtures/                # Synthetic PDFs and expected outputs
  e2e/                     # End-to-end tests
docs/
~~~

## Core domain objects
- **Document:** random opaque ID, owner/tenant, content hash, size/pages/type, storage pointer, created/expires-at, provenance.
- **Revision:** parent document/revision, operation list, input/output hashes, validity/fidelity report, preview reference.
- **ToolDefinition:** stable feature ID, input constraints, supported engines, options schema, output types, privacy mode, cost/complexity.
- **Job:** tenant, tool ID, inputs, status (queued/running/succeeded/failed/cancelled), timestamps, retry limit, progress, result pointers.
- **AuditEvent:** actor, tenant, action, outcome, timestamp, sanitized metadata; never raw document text by default.
- **Workflow:** ordered steps, typed inputs/outputs and explicit user permissions.

## Engine adapter contract
One tool can have different implementations. Each adapter must expose: capabilities/version, configuration and license metadata, validate(request), execute(job, sandbox), cancellation, progress, deterministic errors, health checks and output validation. Route to an engine only if it meets that feature's fidelity and safety policy.

- Use typed request/response DTOs, stable operation IDs and durable job IDs.
- Validate uploaded content by parsing and bounded resource use.
- Keep engine credentials/server secrets out of the client.
- Allow feature flags and a graceful fallback when an engine is unavailable.
- Record which engine/version processed an output for quality/debugging.

## Editor design
PDF.js can display selectable text but isn't an out-of-the-box high-fidelity content editor. pdf-lib is useful for adding/modifying forms/annotations and new objects, **not for general native existing-text rewriting**. Treat native content editing as its own adapter-backed feature; see [Decisions](DECISIONS.md). Secure redaction must be separate from whiteout overlays.

## Data/storage and privacy
- Local-first where possible and explicit local/server/third-party processing indicators.
- Object storage private; short-lived upload/download links; key/tenant isolation.
- Retention policy, deletion job and job-artifact lifecycle are a release gate, not an afterthought.
- No public PDF URL ingestion without SSRF defenses and network egress policy.
- No untrusted PDF handling on privileged hosts.

## Technology candidates
React + TypeScript; a suitable application framework; PostgreSQL metadata; Redis/BullMQ queues; object storage; isolated container processing; Gotenberg with specialist adapters; OCRmyPDF; Docling. **Choose versions after auditing existing starter code and operational footprint.** Avoid adding every candidate automatically.

## Open technical decisions
1. Keep/refactor PDFClear or start with a fresh app shell?
2. Native editor SDK: commercial integration vs long-term proprietary editor investment?
3. Queue/storage stack for earliest MVP versus long-term scale?
4. Browser-local versus server operations, specifically for privacy-sensitive workflows?
5. Long-term licensing model of original code (proprietary, dual, open-source)?

See [Decisions](DECISIONS.md), [Reuse vs Build](REUSE-VS-BUILD.md) and [API/Data Contracts](API-AND-DATA-CONTRACTS.md).
