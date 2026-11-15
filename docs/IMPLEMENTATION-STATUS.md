> **2026-11-14 stage B verification:** Gotenberg DOCX-to-PDF passed actual private Docker Compose conversion in [GitHub CI run 43606679093](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43606679093): synthetic DOCX converted and extracted PDF text verified. UI integration is being tested in this PR. Fifteen prototype tools targeted; E/F frozen per [Active Scope](ACTIVE-SCOPE.md).\n\n# Implementation Status and Blockers

**Updated:** 2026-11-14. This document describes **what exists**, distinct from the goal list.

## Contributor automation update

Added one local check command, canonical AI contributor instructions with Copilot/Claude/Gemini entry points, CI configuration checks, critical-test collection tracking, fail-closed report/coverage checks, structured failure summaries, and six mutation probes in disposable copies. New tests verify that the guards reject missing jobs, reduced coverage, skipped tests, malformed evidence and workflow-command injection. PyYAML 6.0.3 (MIT) is a development-only dependency. CODEOWNERS marks sensitive paths; required owner review/branch enforcement still requires administrator settings. The latest GitHub CI run is the evidence for full matrix/mutation/browser verification; local guard tests and syntax checks are available in this workspace.

## Current release-hardening implementation

Fourteen tools now have backend implementations and website controls. Added page numbering, printable-ASCII text watermarks and visual crop (explicitly not secure redaction), using ReportLab 4.4.9 (BSD) and Pillow 13.0.0 (MIT-CMU). [Deployment guide](DEPLOYMENT.md) describes a separate internal worker with read-only filesystem, no public port, no internet egress, non-root identity and CPU/memory/PID limits. API and worker each bound active uploads to two. The HTTP adapter disables proxies and redirects and never falls back to local execution if a configured worker fails.

CI now includes a real Chromium upload → merge → reuse → extract → number → download journey with reopened PDF assertions, error recovery and mobile-width checking. It runs against Compose's isolated worker, verifies read-only/non-root/no-egress boundaries and retains browser traces/screenshots. Existing matrix, coverage and dependency checks remain required. The exact latest run in GitHub Actions is the final verification evidence; browser and Docker binaries were not run locally in this restricted workspace.

The original full roadmap is **not complete**. Native editing, OCR, Office/image conversion, secure redaction, certificate signing, accounts, storage, billing and AI remain open. No public deployment was performed. TLS, authentication/per-user quotas, final license/contribution terms, complete PDF fidelity/accessibility review and container-image vulnerability scanning remain release work. See DEPLOYMENT.md for current trust boundaries.

## Current core-toolkit implementation

See [Core Toolkit](CORE-TOOLKIT.md). Eleven tools now have website controls and API implementations. New synthetic tests cover page selection, split ZIPs, page order, rotation, compression, metadata, AES-256 protection/unlock, malformed requests, process deadlines and capacity. PDF processing now runs in a child process with two concurrent slots per API process, a 25-second wall deadline, and Linux CPU/address-space limits. This is resource separation, not a complete security sandbox.

Updated dependencies: FastAPI 0.141.1, Starlette 1.6.0, python-multipart 0.0.32 and pytest 9.0.3 address the specific advisories from the previous run. Added cryptography 50.0.0 for pypdf AES encryption (Apache-2.0 OR BSD-3-Clause). No proprietary editor or incompatible copyleft library was imported. The latest commit's GitHub Actions result is the authoritative clean-install/audit check; historical failures below describe the earlier pins.

Local tests use preinstalled pypdf 6.21.4; CI uses pinned pypdf 7.0.1. Browser interaction QA, full fidelity corpus, network/filesystem worker isolation and global ingress quotas remain outstanding. The next work is to verify latest CI, add browser end-to-end coverage, isolate worker filesystem/network, then integrate audited OCR/conversion engines. Native text editing, digital signatures, secure redaction, accounts, cloud storage, billing and AI remain unimplemented; no completion claim applies to the entire roadmap.

## Earlier implementation evidence

| Workstream | Actual status | Evidence |
| --- | --- | --- |
| Product requirements / architecture | Documented | README.md and docs/ |
| Ordered implementation checklist | Documented | [Checklist](IMPLEMENTATION-CHECKLIST.md) |
| First website + API | Prototype committed | `app/main.py`, `app/static/` |
| OP-01 Merge PDF | Prototype; local output/negative tests passed | 17 synthetic tests in `tests/test_merge.py`, including text and page-order preservation |
| Raw upload limits | Implemented; 12 local regression tests passed | `app/upload_limits.py`, `tests/test_upload_limits.py`; parser isolation remains outstanding |
| Contributor CI | Running and detecting failures | [Run 43516326218](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43516326218): matrix tests, lint and packaging passed; dependency audit failed; container readiness retry corrected in follow-up |
| Previous clean CI dependency install | Verified on previous main commit | [Run 43471256283](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43471256283), commit `8e408f8` succeeded |
| Gotenberg 9 adapter | Planned | Verify its latest merge/conversion endpoints and quality |
| PDFClear and Folio imports | Not done | Audit required before any code import |
| Existing-text native PDF editing | Blocked on engine and license selection | See `docs/DECISIONS.md` |
| Other catalog tools | Planned | `docs/FEATURE-INVENTORY.md` |
| Public production deployment | Not approved | Untrusted PDF processing isolation, retention and security missing |

