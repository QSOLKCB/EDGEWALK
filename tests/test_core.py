import unittest

from edgewalk.core import (
    PHASE_EXPONENTS,
    build_tanner,
    code_parameters,
    etq_address,
    gf2_rref,
    golay_checks,
    inverse_etq_address,
    parity,
    run_walk,
    tanner_metrics,
    walk_receipt,
)


class GolayInvariantTests(unittest.TestCase):
    def test_code_parameters(self):
        self.assertEqual(code_parameters(), {
            "classicalN": 23, "classicalK": 12, "classicalD": 7,
            "quantumN": 23, "quantumK": 1, "quantumD": 7, "checkRank": 11,
        })

    def test_css_orthogonality(self):
        rows = golay_checks()
        self.assertEqual(len(gf2_rref(rows)[1]), 11)
        self.assertTrue(all(parity(a, b) == 0 for a in rows for b in rows))
        self.assertTrue(all(row.bit_count() == 8 for row in rows))

    def test_tanner_fixture(self):
        graph = build_tanner()
        metrics = tanner_metrics(graph)
        self.assertEqual(metrics["vertices"], 45)
        self.assertEqual(metrics["edges"], 176)
        self.assertEqual(metrics["directedEdges"], 352)
        self.assertEqual(sum(n.startswith("q:") for n in graph), 23)
        self.assertEqual(sum(n.startswith("x:") for n in graph), 11)
        self.assertEqual(sum(n.startswith("z:") for n in graph), 11)

    def test_crt_bijection(self):
        self.assertEqual(len({(etq_address(n)["siteIndex"], etq_address(n)["fibreLabel"]) for n in range(303)}), 303)
        for n in range(303):
            e = etq_address(n)
            self.assertEqual(inverse_etq_address(e["siteIndex"], e["fibreLabel"]), n)
        self.assertEqual(sum(PHASE_EXPONENTS) % 4, 0)
        with self.assertRaises(ValueError):
            etq_address(303)
        with self.assertRaises(ValueError):
            etq_address(True)

    def test_actual_edge_walk(self):
        graph = build_tanner()
        walk = run_walk(graph)
        self.assertEqual(len(walk), 303)
        for item in walk:
            self.assertIn(item["to"], graph[item["from"]])
            self.assertIn(item["from"], graph[item["to"]])

    def test_receipt_repeatable(self):
        left = walk_receipt()
        right = walk_receipt()
        self.assertEqual(left, right)
        self.assertEqual(len(left["sha256"]), 64)
        self.assertNotIn("ETQ/V3", left["domain"])

    def test_asymmetric_edge_rejected(self):
        graph = build_tanner()
        graph["q:00"] = tuple()
        with self.assertRaises(ValueError):
            tanner_metrics(graph)


if __name__ == "__main__":
    unittest.main()
