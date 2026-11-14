"""Prove selected tests fail for known regressions in disposable source copies."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('merge-order', 'app/pdf_engine.py', 'for document in documents:', 'for document in reversed(documents):',
     'tests/test_merge.py::test_merges_in_requested_order_and_verifies_pages'),
    ('declared-upload-limit', 'app/upload_limits.py', 'if declared > self.max_bytes:', 'if False:',
     'tests/test_upload_limits.py::UploadLimitsTests::test_declared_oversize_rejected_without_reading'),
    ('chunked-upload-limit', 'app/upload_limits.py', 'if total > self.max_bytes:', 'if False:',
     'tests/test_upload_limits.py::UploadLimitsTests::test_chunked_oversize_never_reaches_parser'),
    ('weak-encryption', 'app/toolkit.py', 'algorithm="AES-256"', 'algorithm="RC4-128"',
     'tests/test_toolkit.py::ToolkitTests::test_aes256_protect_and_authorized_unlock'),
    ('ignored-remote-worker', 'app/worker.py', 'if endpoint:', 'if False:',
     'tests/test_release.py::ReleaseTests::test_remote_result_and_environment_routing'),
    ('crop-changes-media', 'app/page_decorations.py', 'page.cropbox.lower_left =', 'page.mediabox.lower_left =',
     'tests/test_release.py::ReleaseTests::test_crop_changes_viewport_not_media_or_content'),
]


def mutate(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Mutation target moved or became ambiguous; update the case while preserving its invariant.')
    result = source.replace(old, new, 1)
    ast.parse(result)
    return result


def classify(code):
    # A collection error, timeout or missing dependency is NOT a killed mutant.
    return 'killed' if code == 1 else 'survived' if code == 0 else 'invalid-run'


def main():
    results = []
    environment = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTEST_ADDOPTS', 'PDFSTUDIO_WORKER_URL'):
        environment.pop(key, None)
    with tempfile.TemporaryDirectory(prefix='.ci-mutations-', dir=ROOT) as directory:
        copy = Path(directory)
        for folder in ('app', 'tests'):
            shutil.copytree(ROOT / folder, copy / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        shutil.copy2(ROOT / 'pyproject.toml', copy / 'pyproject.toml')
        nodes = [case[4] for case in CASES]
        baseline = subprocess.run([sys.executable, '-m', 'pytest', '-q', *nodes], cwd=copy,
                                  env=environment, capture_output=True, text=True, timeout=90)
        if baseline.returncode:
            print('Baseline tests must pass before mutation verification.\n' + baseline.stdout[-3000:] + baseline.stderr[-1000:])
            return 1
        for name, filename, old, new, node in CASES:
            path = copy / filename
            source = path.read_text()
            try:
                path.write_text(mutate(source, old, new))
                # Prevent stale bytecode from hiding a same-size source edit.
                for cache in (copy / 'app').rglob('__pycache__'):
                    shutil.rmtree(cache)
                run = subprocess.run([sys.executable, '-m', 'pytest', '-q', node], cwd=copy,
                                     env=environment, capture_output=True, text=True, timeout=45)
                state = classify(run.returncode)
                results.append({'mutation': name, 'test': node, 'status': state, 'exit_code': run.returncode,
                                'diagnostic': run.stdout[-4000:] if state != 'killed' else ''})
                print(f'{name}: {state} — {node}')
            except (ValueError, SyntaxError, subprocess.TimeoutExpired) as exc:
                results.append({'mutation': name, 'test': node, 'status': 'invalid-run', 'diagnostic': str(exc)})
            finally:
                path.write_text(source)
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    (reports / 'mutations.json').write_text(json.dumps(results, indent=2))
    failed = [result for result in results if result['status'] != 'killed']
    if failed:
        print('Add or repair assertions for surviving mutations; repair setup for invalid runs. Do not delete the mutation.')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write('## Test-strength check\n\n' + '\n'.join(f"- {r['mutation']}: **{r['status']}**" for r in results) + '\n')
    return bool(failed)


if __name__ == '__main__':
    sys.exit(main())
