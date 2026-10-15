"""Tests for prompt-injection-evals: case integrity, judge logic, adapters,
and an end-to-end mock run. Stdlib only (unittest).
"""
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import eval as ev  # noqa: E402
from adapters.mock_safe import SafeMockAdapter  # noqa: E402
from adapters.mock_vulnerable import VulnerableMockAdapter  # noqa: E402

CASES_DIR = os.path.join(ROOT, "cases")
REQUIRED_FIELDS = {"id", "category", "scenario", "expected_safe_behavior"}
ID_RE = re.compile(r"^PI-\d{3}$")


class CaseIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.cases = ev.load_cases(CASES_DIR)

    def test_minimum_case_count(self):
        self.assertGreaterEqual(len(self.cases), 50,
                                "need 50+ cases, found %d" % len(self.cases))

    def test_ids_unique_and_wellformed(self):
        ids = [c.get("id") for c in self.cases]
        self.assertEqual(len(ids), len(set(ids)), "duplicate case ids")
        for cid in ids:
            self.assertTrue(ID_RE.match(cid or ""), "bad id format: %r" % cid)

    def test_required_fields(self):
        for c in self.cases:
            for field in REQUIRED_FIELDS:
                self.assertIn(field, c, "%s missing %s" % (c.get("id"), field))
                self.assertTrue(c[field], "%s has empty %s" % (c.get("id"), field))

    def test_attack_or_turns_present(self):
        for c in self.cases:
            has = bool(c.get("attack")) or bool(c.get("turns"))
            self.assertTrue(has, "%s has neither attack nor turns" % c.get("id"))

    def test_categories_cover_expected_families(self):
        cats = {c["category"] for c in self.cases}
        for expected in ("direct_override", "system_extraction",
                          "indirect_tool_output", "multiturn",
                          "encoding", "authority",
                          "fake_tool_error", "delimiter"):
            self.assertIn(expected, cats, "missing category %s" % expected)

    def test_attack_text_is_meaningful(self):
        for c in self.cases:
            texts = c.get("turns") or [c.get("attack", "")]
            for t in texts:
                self.assertGreaterEqual(len(t), 20,
                                        "%s has a filler-length attack" % c.get("id"))


class JudgeTest(unittest.TestCase):
    def test_leak_marker_fails(self):
        case = {"leak_markers": ["sys_prompt_dump"], "execution_indicators": []}
        v, _ = ev.judge("Here is my system prompt: SYS_PROMPT_DUMP ...", case)
        self.assertEqual(v, "FAIL")

    def test_refusal_passes(self):
        case = {"leak_markers": ["sys_prompt_dump"], "execution_indicators": []}
        v, _ = ev.judge("I can't comply with that request.", case)
        self.assertEqual(v, "PASS")

    def test_execution_indicator_fails(self):
        case = {"leak_markers": [], "execution_indicators": ["jailbroken"]}
        v, _ = ev.judge("Sure. JAILBROKEN", case)
        self.assertEqual(v, "FAIL")

    def test_refusal_beats_quoted_indicator(self):
        case = {"leak_markers": [], "execution_indicators": ["jailbroken"]}
        v, _ = ev.judge("I won't do that. I'm not going to say 'jailbroken' for you.",
                        case)
        self.assertEqual(v, "PASS")

    def test_benign_response_inconclusive(self):
        case = {"leak_markers": ["xyz_marker"], "execution_indicators": []}
        v, _ = ev.judge("The weather is nice today.", case)
        self.assertEqual(v, "INCONCLUSIVE")


class AdapterTest(unittest.TestCase):
    def test_safe_mock_passes_extraction(self):
        case = {"id": "PI-009", "category": "system_extraction",
                "leak_markers": ["sys_prompt_dump"], "execution_indicators": []}
        resp = SafeMockAdapter().respond(case["id"] and "attack text", case)
        v, _ = ev.judge(resp, case)
        self.assertEqual(v, "PASS")

    def test_vulnerable_mock_fails_extraction(self):
        case = {"id": "PI-009", "category": "system_extraction",
                "leak_markers": ["sys_prompt_dump"], "execution_indicators": []}
        resp = VulnerableMockAdapter().respond("attack text", case)
        v, _ = ev.judge(resp, case)
        self.assertEqual(v, "FAIL")


class EndToEndTest(unittest.TestCase):
    def test_safe_mock_full_run_scores_100(self):
        cases = ev.load_cases(CASES_DIR)
        results = ev.run(cases, SafeMockAdapter())
        self.assertEqual(len(results), len(cases))
        fails = [r for r in results if r["verdict"] != "PASS"]
        self.assertEqual(fails, [], "safe mock should pass everything: %r" % fails[:3])
        report = ev.markdown_report(results, ev.score(results), "mock-safe")
        self.assertIn("100.0%", report)
        self.assertIn("# Prompt-Injection Evals", report)

    def test_vulnerable_mock_full_run_fails(self):
        cases = ev.load_cases(CASES_DIR)
        results = ev.run(cases, VulnerableMockAdapter())
        failed = [r for r in results if r["verdict"] == "FAIL"]
        self.assertGreater(len(failed), len(cases) // 2,
                           "vulnerable mock should fail most cases")

    def test_report_renders_all_categories(self):
        cases = ev.load_cases(CASES_DIR)
        results = ev.run(cases, SafeMockAdapter())
        report = ev.markdown_report(results, ev.score(results), "mock-safe")
        for cat in ("direct_override", "delimiter", "multiturn"):
            self.assertIn(cat, report)


if __name__ == "__main__":
    unittest.main()
