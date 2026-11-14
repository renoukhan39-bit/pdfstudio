"""Portable entry point for the checks every AI or human contributor must run."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true', help='Also run mutation probes, packaging and vulnerability audit.')
    options = parser.parse_args()
    python = sys.executable
    commands = [
        ('CI contract', [python, 'scripts/ci_guard.py']),
        ('Lint', [python, '-m', 'ruff', 'check', 'app', 'tests', 'scripts']),
        ('Python syntax', [python, '-m', 'compileall', '-q', 'app', 'scripts', 'tests']),
        ('JavaScript syntax', ['node', '--check', 'app/static/app.js']),
        ('Tests', [python, '-m', 'pytest', '-q', '--junitxml=reports/junit.xml', '--cov=app', '--cov-branch',
                   '--cov-report=term-missing', '--cov-report=xml:reports/coverage.xml', '--cov-fail-under=85']),
    ]
    if options.full:
        commands.extend([
            ('Mutation probes', [python, 'scripts/check_mutations.py']),
            ('Package', [python, '-m', 'build']),
            ('Dependency audit', [python, '-m', 'pip_audit', '--skip-editable']),
        ])
    for label, command in commands:
        print(f'Checking {label}: ' + ' '.join(command), flush=True)
        try:
            status = subprocess.run(command, cwd=ROOT, check=False).returncode
        except FileNotFoundError:
            print('Missing executable. Install Python dev dependencies and Node 22; see docs/AI-CONTRIBUTOR-GUIDE.md.')
            return 1
        if label == 'Tests':
            report_status = subprocess.run([python, 'scripts/ci_feedback.py'], cwd=ROOT, check=False).returncode
            status = status or report_status
        if status:
            print(f'{label} failed. Fix the reported cause, then run this command again. Do not weaken tests.')
            return status
    print('Local checks passed. GitHub also requires Docker isolation and the browser journey.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
