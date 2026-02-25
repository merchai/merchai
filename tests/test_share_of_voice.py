"""
tests/test_share_of_voice.py
"""

import unittest

from src.metrics.share_of_voice import compute_share_of_voice


class TestComputeShareOfVoice(unittest.TestCase):

    # ── Core behaviour ────────────────────────────────────────────────────

    def test_basic_example_from_spec(self):
        result = compute_share_of_voice(["Nike", "Adidas", "Nike"])
        self.assertEqual(result, {"Nike": 0.67, "Adidas": 0.33})

    def test_scores_sum_to_1(self):
        result = compute_share_of_voice(["Nike", "Adidas", "Puma"])
        self.assertAlmostEqual(sum(result.values()), 1.0, places=1)

    def test_single_brand_gets_full_share(self):
        result = compute_share_of_voice(["Nike", "Nike", "Nike"])
        self.assertEqual(result, {"Nike": 1.0})

    def test_equal_brands_split_evenly(self):
        result = compute_share_of_voice(["A", "B"])
        self.assertEqual(result["A"], result["B"])
        self.assertEqual(result["A"], 0.5)

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(compute_share_of_voice([]), {})

    # ── Normalisation rules ───────────────────────────────────────────────

    def test_case_insensitive_counting(self):
        result = compute_share_of_voice(["nike", "NIKE", "Nike"])
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.values())[0], 1.0)

    def test_output_key_preserves_first_seen_casing(self):
        result = compute_share_of_voice(["ADIDAS", "adidas", "Adidas"])
        self.assertIn("ADIDAS", result)

    def test_strips_whitespace_from_mentions(self):
        result = compute_share_of_voice(["  Nike  ", "Nike"])
        self.assertEqual(len(result), 1)

    def test_ignores_blank_strings(self):
        result = compute_share_of_voice(["Nike", "", "  ", "Adidas"])
        self.assertNotIn("", result)
        self.assertEqual(len(result), 2)

    def test_blank_only_list_returns_empty_dict(self):
        self.assertEqual(compute_share_of_voice(["", "  ", "\t"]), {})

    # ── Output contract ───────────────────────────────────────────────────

    def test_values_rounded_to_2dp(self):
        # 1/3 = 0.333... → 0.33
        result = compute_share_of_voice(["A", "B", "C"])
        self.assertEqual(result["A"], 0.33)

    def test_returns_dict(self):
        self.assertIsInstance(compute_share_of_voice(["Nike"]), dict)

    def test_all_values_between_0_and_1(self):
        result = compute_share_of_voice(["Nike", "Adidas", "Puma", "Nike"])
        for v in result.values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)

    # ── Determinism ───────────────────────────────────────────────────────

    def test_deterministic_same_input_same_output(self):
        mentions = ["Nike", "Adidas", "Nike", "Puma", "Adidas"]
        self.assertEqual(
            compute_share_of_voice(mentions),
            compute_share_of_voice(mentions),
        )

    # ── Error handling ────────────────────────────────────────────────────

    def test_raises_on_non_list_input(self):
        with self.assertRaises(TypeError):
            compute_share_of_voice("Nike")

    def test_raises_on_non_string_element(self):
        with self.assertRaises(TypeError):
            compute_share_of_voice(["Nike", 42])


if __name__ == "__main__":
    unittest.main()