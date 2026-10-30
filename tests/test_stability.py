"""v0.3 spectral-stability tests; synthetic graphs are not canonical ETQ input."""
import unittest

from edgewalk.core import build_tanner
from edgewalk.stability import (
    _bp_map, bethe_hessian, bp_fixed_point_probe, bp_messages,
    bp_update_and_jacobian, laplacian_projectors, nonbacktracking_modes,
    nonbacktracking_operator, paired_bethe_perturbation, stability_report,
    symmetric_spectrum, verify_etq_spectral_shift,
)


def cycle(vertices):
    n = len(vertices)
    return {vertices[i]: tuple(sorted((vertices[(i - 1) % n], vertices[(i + 1) % n])))
            for i in range(n)}


def cartesian_303():
    """Synthetic cycle Cartesian C3; NOT original E8 adjacency."""
    base = {j: {(j-1) % 101, (j+1) % 101} for j in range(101)}
    graph = {}
    for j in range(101):
        for a in range(3):
            graph[str(3*j+a)] = tuple(sorted(
                {str(3*k+a) for k in base[j]} |
                {str(3*j+b) for b in range(3) if b != a}, key=int))
    return graph


try:
    import numpy
    import scipy
    NUMERICAL_AVAILABLE = True
except ImportError:
    NUMERICAL_AVAILABLE = False


