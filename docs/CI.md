# Contributor checks and failure recovery

Every pull request, main-branch push, merge-queue entry and manual run executes
`.github/workflows/ci.yml`. No secrets or paid services are required. Fork PRs
use `pull_request`, never `pull_request_target`, with read-only permissions.
GitHub may require a maintainer to approve a first-time contributor's run.

## Local reproduction

Use Python 3.11–3.13 and Node 22 (JavaScript syntax checking only):

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pip check
python -m ruff check app tests scripts
node --check app/static/app.js
python -m pytest -q --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=85
python -m build
python -m pip_audit --skip-editable
```

## What fails a contribution

| Check | Failure means | Where to investigate |
| --- | --- | --- |
| Lint and syntax | Undefined/unused names, invalid Python or JavaScript | File and line printed in log |
| Tests (Python 3.11/3.12/3.13) | Broken behavior, output PDF mismatch, unsafe input accepted, coverage below 85% | Failed assertion and uploaded JUnit/coverage reports |
| Package and installed-app smoke test | Packaging broken, missing assets, installed merge fails | Build log and `scripts/smoke.py` |
| Dependency audit | Known vulnerability or scanner failure | Audit log and CycloneDX artifact; upgrade affected packages and rerun tests |
| Container smoke test | Image cannot build/start, runs as root, assets missing | Docker logs in the cleanup step |
| Isolated worker and browser journey | Worker network/filesystem isolation, upload/download or chaining fails | Compose logs and uploaded Playwright trace |
| CI required | Any required job failed, was cancelled or skipped | Open the corresponding job above |

Open the PR's **Checks** tab, select the failed job, reproduce its command, fix
the cause, and push another commit. Do not lower coverage or ignore an advisory
just to make CI green. Reports are kept for seven days. Superseded runs are
cancelled to conserve Actions usage. Dependabot proposes weekly Python, Actions
and Docker updates; it does not merge them automatically.

## Merge policy and repository setting

Require a focused PR, one review, and **CI required** before merging to main.
A workflow reports failure but cannot itself enforce branch protection. A
repository administrator must configure a main-branch ruleset requiring pull
requests, one approving review, and the exact status check `CI required`.
The current change does not modify repository administration settings.

## Scope and remaining work

CI verifies the merge prototype and ingress protections. It does not prove
browser accessibility, hostile-PDF sandboxing, complete license compliance or
production readiness. Direct dependencies are pinned; transitive resolution is
not yet locked. The CycloneDX file inventories installed packages, not the
complete container OS. Add a reviewed lockfile and container-level scanning next.
Original-code licensing and contribution terms still need an owner decision.

Run the browser checks locally with `pip install -e ".[dev,browser]"`, `python -m playwright install chromium`, `docker compose up --build -d --wait`, then `python scripts/browser_smoke.py`. CI uses Ubuntu 24.04 for browser dependency compatibility.
