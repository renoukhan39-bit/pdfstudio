"""Negative controls for the contribution gates, not tests of application internals."""
import copy
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import yaml

from scripts.ci_feedback import annotation, evaluate
from scripts.ci_guard import UniqueLoader, validate
from scripts.check_mutations import classify, mutate

ROOT = Path(__file__).resolve().parents[1]


class CiQualityTests(unittest.TestCase):
    def workflow(self):
        return yaml.load((ROOT / '.github/workflows/ci.yml').read_text(), Loader=UniqueLoader)

    def evidence(self, inner=''):
        return ET.fromstring(f'<testsuite><testcase classname="tests.synthetic" name="test_critical">{inner}</testcase></testsuite>')

    def coverage(self, covered='90'):
        return ET.fromstring(f'<coverage lines-covered="{covered}" lines-valid="100" branches-covered="0" branches-valid="0"/>')

    def report(self, inner='', collected=None, covered='90'):
        return evaluate(self.evidence(inner), self.coverage(covered), ['critical'] if collected is None else collected, ['critical'], minimum=1)

    def test_current_workflow_satisfies_policy(self):
        self.assertEqual(validate(self.workflow()), [])

    def test_required_job_cannot_disappear_or_escape_aggregate(self):
        for modification in ('delete-job', 'remove-needs', 'conditional-job', 'conditional-gate'):
            workflow = self.workflow()
            if modification == 'delete-job':
                del workflow['jobs']['integration']
            elif modification == 'remove-needs':
                workflow['jobs']['required']['needs'].remove('integration')
            elif modification == 'conditional-job':
                workflow['jobs']['tests']['if'] = 'false'
            else:
                workflow['jobs']['required']['if'] = 'success()'
            with self.subTest(modification=modification):
                self.assertTrue(validate(workflow))

    def test_coverage_matrix_and_commands_cannot_be_removed(self):
        baseline = self.workflow()
        for name in ('coverage', 'matrix', 'command'):
            workflow = copy.deepcopy(baseline)
            if name == 'coverage':
                for step in workflow['jobs']['tests']['steps']:
                    if 'run' in step:
                        step['run'] = step['run'].replace('--cov-fail-under=85', '--cov-fail-under=1')
            elif name == 'matrix':
                workflow['jobs']['tests']['strategy']['matrix']['python'] = ['3.12']
            else:
                workflow['jobs']['integration']['steps'] = []
            with self.subTest(name=name):
                self.assertTrue(validate(workflow))

    def test_unsafe_permissions_and_failure_suppression_are_rejected(self):
        for kind in ('permissions', 'trigger', 'job-continue', 'step-continue'):
            workflow = self.workflow()
            if kind == 'permissions':
                workflow['permissions']['contents'] = 'write'
            elif kind == 'trigger':
                workflow['on']['pull_request_target'] = {}
            elif kind == 'job-continue':
                workflow['jobs']['tests']['continue-on-error'] = 'true'
            else:
                workflow['jobs']['quality']['steps'][0]['continue-on-error'] = 'true'
            with self.subTest(kind=kind):
                self.assertTrue(validate(workflow))

    def test_duplicate_yaml_keys_fail_instead_of_overriding(self):
        with self.assertRaises(ValueError):
            yaml.load('jobs: {}\njobs: {}', Loader=UniqueLoader)

    def test_valid_report_passes(self):
        self.assertTrue(self.report()['ok'])

    def test_failures_errors_skips_and_xfails_fail_gate(self):
        for tag in ('failure', 'error', 'skipped'):
            with self.subTest(tag=tag):
                result = self.report(f'<{tag} message="synthetic regression"/>')
                self.assertFalse(result['ok'])
                self.assertEqual(result['failures'][0]['kind'], tag)

    def test_missing_critical_test_fails_gate(self):
        result = self.report(collected=['unrelated'])
        self.assertFalse(result['ok'])
        self.assertIn('Missing critical tests', result['errors'][0])

    def test_empty_run_and_low_coverage_fail_gate(self):
        self.assertFalse(self.report(collected=[])['ok'])
        self.assertFalse(self.report(covered='20')['ok'])
        self.assertFalse(self.report(covered='bogus')['ok'])
        empty = evaluate(ET.fromstring('<testsuite/>'), self.coverage(), ['critical'], ['critical'], minimum=1)
        self.assertFalse(empty['ok'])

    def test_annotations_cannot_inject_workflow_commands(self):
        encoded = annotation('bad%\n::warning::injected\r')
        self.assertNotIn('\n', encoded)
        self.assertNotIn('\r', encoded)
        self.assertIn('%25', encoded)
        self.assertIn('%0A', encoded)

    def test_mutation_requires_one_valid_target(self):
        self.assertEqual(mutate('value = 1', '1', '2'), 'value = 2')
        for source in ('value = 3', 'value = 11'):
            with self.assertRaises(ValueError):
                mutate(source, '1', '2')
        with self.assertRaises(SyntaxError):
            mutate('value = 1', '1', '(')

    def test_only_assertion_failure_kills_a_mutation(self):
        self.assertEqual(classify(1), 'killed')
        self.assertEqual(classify(0), 'survived')
        for code in (2, 3, 4, 5, 6, -9):
            self.assertEqual(classify(code), 'invalid-run')
