# Working on PDF Studio with any coding assistant

Read AGENTS.md, START-HERE, IMPLEMENTATION-STATUS and the relevant feature contract before editing. Work in a branch/PR, preserve existing tools, and implement one bounded behavior with synthetic output tests. Do not mark features shipped because an endpoint returns 200.

## One command to reproduce the core CI checks

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/check.py
# Also prove tests reject known regressions, build the package, and audit dependencies:
python scripts/check.py --full
```

Install Node 22 for the JavaScript syntax step. Docker/browser acceptance checks remain separate: follow DEPLOYMENT.md or let the required GitHub integration job run. A missing dependency or unavailable Docker is an unverified check, never a passing check.

## Failure → repair loop

1. Open the failed PR check and its job summary. Download the test-reports artifact for the Python version that failed.
2. Read `ci-feedback.json` for errors and `junit.xml` for full tracebacks. `ci-feedback.md` is the human-readable version. The JSON contains a command argument array under `reproduce`.
3. Reproduce the smallest failing test: `python -m pytest -x -vv tests/path.py::test_name` (insert `::ClassName` before a unittest method).
4. Explain the broken invariant, fix the implementation, and add a regression test if the behavior was not already covered. Reopen generated PDF/ZIP outputs and assert content, ordering, encryption or geometry as appropriate.
5. Run `python scripts/check.py`; use `--full` when changing processing, dependencies or quality controls. Push the fix and verify the latest commit's `CI required` result.
6. Report the commit, exact commands/results, limitations and next task. Never claim a command ran when only a workflow file was written.

## Checks specifically protecting future AI changes

- `CI contract` rejects removed jobs, incomplete aggregate dependencies, lower coverage floors, missing supported Python versions, elevated workflow permissions, conditional job skipping, continue-on-error and missing check commands. Duplicate YAML keys fail rather than silently replacing a job.
- Test evidence must contain at least the original 54 tests, all critical node IDs in `ci/required-tests.json`, valid branch-inclusive coverage of at least 85%, and no failures/errors/skips/xfails. Missing or malformed reports fail closed.
- `Tests reject known bugs` first verifies the baseline, then deliberately introduces six regressions in temporary copies: reversed merge order, ignored declared/chunked upload limits, weak encryption, ignored remote-worker routing and cropping that modifies the media box. Every mutant must make its targeted test fail. A timeout, import/collection failure or zero selected tests is not accepted as a killed mutation.
- Mutation targets can move during legitimate refactors. Update the probe to exercise the same invariant, explain the change in the PR and obtain review. Do not remove probes or critical tests just to get green CI.
- Unknown pytest markers/configuration fail; unexpected passes of expected-failure tests are strict failures.

## Review boundaries

No finite test suite catches every bug or judges product completeness. These checks catch specified regressions and common accidental weakening. A contributor who can change the workflow and its guard can also change the rules; tests are not a substitute for protected branches and review.

A repository administrator must require `CI required`, pull requests, at least one approval, and CODEOWNERS review for sensitive files. CODEOWNERS identifies the owner, but the workflow cannot enable those repository settings. Do not grant AI tools branch-protection bypass permissions. This change does not configure administration settings or auto-merge PRs.

Changes to tests, critical-test manifests, coverage policy, audit exclusions, workflows or this guide need a clear rationale. Keep review safeguards intact. No CI or AI tool may silently choose a product license, import incompatible code, expose the worker publicly, or claim visual cropping/whiteout is secure redaction.
