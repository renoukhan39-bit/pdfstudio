# PDF Studio repository structure

PDF Studio is a 15-tool PDF and DOCX conversion prototype. Its active product is the small FastAPI application under `app/`. AI, accounts, billing, teams, and broad automation remain future work under the A–D scope freeze in [Active Scope](docs/ACTIVE-SCOPE.md). The presence of an upstream source snapshot does not make that upstream a product dependency.

```text
pdfstudio/
├── app/                         FastAPI application and PDF worker code
│   ├── static/                  No-build HTML, CSS, and browser JavaScript
│   ├── main.py                  Public API and static-file routes
│   ├── toolkit.py               Tool registry and PDF operation dispatcher
│   ├── pdf_engine.py            PDF merge and shared size/page limits
│   ├── page_decorations.py      Numbering, watermark, visual crop
│   ├── gotenberg.py             Internal DOCX-to-PDF adapter
│   ├── upload_limits.py         Request ingress limits
│   ├── worker.py                Bounded local execution / private worker transport
│   └── worker_service.py        Private worker HTTP service
├── tests/                       Application and contributor-guard regression tests
├── scripts/                     Contributor checks and functional smoke scripts
├── ci/                          Critical test manifest consumed by check scripts
├── .github/                     The only active GitHub workflow and repository policies
├── docs/                        Product, architecture, development and quality guidance
│   └── research/                Candidate repository register and external benchmarks
├── AnalyseFuture/               Recovery records and inactive upstream snapshots
│   └── upstream-reference-snapshots/
├── Dockerfile, compose.yaml     Development containers: API, private worker, Gotenberg
├── pyproject.toml               Python package, pinned direct dependencies and tool config
├── AGENTS.md, CLAUDE.md,
│   GEMINI.md                     Conventional agent entry points
├── README.md                    Project entry point
└── PROJECT_STRUCTURE.md         This map
```

`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `THIRD_PARTY_NOTICES.md` stay at the root so contributor and legal tooling can find them. Root `.gitignore` and `.dockerignore` retain their tooling-specific roles. Most of the 24 starting `docs/*.md` files remain at known paths because contributor scripts, root guidance and cross-links use them. Two research Markdown files and the root public-repository catalog were grouped into `docs/research/`.

## How the active files work together

The browser loads `app/static/index.html`, `styles.css`, and `app.js` from `app/main.py`. The API applies `app/upload_limits.py`, validates requests, and calls `app/worker.py`. In local development the worker starts a bounded child process; in Compose it routes to `app/worker_service.py` on an internal network. `app/toolkit.py` dispatches PDF operations through `pypdf`, `app/pdf_engine.py`, and `app/page_decorations.py`. DOCX conversion uses `app/gotenberg.py` and private Gotenberg 9. The existing Python package layout, test paths, script paths, and CI command paths were kept stable; no app import was moved in this reorganization.

`pyproject.toml` packages only `app*`; Dockerfile copies only `pyproject.toml` and `app/`. `.dockerignore` excludes `AnalyseFuture/`, so the upstream snapshots and their fixtures are not sent in the container build context. Nested `.github` folders inside snapshots are historical upstream content; GitHub executes only workflows in the repository-root `.github/workflows/`.

## Where to put future work

- Add a focused active PDF operation to `app/toolkit.py` or its appropriate helper module, with corresponding `tests/` coverage and status updates in [Core Toolkit](docs/CORE-TOOLKIT.md). Split a module only when a real ownership or maintenance need warrants it, with imports and guard scripts updated together.
- Put external engine adapters alongside `app/gotenberg.py` after a recorded license/security decision, with worker and output validation. Do not copy entire upstream applications into `app/`.
- Put product contracts, roadmaps and quality guidance in `docs/`; external studies, comparisons and candidate registers belong in `docs/research/`.
- Preserve inactive experiments, branch recovery notes, uncertain assets and upstream snapshots in `AnalyseFuture/`, with origin, reason, and replacement documented. This is organization, not a secure secrets vault or permission boundary.
- Keep required CI under the root `.github/workflows/` and contributor automation in `scripts/` and `ci/`.

See [the repository audit](AnalyseFuture/REPOSITORY_AUDIT.txt), [all starting tracked paths and destinations](AnalyseFuture/COMPLETE_FILE_INVENTORY.txt), [feature inventory](AnalyseFuture/FEATURE_INVENTORY.txt), [dependency map](AnalyseFuture/DEPENDENCY_MAP.txt), [archive manifest](AnalyseFuture/ARCHIVED_FILES_MANIFEST.txt), and [validation status](AnalyseFuture/TEST_AND_VALIDATION_REPORT.txt). This reorganization deliberately did not run tests, as requested.
