# Codex Cloud Contributor Playbook: Save Credits, Ship Verified Features

## How to use this repository with Codex
1. Connect the GitHub repository in your available Codex environment.
2. Read [AGENTS.md](../AGENTS.md), [Start Here](START-HERE.md), and the relevant module docs.
3. Select **one** issue/slice, not the entire long-term vision.
4. Ask Codex to audit existing code/dependencies and propose a minimal implementation with acceptance tests.
5. Review the plan and any commercial license/SDK decisions before proceeding.
6. Let Codex implement, run available build/tests and produce a PR with exact results.
7. Review before merge; update feature inventory and ADRs.

**Codex availability, models, environment and cloud features depend on your current account configuration; don't assume a particular named model is available.**

## First task prompt
> Inspect this repository. It is currently a documentation-first project for a world-class PDF platform. Read AGENTS.md and docs/START-HERE.md. Do not fabricate an existing app. Review PDFClear as a potential base and Gotenberg as a processing service, including maintenance, security, exact licensing and dependency constraints. Propose the smallest reproducible app shell + one tested PDF operation (merge) using an adapter. Before coding, provide scope, architecture changes, files, risks and acceptance tests. Then implement a focused PR with verified commands and outputs. Preserve original licenses. Do not integrate unapproved restrictive licenses or external API keys.

## Every Codex task should include
- User story and a stable feature ID.
- What code exists and what is currently missing.
- Engine reuse candidates and why chosen.
- License/security/data privacy constraints.
- Concrete acceptance tests and sample synthetic input/output.
- Maximum scope and files permitted to change.
- Prohibition on speculative rewrites, new custom processing algorithms without evaluation, and unproven feature claims.

## Cost-control rules
- Spend initial task time on inspection, not generating code.
- Prefer API adapters over rebuilding Gotenberg/OCR/PDF renderers.
- Use small sequential PRs; integrate only the needed dependency for that milestone.
- Do not ask Codex to build all 80+ features in one prompt.
- Collect exact command results; stop on environment/licensing limitations instead of inventing success.
- Run targeted tests first, full suite at release checkpoints.
- Skip decorative UI or unrequested components until core flow is working.

## Prompt for an engine audit
> For feature [ID], compare existing code, Gotenberg, PDF.js/pdf-lib, qpdf/PDFBox/pdfcpu, and relevant hosted SDKs. Return capability, output fidelity, licensing obligations (including transitive packages), maintenance, deployment footprint, privacy, cost and test plan. Recommend one primary adapter and one fallback only if justified. Do not implement until the selection is approved.

## Output checklist
Actual files changed, tests run, actual output files verified, list of supported and unsupported PDFs, dependency/license implications, security/privacy impact, next smallest task.
