"""Fail closed on missing/weakened test evidence and write human/AI diagnostics."""
import html
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def annotation(value):
    return value.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')


def evaluate(junit, coverage, collected, required, minimum=54):
    errors = []
    cases = list(junit.iter('testcase'))
    failures = []
    for case in cases:
        for tag in ('failure', 'error', 'skipped'):
            issue = case.find(tag)
            if issue is not None:
                failures.append({'test': f"{case.get('classname', '')}::{case.get('name', '')}",
                                 'kind': tag, 'message': (issue.get('message') or issue.text or tag)[:2000]})
    if len(cases) < minimum or len(collected) < minimum:
        errors.append(f'Expected at least {minimum} tests; collected {len(collected)}, reported {len(cases)}. Restore test discovery.')
    missing = sorted(set(required) - set(collected))
    if missing:
        errors.append('Missing critical tests: ' + ', '.join(missing))
    if failures:
        errors.append('Tests failed, errored, or were skipped/xfail. Fix the cause; do not hide it with skip markers.')
    try:
        covered = int(coverage.get('lines-covered')) + int(coverage.get('branches-covered'))
        total = int(coverage.get('lines-valid')) + int(coverage.get('branches-valid'))
        percent = 100 * covered / total
        if total <= 0 or covered < 0 or covered > total or percent < 85:
            raise ValueError
    except (TypeError, ValueError, ZeroDivisionError):
        percent = None
        errors.append('Coverage is missing, invalid, or below the 85% branch-inclusive floor.')
    return {'ok': not errors, 'tests': len(cases), 'coverage_percent': percent, 'errors': errors,
            'failures': failures, 'reproduce': ['python', 'scripts/check.py'],
            'guide': 'docs/AI-CONTRIBUTOR-GUIDE.md'}


def main():
    reports = ROOT / 'reports'
    try:
        junit = ET.parse(reports / 'junit.xml').getroot()
        coverage = ET.parse(reports / 'coverage.xml').getroot()
        collected = json.loads((reports / 'collected-tests.json').read_text())
        required = json.loads((ROOT / 'ci/required-tests.json').read_text())
        result = evaluate(junit, coverage, collected, required)
    except (OSError, ET.ParseError, ValueError, TypeError) as exc:
        result = {'ok': False, 'errors': [f'Missing or malformed CI evidence: {exc}'], 'failures': [],
                  'reproduce': ['python', 'scripts/check.py'], 'guide': 'docs/AI-CONTRIBUTOR-GUIDE.md'}
    reports.mkdir(exist_ok=True)
    (reports / 'ci-feedback.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    lines = ['## PDF Studio test feedback', '', 'Status: ' + ('PASS' if result['ok'] else 'FAIL'), '',
             'Reproduce: `python scripts/check.py`', '',
             'For a single failure: `python -m pytest -x -vv tests/path.py::test_name`', '',
             'Full traceback: test-reports artifact → junit.xml. Machine-readable details: ci-feedback.json.', '']
    for error in result['errors']:
        print('::error title=PDF Studio CI::' + annotation(error))
        lines.append('- ' + html.escape(error))
    for failure in result['failures'][:15]:
        print('::error title=Failing test::' + annotation(failure['test'] + ': ' + failure['message'][:300]))
        lines.extend(['', '<details><summary>' + html.escape(failure['test']) + '</summary>',
                      '<pre>' + html.escape(failure['message']) + '</pre></details>'])
    summary = '\n'.join(lines) + '\n'
    (reports / 'ci-feedback.md').write_text(summary, encoding='utf-8')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
            output.write(summary)
    print('Test evidence passed.' if result['ok'] else 'Test evidence failed. Read reports/ci-feedback.json.')
    return not result['ok']


if __name__ == '__main__':
    sys.exit(main())
