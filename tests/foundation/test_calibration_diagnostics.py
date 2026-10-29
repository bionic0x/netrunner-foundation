"""Independent numerical regression tests for descriptive calibration diagnostics."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ante.learn import calibration  # noqa: E402


def policy(q=0.5, registered_at='2026-01-01T00:00:00Z', floor=30):
    return calibration.parse_policy({
        'schema_version': 1, 'policy_id': 'precommitted-v1',
        'minimum_sample': floor, 'bin_edges': [0, 0.2, 0.4, 0.6, 0.8, 1],
        'baseline': {'kind': 'fixed_probability', 'probability': q,
                     'registered_at': registered_at, 'source': 'externally preserved preregistration reference'}
    })


def rows(ps, ys, distinct=True):
    return [{'p': p, 'o': y, 'decision': f'd{i}' if distinct else 'd0',
             'decided_at': '2026-10-28T12:00:00Z'} for i, (p, y) in enumerate(zip(ps, ys))]


class NumericalDiagnostics(unittest.TestCase):
    def test_brier_skill_and_murphy_reconcile(self):
        result = calibration.summarize(rows([0.7] * 4, [1, 1, 1, 0]), policy())
        self.assertAlmostEqual(.19, result['brier_score_unrounded'])
        self.assertAlmostEqual(.25, result['reference_brier_score'])
        self.assertAlmostEqual(.24, result['brier_skill_score'])
        self.assertAlmostEqual(.0025, result['murphy']['reliability'])
        self.assertAlmostEqual(0, result['murphy']['resolution'])
        self.assertAlmostEqual(.1875, result['murphy']['uncertainty'])
        self.assertAlmostEqual(.05, result['ece']['value'])
        self.assertAlmostEqual(0, result['murphy']['identity_error'], places=13)

    def test_exact_groups_preserve_murphy_identity_for_continuous_probabilities(self):
        data = rows([.04, .08, .18, .21, .33, .42, .51, .77, .87, .96],
                    [0, 0, 1, 0, 1, 0, 1, 1, 0, 1])
        r = calibration.summarize(data)
        self.assertAlmostEqual(r['brier_score_unrounded'], r['murphy']['reconstructed_brier'], places=12)
        self.assertEqual(10, r['murphy']['forecast_groups'])
        self.assertEqual(10, r['murphy']['singleton_groups'])
        self.assertIsNone(r['brier_skill_score'])
        self.assertEqual('NO_PREDECLARED_REFERENCE', r['reference_status'])

    def test_reference_zero_denominator_is_explicit_null_not_infinity(self):
        r = calibration.summarize(rows([0.25] * 30, [0] * 30), policy(q=0))
        self.assertIsNone(r['brier_skill_score'])
        self.assertEqual('ZERO_REFERENCE_BRIER', r['reference_status'])
        self.assertEqual(0, r['reference_brier_score'])

    def test_negative_skill_is_preserved(self):
        r = calibration.summarize(rows([.9] * 15 + [.1] * 15, [0] * 15 + [1] * 15), policy())
        self.assertLess(r['brier_skill_score'], 0)

    def test_late_reference_does_not_produce_bss(self):
        r = calibration.summarize(rows([.7] * 30, [1] * 30),
                                  policy(registered_at='2026-10-29T00:00:00Z'))
        self.assertIsNone(r['brier_skill_score'])
        self.assertEqual('REFERENCE_DATE_NOT_BEFORE_ALL_PREDICTIONS', r['reference_status'])

    def test_reference_registered_at_same_instant_is_not_prior(self):
        r = calibration.summarize(rows([.7] * 30, [1] * 30),
                                  policy(registered_at='2026-10-28T12:00:00Z'))
        self.assertIsNone(r['brier_skill_score'])
        self.assertEqual('REFERENCE_DATE_NOT_BEFORE_ALL_PREDICTIONS', r['reference_status'])

    def test_tied_probabilities_not_split_in_equal_mass_sensitivity(self):
        r = calibration.summarize(rows([.5] * 40, [0] * 20 + [1] * 20))
        self.assertEqual(0, r['ece']['value'])
        self.assertEqual(0, r['ece']['sensitivity']['equal_mass_5_ties_intact'])

    def test_decision_clusters_are_not_misrepresented_as_independent(self):
        r = calibration.summarize(rows([.2] * 30, [0] * 30, distinct=False))
        self.assertEqual(30, r['n'])
        self.assertEqual(1, r['distinct_decisions'])
        self.assertIsNone(r['uncertainty_interval'])

    def test_invalid_probabilities_and_binary_outcomes_fail(self):
        bad = [(float('nan'), 1), (1.01, 1), (True, 1), (.5, True), (.5, 2)]
        for p, o in bad:
            with self.subTest(p=p, o=o), self.assertRaises(calibration.CalibrationError):
                calibration.summarize(rows([p], [o]))

    def test_policy_validation_guards_floor_schema_and_edges(self):
        base = policy()['document']
        for replacement in ({'minimum_sample': 1}, {'minimum_sample': True},
                            {'schema_version': 2}, {'bin_edges': [0, .5, .5, 1]},
                            {'bin_edges': [0, .2, .8, .9]}, {'extraneous': 1}):
            with self.subTest(replacement=replacement), self.assertRaises(calibration.CalibrationError):
                calibration.parse_policy({**base, **replacement})

    def test_policy_fingerprint_is_stable_and_not_authentication(self):
        p1 = policy()
        p2 = calibration.parse_policy(json.loads(json.dumps(p1['document'], sort_keys=True)))
        self.assertEqual(p1['sha256'], p2['sha256'])
        self.assertEqual('NOT_AUTHENTICATED', calibration.policy_receipt(p1)['attestation'])


if __name__ == '__main__':
    unittest.main()
