"""Review aid for accidental CI weakening, not a defense against repo administrators."""
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'quality', 'tests', 'package', 'dependencies', 'container', 'integration', 'guardrails', 'mutations'}
COMMANDS = {
    'quality': ('ruff check', 'node --check'),
    'tests': ('-m pytest', '--junitxml=', 'scripts/ci_feedback.py'),
    'package': ('-m build', 'scripts/smoke.py'),
    'dependencies': ('-m pip_audit', 'cyclonedx-json'),
    'container': ('docker build', 'docker run'),
    'integration': ('docker compose up', 'scripts/isolation_smoke.py', 'scripts/browser_smoke.py'),
    'guardrails': ('scripts/ci_guard.py',),
    'mutations': ('scripts/check_mutations.py',),
}


class UniqueLoader(yaml.BaseLoader):
    pass


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def validate(workflow):
    errors = []
    events = workflow.get('on', {})
    if not isinstance(events, dict) or not {'push', 'pull_request', 'workflow_dispatch', 'merge_group'} <= set(events):
        errors.append('Restore push, pull_request, workflow_dispatch and merge_group triggers.')
    if 'pull_request_target' in events:
        errors.append('Do not execute contributor code under pull_request_target.')
    if workflow.get('permissions') != {'contents': 'read'}:
        errors.append('Use read-only contents permission at workflow level.')
    jobs = workflow.get('jobs', {})
    if not REQUIRED <= set(jobs):
        errors.append('Restore all required jobs: ' + ', '.join(sorted(REQUIRED - set(jobs))))
    gate = jobs.get('required', {})
    if gate.get('name') != 'CI required' or gate.get('if') != 'always()':
        errors.append('Keep the CI required aggregate check named exactly and running with always().')
    if set(gate.get('needs', [])) != set(jobs) - {'required'}:
        errors.append('CI required must depend on every other job, including newly added jobs.')
    matrix = jobs.get('tests', {}).get('strategy', {}).get('matrix', {}).get('python', [])
    if not {'3.11', '3.12', '3.13'} <= set(matrix):
        errors.append('Keep the supported Python 3.11/3.12/3.13 matrix.')
    commands = '\n'.join(step.get('run', '') for step in jobs.get('tests', {}).get('steps', []))
    coverage = re.findall(r'--cov-fail-under[= ]([0-9]+)', commands)
    if not coverage or min(map(int, coverage)) < 85 or '--cov-branch' not in commands:
        errors.append('Restore branch coverage and a coverage floor of at least 85%.')
    if 'scripts/ci_feedback.py' not in commands:
        errors.append('Restore the test-report and collection guard.')
    for name, job in jobs.items():
        run_text = '\n'.join(step.get('run', '') for step in job.get('steps', []))
        for marker in COMMANDS.get(name, ()):
            if marker not in run_text:
                errors.append(f'{name}: restore the check containing {marker}.')
        if '--ignore-vuln' in run_text:
            errors.append(f'{name}: advisory exclusions require maintainer policy review, not a silent bypass.')
        if name != 'required' and 'if' in job:
            errors.append(f'{name}: required jobs cannot be conditionally skipped.')
        if job.get('continue-on-error', 'false') != 'false':
            errors.append(f'{name}: remove continue-on-error from the job.')
        if 'permissions' in job and job['permissions'] != {'contents': 'read'}:
            errors.append(f'{name}: do not elevate job permissions.')
        for step in job.get('steps', []):
            if step.get('continue-on-error', 'false') != 'false':
                errors.append(f'{name}: remove continue-on-error from check steps.')
    return errors


def main():
    try:
        workflow = yaml.load((ROOT / '.github/workflows/ci.yml').read_text(), Loader=UniqueLoader)
        errors = validate(workflow)
    except (ValueError, yaml.YAMLError, TypeError, AttributeError) as exc:
        errors = [f'Invalid workflow configuration: {exc}']
    for error in errors:
        print('CI GUARD: ' + error)
    if errors:
        print('Fix the configuration; do not disable this guard. See docs/AI-CONTRIBUTOR-GUIDE.md.')
    else:
        print('CI contract passed: required checks, coverage, triggers and permissions.')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
