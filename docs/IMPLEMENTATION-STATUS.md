# Implementation Status and Blockers

**Updated:** 2026-11-13. This document describes **what exists**, distinct from the goal list.

| Workstream | Actual status | Evidence |
| --- | --- | --- |
| Product requirements / architecture | Documented | README.md and docs/ |
| Ordered implementation checklist | Documented | [Checklist](IMPLEMENTATION-CHECKLIST.md) |
| First website + API | Prototype committed | `app/main.py`, `app/static/` |
| OP-01 Merge PDF | Local tests passed | `app/pdf_engine.py`; 10 synthetic tests in `tests/test_merge.py` |
| Clean CI dependency install | Not yet verified | GitHub Actions workflow exists; clean installation results must be checked |
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

- **Local:** `PYTHONPATH=. pytest -q tests/test_merge.py` — **10 passed**.
- **Local:** Python compilation and JavaScript syntax check were performed on development copies.
- **Dependency caveat:** local checks used preinstalled `pypdf 5.9.0`; `pyproject.toml` pins the current, newer `pypdf 7.0.1`. GitHub CI must still verify the exact pinned environment and rerun tests. No live deployment or production security audit was performed.

## Blockers requiring owner/Codex follow-up

1. Select original software licensing and contribution terms.
2. Run green CI on a clean environment with exact pinned versions.
3. Harden uploads and sandbox PDF parsing before any public service launch.
4. Audit PDFClear and Folio before upstream integration.
5. Evaluate Gotenberg 9 as production processing backend; implement adapter if approved.
6. Select native text editor SDK/license or approve long-term engineering investment.
7. Decide hosting, privacy/retention policy, metrics and budgets.

**Next smallest task:** clean-install CI verification, hard ingress limits and Gotenberg adapter proof of concept, using synthetic sample PDFs only.
