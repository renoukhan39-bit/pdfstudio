# Instructions for Codex and AI Coding Agents

Read this file, [Start Here](docs/START-HERE.md), [Architecture](docs/ARCHITECTURE.md), [Licensing](docs/LICENSING-AND-DEPENDENCIES.md), and [Quality](docs/QUALITY-AND-TESTING.md) before changing code.

## Mission and scope
Create an independently branded commercial-quality PDF platform. Compete with Adobe Acrobat in editing depth, Sejda in editing convenience, iLovePDF in tool breadth, and Smallpdf in usability. **Do not claim we are #1 or already feature complete.** A merge-only proof of concept now exists under app/ with tests/. Its tool status is PROTOTYPE, not SHIPPED. Follow docs/IMPLEMENTATION-CHECKLIST.md in order.

## Mandatory engineering sequence
1. Read the repository and identify what already exists before suggesting a rewrite.
2. Produce a short scope, files-to-change list, license risk check and acceptance tests **before implementation**.
3. Prefer maintained, production-proven libraries and service adapters to custom PDF engines.
4. Implement one vertical slice at a time; no big-bang multi-repository merge.
5. Add automated tests, run available checks, report exact commands and results.
6. Update feature status and docs for every delivered feature.
7. Make focused commits/PRs. Never remove working features casually or assert unverified completeness.

## Hard rules
- Do not copy proprietary source, logos, interfaces or product assets from competitors.
- Do not ingest other GitHub repositories wholesale. Audit their code and licenses first.
- Do not introduce AGPL, source-available, noncommercial, SDK-license or conflicting dependencies into a proprietary product without explicit recorded legal/owner approval. “Public on GitHub” does **not** mean permissively licensed.
- Existing-text editing must change underlying content; a white box with new text on top is **not** native editing. Document quality/fidelity limits.
- Visual whiteout is **not** secure redaction. Secure redaction must remove the content, then pass extraction and forensic tests.
- “Drawn signature” is not the same as a certificate-backed digital signature; test and label each separately.
- Treat PDFs as untrusted input; prevent SSRF, path traversal, resource exhaustion and arbitrary file execution; run workers with strict isolation.
- No credentials, keys, customer data, sample IDs or confidential PDFs in commits, logs, issues, or AI prompts.
- No feature can be marked shipped without end-to-end output verification and security acceptance where applicable.

## Current implementation and next task
The merge prototype now has raw-body upload limits and expanded contributor CI. Read docs/PROTOTYPE.md, docs/CI.md and docs/IMPLEMENTATION-STATUS.md. Next: resolve any CI findings, lock/audit dependencies, then create an isolated Gotenberg 9 adapter spike with output tests. No public deployment until PDF worker isolation and global resource limits are proven.

## Decision discipline
For every engine selection record: capabilities, license, integration effort, maintenance, security, quality, costs and fallback. Use [Decisions](docs/DECISIONS.md). Ask for owner approval on licensing/branding/pricing choices rather than silently choosing them.

## Codex token/credit management
- Audit existing modules and dependency capabilities first.
- Request minimal diffs and reviewable PRs; do not regenerate whole codebases.
- Avoid broad research, speculative scaffolding and duplicate implementations.
- Keep a “reuse/build/defer” decision per feature.
- Stop at blockers (license, secret, SDK contract, no suitable engine) and report them.

## Response format for each coding task
Summary | Files changed | Reuse decision | Commands run + results | Before/after behavior | Security/license impact | Open risks | Next smallest task.

See [Codex Playbook](docs/CODEX-PLAYBOOK.md).

