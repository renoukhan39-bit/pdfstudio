# Security Policy

**Status:** planning; no deployed service or supported release has been announced.

## Reporting vulnerabilities
Please do **not** post vulnerabilities or secrets in public issues. Use GitHub's private vulnerability reporting feature for this repository if enabled. If it is unavailable, contact the maintainer through a private channel listed on their GitHub profile; never send unredacted user documents in an unverified channel.

## Threat model to implement before public launch
- Treat PDF, Office, image, HTML and URL inputs as hostile.
- Put server processing in isolated, unprivileged containers/workers with CPU/memory/time/file-size/page-count limits, no ambient cloud credentials, and limited outbound network access.
- Reject path traversal, decompression bombs, malformed file abuse, unsafe HTML execution and remote URL SSRF; allowlist network destinations where feasible.
- Scan files, verify content type and enforce quotas/rate limits.
- Encrypt transport, protect temporary storage, minimize logs and set automatic file expiry/deletion.
- Keep storage private by default with short-lived scoped download URLs.
- Obtain explicit consent for external AI services and document transmission; support local-only operations where possible.
- Implement true redaction that removes content (not overlay) and verify text extraction and metadata do not leak it.
- Carefully separate signature images, electronic acknowledgments and cryptographic digital signatures.
- Apply automated dependency/SBOM, secret, container and supply-chain scanning.
- Use CSRF protection, authz checks and audit logs for collaboration and account features.

## Data handling default until policy is approved
Build for ephemeral processing: avoid indefinite PDF retention, do not train on customer documents by default, and do not store customer documents in analytics. Specific retention/deletion SLAs require a decision, implementation, tests and an accurate published privacy policy.
