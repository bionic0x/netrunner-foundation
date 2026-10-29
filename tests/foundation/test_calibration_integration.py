"""Integration regressions for new calibration policy and historical --at cutoff.

Uses the existing Foundation test fixture, preserving its real ledger, artifacts,
reconciliation rules, and CLI. No synthetic data enters the live statistics.
"""
import contextlib
import io
import json
import unittest

from test_learn import Workspace, decide_artifact
from ante import cli
from ante.learn import commands, ledger


class CalibrationIntegration(Workspace):
    def test_reconciliations_in_future_not_visible_to_prior_calibration(self):
        art = decide_artifact('point-in-time')
        first = self.record(art)
        self.observe(art, 'CONFIRMED', at='2026-12-02T00:00:00Z')
        before = commands.calibrate(self.ledger, '2026-11-01T00:00:00Z', min_sample=1)
        self.assertEqual(0, before['decisive_predictions'])
        self.assertEqual(first['entry_hash'], before['ledger_head'])
        after = commands.calibrate(self.ledger, '2026-12-31T00:00:00Z', min_sample=1)
        self.assertEqual(1, after['decisive_predictions'])
        self.assertAlmostEqual(.09, after['groups'][0]['brier'])

    def test_policy_floor_counts_distinct_decisions_not_just_many_predictions(self):
        base = decide_artifact('cluster', expectations=[{
            'id': f'e{i}', 'what_should_change': 'x', 'in_whom': 'y',
            'horizon': '2026-12-01T00:00:00Z', 'refuted_by': 'z',
            'probability': {'verbal': 'likely', 'interval': [0.6, 0.8]}
        } for i in range(30)])
        self.record(base)
        # One observation per prediction: 30 rows from just ONE originating decision.
        for i in range(30):
            self.observe(base, 'CONFIRMED', expectation=f'e{i}',
                         at=f'2026-12-02T00:{i:02d}:00Z')
        policy_doc = {'schema_version': 1, 'policy_id': 'locked-test',
                      'minimum_sample': 30, 'bin_edges': [0, .2, .4, .6, .8, 1],
                      'baseline': None}
        p = self.write('policy.json', policy_doc)
        report = commands.calibrate(self.ledger, '2026-12-31T00:00:00Z', min_sample=1,
                                    policy_path=p)
        self.assertEqual(30, report['decisive_predictions'])
        self.assertEqual(30, report['min_sample'])
        self.assertEqual('INSUFFICIENT_SAMPLE', report['groups'][0]['result'])
        self.assertEqual(1, report['groups'][0]['distinct_decisions'])
        self.assertIsNone(report['groups'][0]['brier'])

    def test_cli_optional_policy_is_still_offline_and_validates_format(self):
        art = decide_artifact('cli-calibration')
        self.record(art)
        self.observe(art, 'CONFIRMED')
        doc = {'schema_version': 1, 'policy_id': 'locked-test', 'minimum_sample': 30,
               'bin_edges': [0, .2, .4, .6, .8, 1], 'baseline': None}
        p = self.write('policy.json', doc)
        std = io.StringIO()
        with contextlib.redirect_stdout(std):
            rc = cli.main(['learn', 'calibrate', '--ledger', self.ledger, '--at',
                           '2026-12-31T00:00:00Z', '--policy', p, '--min-sample', '1'])
        self.assertEqual(0, rc)
        result = json.loads(std.getvalue())
        self.assertEqual('POLICY_DECLARED_NOT_AUTHENTICATED', result['analysis_mode'])
        self.assertEqual('INSUFFICIENT_SAMPLE', result['groups'][0]['result'])
        self.assertEqual(30, result['min_sample'])


if __name__ == '__main__':
    unittest.main()