@unittest.skipUnless(NUMERICAL_AVAILABLE, "v0.3 NumPy/SciPy extras not installed")
class SpectralStabilityTests(unittest.TestCase):
    def test_nonbacktracking_oriented_edges_and_no_immediate_reversal(self):
        graph = cycle(("a","b","c","d"))
        arcs, b = nonbacktracking_operator(graph)
        self.assertEqual(len(arcs), 8)
        self.assertEqual(b.nnz, 8)
        for i,(u,v) in enumerate(arcs):
            for j in b.getrow(i).indices:
                self.assertEqual(arcs[j][0],v)
                self.assertNotEqual(arcs[j][1],u)
        spec = nonbacktracking_modes(graph)
        self.assertAlmostEqual(spec["modes"][0]["magnitude"],1,places=10)
        self.assertLess(spec["modes"][0]["residualL2"],1e-8)
        with self.assertRaises(ValueError):
            nonbacktracking_modes(graph,modes=0)

    def test_bethe_hessian_formula(self):
        graph = cycle(("a","b","c","d"))
        r, matrix = bethe_hessian(graph,r=2)
        self.assertEqual(r,2)
        self.assertAlmostEqual(matrix[0,0],5)
        self.assertEqual(matrix[0,1],-2)
        summary = symmetric_spectrum(graph,r=2)
        self.assertEqual(summary["negativeEigenvalueCountFull"],0)
        self.assertEqual(summary["size"],4)
        with self.assertRaises(ValueError):
            bethe_hessian(graph,r=float("nan"))

    def test_degenerate_projector_is_rotation_invariant(self):
        result = laplacian_projectors(cycle(("a","b","c","d")))
        twice = [g for g in result["groups"] if abs(g["eigenvalue"]-2)<1e-8]
        self.assertEqual(len(twice),1)
        self.assertEqual(twice[0]["multiplicity"],2)
        for diagonal in twice[0]["projectorDiagonal"]:
            self.assertAlmostEqual(diagonal,0.5,places=9)
        self.assertAlmostEqual(twice[0]["effectiveVertexSupport"],4,places=9)
        self.assertLess(twice[0]["traceError"],1e-9)
        self.assertLess(twice[0]["idempotenceResidualFro"],1e-9)
        with self.assertRaises(ValueError):
            laplacian_projectors(cycle(("a","b","c","d")),atol=-1)

    def test_etq_shift_topology_and_numeric_residual(self):
        graph = cartesian_303()
        output = verify_etq_spectral_shift(graph)
        self.assertTrue(output["topologyExact"])
        self.assertEqual(output["predictedShifts"],[0,3,3])
        self.assertLess(output["maxAbsEigenvalueShiftError"],1e-9)
        changed = dict(graph)
        changed["0"] = tuple(x for x in changed["0"] if x!="1")
        changed["1"] = tuple(x for x in changed["1"] if x!="0")
        with self.assertRaisesRegex(ValueError,"Cartesian"):
            verify_etq_spectral_shift(changed)

    def test_bp_channels_and_analytic_jacobian_finite_difference(self):
        _, _, x_arcs = bp_messages("x")
        _, _, z_arcs = bp_messages("z")
        self.assertEqual(len(x_arcs),88)
        self.assertEqual(len(z_arcs),88)
        self.assertTrue(all(c.startswith("x:") for _,c in x_arcs))
        self.assertTrue(all(c.startswith("z:") for _,c in z_arcs))
        x = bp_update_and_jacobian("x",message=1.0)
        z = bp_update_and_jacobian("z",message=1.0)
        self.assertAlmostEqual(x["localJacobianSpectralRadius"],z["localJacobianSpectralRadius"])
        import numpy as np
        trial = np.full(len(x_arcs),1.0)
        f, jac = _bp_map("x",trial,0.5)
        self.assertTrue(np.allclose(jac,x["jacobian"]))
        col = 7
        perturbed = trial.copy()
        perturbed[col] += 1e-5
        fp, _ = _bp_map("x",perturbed,0.5)
        self.assertLess(np.max(np.abs((fp-f)/1e-5-jac[:,col])),1e-5)
        with self.assertRaises(ValueError):
            bp_messages("both")

    def test_bp_fixed_point_unqualified_is_not_called_stable(self):
        fixed = bp_fixed_point_probe("x")
        self.assertTrue(fixed["fixedPointQualified"])
        self.assertLessEqual(fixed["fixedPointResidualInfinity"],1e-10)
        self.assertTrue(fixed["locallyAttracting"])
        stalled = bp_fixed_point_probe("x",max_iterations=1,atol=1e-14)
        self.assertFalse(stalled["fixedPointQualified"])
        self.assertIsNone(stalled["locallyAttracting"])

    def test_paired_perturbation_monotonicity_and_determinism(self):
        graph = build_tanner()
        parts = {node:"q" if node.startswith("q:") else "check" for node in graph}
        result = paired_bethe_perturbation(graph,epsilon=0.01,swaps=5,partition=parts)
        self.assertEqual(result["anchorVertex"],"q:00")
        for row in result["systems"].values():
            self.assertGreaterEqual(row["delta"],-1e-9)
        self.assertEqual(result,paired_bethe_perturbation(graph,epsilon=0.01,swaps=5,partition=parts))
        with self.assertRaises(ValueError):
            paired_bethe_perturbation(graph,epsilon=-0.01)

    def test_full_report_is_auxiliary_on_synthetic_graph(self):
        from edgewalk.etq import ETQBundle, ETQ_EVENT_SHA, ETQ_EDGES_SHA
        # Fake source refs in this test are never accepted by load_etq_bundle.
        etq = ETQBundle(adjacency=cartesian_303(),events=tuple(),artifact_sha256={},
                        event_document_receipt=ETQ_EVENT_SHA,graph_edges_receipt=ETQ_EDGES_SHA)
        result = stability_report(etq,include_nonbacktracking=False,swaps=4)
        self.assertFalse(result["identityBearing"])
        self.assertTrue(result["systems"]["etq"]["cartesianShiftVerification"]["topologyExact"])
        self.assertEqual(result["systems"]["golay"]["bpChannels"]["x"]["fixedPoint"]["messages"],88)
        self.assertNotIn("nonBacktrackingModes",result["systems"]["etq"])
        self.assertEqual(result["schema"],"edgewalk.stability.v0.3/auxiliary")


if __name__ == "__main__":
    unittest.main()
