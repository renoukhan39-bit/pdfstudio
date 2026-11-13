# Operations, Privacy and Deployment Plan

No production architecture is deployed yet. The following are **release requirements**, not operational claims.

## Deployment topology
- Static or server-rendered frontend behind HTTPS.
- Stateless API with authentication, quotas, billing/feature flags.
- Async queue and isolated sandbox processing workers.
- Engine containers (Gotenberg, OCR, layout extraction) with version pinning.
- Private object storage with per-document expiration.
- Database for metadata/jobs/users only; store raw documents only where explicitly authorized.
- Metrics/logging excluding PDF content, plus alerts on processing failures and costs.

## Security and privacy gates
- Untrusted file parsing under CPU/memory/time and page constraints.
- Hardened containers: unprivileged users, no privileged mounts, minimal egress, readonly filesystem where practical.
- URL-to-PDF protections for SSRF and unsafe HTML.
- Encrypted transfer/storage where applicable; signed scoped URLs; worker cleanup.
- Secrets manager, least-privilege IAM and audit events.
- GDPR/other privacy obligations assessed for launch regions; accurate privacy policy and deletion controls.
- Human-consent controls for external AI and API processors.
- Automated SBOM, license scan, dependency vulnerability checks, container scanning.

## Reliability plan
- Health checks and circuit breakers per engine.
- Bounded retries and idempotent jobs, with dead-letter/recovery strategy.
- Backups for metadata, not accidental indefinite preservation of private PDFs.
- Separate dev/staging/prod with environment-specific secrets.
- Cost and latency dashboards by feature/engine, usage quotas and abuse prevention.
- Rollback and recovery procedures documented before opening to real users.

## Launch checklist
Verified tests; license approvals; security review; privacy/retention policy; user support/abuse contact; monitoring and incident runbook; load test; backups/recovery test; accessibility review; browser/OS matrix.
