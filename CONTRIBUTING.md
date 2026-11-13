# Contributing to PDF Studio

Welcome! You should not need access to private chats or previous conversations to contribute.

## First steps
1. Read [Start Here](docs/START-HERE.md), [Vision](docs/PRODUCT-VISION.md), [Feature Inventory](docs/FEATURE-INVENTORY.md), and [Architecture](docs/ARCHITECTURE.md).
2. Review [Roadmap](docs/ROADMAP.md) and [Backlog](docs/IMPLEMENTATION-BACKLOG.md).
3. Open a small issue describing the user problem, intended behavior, reuse/build decision, relevant licenses and acceptance tests.
4. For major dependencies, pricing decisions, data retention policy or native editing approach, seek maintainer approval first.
5. Submit a focused pull request; avoid large speculative rewrites.

## Current developer setup

The repository has an **early merge prototype**, not the whole planned toolkit.

~~~sh
git clone https://github.com/renoukhan39-bit/pdfstudio.git
cd pdfstudio
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
python -m pytest -q
~~~

Detailed scope, API and security limitations: [Prototype](docs/PROTOTYPE.md). Work through the [ordered checklist](docs/IMPLEMENTATION-CHECKLIST.md).

## Required automated checks

Read [CI and failure recovery](docs/CI.md). Every PR runs lint, JavaScript syntax,
Python 3.11/3.12/3.13 tests with an 85% coverage gate, an installed-wheel smoke
test, dependency vulnerability scanning/SBOM export, and a non-root container
smoke test. Failed tests fail the workflow and retain reports for diagnosis.
Reproduce the failed command locally, fix it, and push another commit.
Maintainers should require the `CI required` check and one review in main's
branch ruleset; workflow code alone does not activate merge enforcement.

## Pull request expectations
- Link the issue and mention the feature ID from the inventory.
- Explain why an existing library/service is or is not sufficient.
- Note dependencies, licenses and any legal review needed.
- Include input/output PDF test cases, negative cases and automated tests.
- Describe impact on accessibility, privacy, security, file deletion and costs.
- Include before/after screenshots for UI changes (synthetic data only).
- Update documentation and status from proposed -> in progress -> tested only when proven.
- Supply exact commands run and their results.

## Coding standards (to be finalized with the starter codebase)
- Prefer TypeScript, strict typing and typed engine interfaces for the browser/API layer.
- Keep PDF processing separated from UI. Provide explicit contracts for errors, progress, retries, and cancellation.
- Make third-party SDK dependencies replaceable behind adapters.
- Validate files by content and parsing, not extension alone.
- Keep tests deterministic; use synthetic and license-safe PDF fixtures.
- Add dependency lockfiles and CI checks when executable code is introduced.

## License note
No license has yet been selected for original project code. Do not assume pull requests or external code can be redistributed under arbitrary terms. By contributing, you represent that you have the right to submit your contribution. Contributors and maintainer should agree on contribution/licensing policy before substantial code submissions.

## Conduct and security
See [Code of Conduct](CODE_OF_CONDUCT.md) and [Security](SECURITY.md). Do not publish exploitable proof-of-concepts or real users' PDFs in a public issue.

