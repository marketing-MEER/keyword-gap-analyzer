import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from keyword_gap_analyzer import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"

YOU = """Keyword,Volume,Current position,Current URL
crm software,1000,3,https://me.com/crm
free crm,500,15,https://me.com/free
crm for real estate agents,200,2,https://me.com/re
"""
RIVAL_A = """Keyword,Position,Search Volume,URL
crm software,1,1000,https://www.a.com/crm
free crm,4,500,https://www.a.com/free
best crm for small business owners in 2026,6,300,https://www.a.com/best
crm pricing,5,800,https://www.a.com/pricing
"""
RIVAL_B = """Keyword,Position,Search Volume,URL
crm software,7,1000,https://b.io/crm
free crm,2,500,https://b.io/free
crm pricing,9,800,https://b.io/pricing
"""


class CoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        for name, text in [("you", YOU), ("a", RIVAL_A), ("b", RIVAL_B)]:
            (d / f"{name}.csv").write_text(text, encoding="utf-8")
        self.table, self.me, self.names = core.analyze(d / "you.csv", [d / "a.csv", d / "b.csv"])
        self.t = self.table.set_index("keyword")

    def tearDown(self):
        self.tmp.cleanup()

    def test_site_names_from_urls(self):
        self.assertEqual(self.me, "me.com")
        self.assertEqual(self.names, ["a.com", "b.io"])

    def test_gap_types(self):
        self.assertEqual(self.t.at["crm software", "gap"], "shared")       # 3 is between 1 and 7
        self.assertEqual(self.t.at["free crm", "gap"], "weak")             # 15 is below 4 and 2
        self.assertEqual(self.t.at["crm for real estate agents", "gap"], "strong")
        self.assertEqual(self.t.at["crm pricing", "gap"], "missing")       # two rivals, not you
        self.assertEqual(self.t.at["best crm for small business owners in 2026", "gap"], "untapped")

    def test_revenue_score_weights_long_keywords(self):
        # 2-word keyword is weighted ~0.1x, 8-word keyword ~1.06x (NP revenue share by length)
        self.assertAlmostEqual(self.t.at["free crm", "revenue_score"], round(500 * 4.76 / 46.29, 1))
        self.assertAlmostEqual(self.t.at["best crm for small business owners in 2026", "revenue_score"],
                               round(300 * 48.95 / 46.29, 1))
        self.assertTrue(self.t.at["best crm for small business owners in 2026", "comparison_intent"])
        self.assertFalse(self.t.at["free crm", "comparison_intent"])

    def test_best_competitor(self):
        self.assertEqual(self.t.at["free crm", "best_competitor"], "b.io")
        self.assertEqual(self.t.at["crm for real estate agents", "best_competitor"], "")

    def test_summary_counts_every_keyword_once(self):
        self.assertEqual(core.summary(self.table)["keywords"].sum(), len(self.table))


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gap"
            args = [str(EXAMPLES / f) for f in ["brightcrm_keywords.csv", "pipelinehq_keywords.csv",
                                                 "salesdeck_keywords.csv"]] + ["-o", str(out)]
            res = CliRunner().invoke(cli.main, args)
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("Keyword gap report", out.with_suffix(".html").read_text(encoding="utf-8"))
            self.assertTrue(out.with_suffix(".xlsx").exists())


if __name__ == "__main__":
    unittest.main()
