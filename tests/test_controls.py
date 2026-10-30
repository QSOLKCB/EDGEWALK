"""v0.4 controls regression suite; synthetic ETQ is never a released fixture."""
import unittest
from edgewalk.controls import (
    METRICS, VARIANTS, _CounterRNG, _graph, _rewire,
    build_basis_tanner, etq_base, four_cycles, graph_sha256, lift_etq,
    run_controlled_experiment, replay_experiment_receipt, trace_a4,
)


def synthetic_product():
    base = {str(i): tuple(sorted((str((i-1)%101),str((i+1)%101))))
            for i in range(101)}
    return lift_etq(base), base


class ControlledSpectralTests(unittest.TestCase):
    def test_distinct_golay_bases_preserve_css_and_relabel_topology(self):
        from edgewalk.core import golay_checks, gf2_rref, parity
        checks = golay_checks()
        self.assertEqual(len(gf2_rref(checks)[1]),11)
        self.assertTrue(all(parity(a,b)==0 for a in checks for b in checks))
        digests=[]
        for variant in VARIANTS:
            graph=build_basis_tanner(variant)
            self.assertEqual(len(graph),45)
            self.assertEqual(sum(len(row) for row in graph.values())%2,0)
            digests.append(graph_sha256(graph))
        self.assertEqual(len(set(digests)),3)

    def test_four_cycle_and_exact_trace_a4(self):
        graph={'a':('b','d'),'b':('a','c'),'c':('b','d'),'d':('a','c')}
        self.assertEqual(four_cycles(graph),1)
        self.assertEqual(trace_a4(graph),32)
        self.assertEqual(trace_a4({'a':('b',),'b':('a',)}),2)

    def test_control_degree_and_channel_constraints(self):
        graph=build_basis_tanner('reference')
        result, attempts=_rewire(graph,6,_CounterRNG(123),channelized=True)
        self.assertGreaterEqual(attempts,6)
        self.assertNotEqual(result,graph)
        self.assertEqual({a:len(row) for a,row in result.items()},
                         {a:len(row) for a,row in graph.items()})
        self.assertTrue(all(a.startswith('q:')!=b.startswith('q:')
                            for a,row in result.items() for b in row))
        self.assertEqual(result,_rewire(graph,6,_CounterRNG(123),channelized=True)[0])
        for q in (a for a in graph if a.startswith('q:')):
            for kind in ('x:','z:'):
                self.assertEqual(sum(b.startswith(kind) for b in graph[q]),
                                 sum(b.startswith(kind) for b in result[q]))

    def test_reproducible_receipt_and_bootstrap_isolation(self):
        first=run_controlled_experiment(ensemble_size=4,swaps=2,seed=4,bootstrap_draws=32)
        larger_bootstrap=run_controlled_experiment(ensemble_size=4,swaps=2,seed=4,bootstrap_draws=256)
        second_seed=run_controlled_experiment(ensemble_size=4,swaps=2,seed=5,bootstrap_draws=32)
        self.assertEqual(first['sha256'],larger_bootstrap['sha256'])
        self.assertNotEqual(first['sha256'],second_seed['sha256'])
        self.assertNotEqual(first['exploratoryAnalysis'],larger_bootstrap['exploratoryAnalysis'])
        self.assertEqual(first['exploratoryAnalysis']['familySize'],12)
        self.assertEqual(set(first['exactEvidence']['systems']),{'golay/'+v for v in VARIANTS})
        for entry in first['exactEvidence']['systems'].values():
            self.assertEqual(len({c['graphSha256'] for c in entry['controls']}),4)
            self.assertEqual(set(entry['observed']),set(METRICS))
            self.assertTrue(all(type(v) is int for v in entry['observed'].values()))

    def test_exact_replay_and_tamper_rejection(self):
        report=run_controlled_experiment(ensemble_size=4,swaps=3,
                                         seed=9,bootstrap_draws=32)
        self.assertTrue(replay_experiment_receipt(report))
        report["exploratoryAnalysis"]["warning"]="different explanation"
        self.assertTrue(replay_experiment_receipt(report))  # not identity-bearing
        report["exactEvidence"]["systems"]["golay/reference"]["observed"]["fourCycles"]+=1
        self.assertFalse(replay_experiment_receipt(report))

    def test_etq_product_preserving_nulls(self):
        full,base=synthetic_product()
        self.assertEqual(etq_base(full),_graph(base))
        self.assertEqual(len(full),303)
        class Synthetic:
            adjacency=full
            events=tuple()
            event_document_receipt='synthetic-not-etq'
            graph_edges_receipt='synthetic-not-etq'
            artifact_sha256={}
        report=run_controlled_experiment(Synthetic(),ensemble_size=4,swaps=2,
                                          seed=7,bootstrap_draws=32,variants=('reference',))
        self.assertEqual(set(report['exactEvidence']['systems']),{'golay/reference','etq/product'})
        self.assertEqual(report['exactEvidence']['systems']['etq/product']['nullConstraint'],
                         'base-101-degree-preserving-cartesian-lift')
        broken={k:tuple(v) for k,v in full.items()}
        broken['0']=tuple(x for x in broken['0'] if x!='1')
        broken['1']=tuple(x for x in broken['1'] if x!='0')
        with self.assertRaisesRegex(ValueError,'Cartesian'):
            etq_base(broken)

    def test_reject_invalid_configs(self):
        for options in ({'ensemble_size':3},{'swaps':0},{'seed':-1},
                        {'bootstrap_draws':5},{'variants':('reference','reference')},
                        {'ensemble_size':True},{'variants':('unknown',)}):
            with self.subTest(options=options),self.assertRaises(ValueError):
                run_controlled_experiment(**options)


if __name__=='__main__':
    unittest.main()