## What the prototype does

- Serves a same-origin HTML/CSS/JavaScript frontend and FastAPI application.
- Merges between **2 and 10 PDFs** in selected order, with **8 MB per-file** and **200 total page** limits.
- Checks PDF file signatures, rejects encrypted/invalid PDFs, and verifies page count in output.
- Returns a merged PDF for download. The application does not intentionally persist uploaded documents. Starlette/FastAPI multipart processing may spool upload data temporarily to disk.

## Verification performed

### 2026-11-14 contributor CI and upload hardening

**Remote evidence:** [GitHub run 43516326218](https://github.com/renoukhan39-bit/pdfstudio/actions/runs/43516326218), commit `85258f0`, installed the exact project pins successfully. All **29 tests passed on Python 3.11, 3.12 and 3.13**. Python 3.12 reported **97.07% branch-inclusive coverage**. Ruff, JavaScript/Python syntax, wheel/sdist build and installed-wheel smoke tests passed. Container build and non-root/asset checks passed, but the first health probe hit a startup connection reset; the follow-up uses bounded retries for all connection errors. The dependency audit correctly failed with **18 known vulnerabilities in 3 packages**; see the downloadable CycloneDX artifact. The follow-up also prints a human-readable advisory table on audit failures. Do not suppress this failure: upgrade the affected dependencies and rerun the matrix before release. The final follow-up run may still be pending at the end of this timeboxed session.

**Additional local packaging check:** `setuptools.build_meta.build_wheel('dist')` succeeded; installing that wheel with `pip --no-index --no-deps --target` and running `scripts/smoke.py` from outside the checkout passed using the preinstalled runtime dependencies.

**Audit triage:** the SBOM identifies `starlette==0.50.0`, `python-multipart==0.0.29` and development-only `pytest==9.0.2`. FastAPI 0.128.2 constrains Starlette below 0.51, so remediation must update compatible FastAPI/Starlette versions together, plus multipart and pytest, then verify the whole matrix. No advisory is ignored and the audit remains a failing required check until resolved. This dependency remediation is the immediate next task after the requested ten-minute session.

- `python -m unittest discover -s tests -p 'test_upload_limits.py' -q`: 12 passed.
- All 17 `test_*` functions in `tests/test_merge.py` executed with Python `runpy`: passed. This is a fallback because pytest installation is blocked in this workspace.
- `PYTHONPATH=. python scripts/smoke.py`: health, homepage, assets and PDF merge/order passed against the source tree.
- `python -m compileall -q app scripts tests` and `node --check app/static/app.js`: passed.
- Workflow YAML parsed; six jobs and aggregate dependencies checked.
- Local runtime: Python 3.12, FastAPI 0.141.1, pypdf 6.21.4, python-multipart 0.0.32, httpx 0.28.1. These differ from project pins. Clean install, Ruff, pytest coverage, wheel build, dependency audit and Docker verification are delegated to the new GitHub workflow; they are not claimed as locally verified.
- `python -m pip install -e '.[dev]'` in a new venv could not obtain build dependencies under workspace network restrictions. Docker and the development check tools are unavailable locally.
- No runtime dependencies or product-license choices added. Development tools: pytest-cov (MIT), Ruff (MIT), build (MIT), pip-audit (Apache-2.0); transitive/license and vulnerability review remains required.
- Before: multipart parsing occurred before size checks. After: actual raw bytes are bounded to 41 MiB and 30 seconds before parsing, with temporary buffers closed on every exit. Per-file and total byte checks also apply to direct engine calls; invalid file-count uploads are closed.

### Earlier prototype evidence

- **Local:** `PYTHONPATH=. pytest -q tests/test_merge.py` — **10 passed**.
- **Local:** Python compilation and JavaScript syntax check were performed on development copies.
- **Dependency caveat:** local checks used preinstalled `pypdf 5.9.0`; `pyproject.toml` pins the current, newer `pypdf 7.0.1`. GitHub CI must still verify the exact pinned environment and rerun tests. No live deployment or production security audit was performed.

## Blockers requiring owner/Codex follow-up

1. Select original software licensing and contribution terms.
2. Verify the expanded CI workflow; configure main's ruleset to require `CI required` and one review. Add a transitive dependency lockfile.
3. Harden uploads and sandbox PDF parsing before any public service launch.
4. Audit PDFClear and Folio before upstream integration.
5. Evaluate Gotenberg 9 as production processing backend; implement adapter if approved.
6. Select native text editor SDK/license or approve long-term engineering investment.
7. Decide hosting, privacy/retention policy, metrics and budgets.

**Next smallest task:** resolve any expanded-CI findings, then audit and implement an isolated Gotenberg adapter proof of concept with synthetic output tests. Global concurrency, reverse-proxy limits, worker CPU/memory isolation and retention controls remain release blockers.

