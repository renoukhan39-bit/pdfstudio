# Initial API and Data Contracts (Design Proposal)

These are **draft contracts**, not implemented HTTP endpoints. Final shapes follow a tested stack and security review.

## API design approach
- Tool registry carries feature IDs, supported input/output types, options schema, size/page limits, available execution modes (browser/server/paid SDK).
- Jobs are asynchronous for expensive work. A small local-only tool may run entirely in the browser.
- Use a typed adapter layer between product APIs and PDF engines; no engine-specific requests in UI code.
- Use stable opaque IDs for documents, revisions, jobs and workflows.
- Maintain idempotency keys and bounded retries for expensive/metered processing.

## Example conceptual routes
| Endpoint | Purpose |
| --- | --- |
| GET /api/tools | Available tested tools and capabilities |
| POST /api/uploads | Create scoped upload session |
| POST /api/documents | Register a validated uploaded file |
| POST /api/jobs | Submit operation with document IDs/options |
| GET /api/jobs/:id | Poll state, progress and result metadata |
| POST /api/jobs/:id/cancel | Request cancellation |
| GET /api/documents/:id/revisions | Version history |
| POST /api/workflows | Save validated workflow definition (later) |
| GET /api/downloads/:token | Scoped expiring download |

## Request/response principles
Job request: feature ID, input revision IDs, validated options, user/tenant scope, optional idempotency key. Job response: job ID, status/progress, accepted engine and version (server metadata), expiry, typed errors and output references.

## Lifecycle and isolation
File → content/size/format validation → private staged storage or browser-local path → isolated tool executor → output validation → version pointer → expiry/deletion. Never let user-provided paths or URLs access internal services. Generate audit records with sanitized metadata only.

## Versioning
Version tool options and API contracts independently from engine versions. Record transformation provenance so failures can be reproduced. Design for different quality tiers and future engine replacement.
