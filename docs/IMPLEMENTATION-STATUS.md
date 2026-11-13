# Implementation Status and Blockers

**Updated:** 2026-11-14. This document describes **what exists**, distinct from the goal list.

| Workstream | Actual status | Evidence |
| --- | --- | --- |
| Product requirements / architecture | Documented | README.md and docs/ |
| Ordered implementation checklist | Documented | [Checklist](IMPLEMENTATION-CHECKLIST.md) |
| First website + API | Prototype committed | `app/main.py`, `app/static/` |
| OP-01 Merge PDF | Prototype; local output/negative tests passed | 17 synthetic tests in `tests/test_merge.py`, including text and page-order preservation |
| Raw upload limits | Implemented; 12 local regression tests passed | `app/upload_limits.py`, `tests/test_upload_limits.py`; parser isolation remains outstanding |
| Contributor CI | Expanded; new workflow awaiting remote result | Matrix tests, coverage, lint, package/container smoke, dependency audit and SBOM; [CI guide](CI.md) |
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

