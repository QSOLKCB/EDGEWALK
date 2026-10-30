"""EDGEWALK v0.2 integration tests.

Fixture is deliberately synthetic; mocked semantic receipts do NOT validate ETQ.
A genuine SONIFICATION build:v3 bundle remains the required end-to-end gate.
"""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from edgewalk.core import build_tanner, etq_address
from edgewalk.analysis import (validated_walk, walk_stats, exact_spectral_moments,
                               degree_preserving_control, compare, auxiliary_spectral)
from edgewalk.etq import load_etq_bundle, ETQBundle, ETQ_EVENT_SHA, ETQ_EDGES_SHA
from edgewalk import etq as etqmod


def synthetic_bundle(folder):
    """Havel-Hakimi graph with published degrees, not actual E8 adjacency."""
    distribution = {22:12,23:6,30:12,32:24,33:12,34:6,40:6,42:12,43:6,44:3,55:2}
    degrees = [d for d, count in distribution.items() for _ in range(count)]
    pending = [(d, i) for i, d in enumerate(degrees)]
    base = [set() for _ in range(101)]
    while pending:
        pending.sort(key=lambda item: (-item[0], item[1]))
        degree, site = pending.pop(0)
        assert 0 <= degree <= len(pending)
        for k in range(degree):
            other_degree, other_site = pending[k]
            pending[k] = (other_degree - 1, other_site)
            base[site].add(other_site)
            base[other_site].add(site)
    edges = []
    for fibre in range(3):
        for site, row in enumerate(base):
            for other in row:
                if site < other:
                    edges.append({"source": 3*site+fibre, "target": 3*other+fibre,
                                  "kind": "base-e8-edge"})
    for site in range(101):
        for a,b in ((0,1),(0,2),(1,2)):
            edges.append({"source":3*site+a,"target":3*site+b,"kind":"fibre-c3-edge"})
    edges.sort(key=lambda edge:(edge["source"],edge["target"]))
    degree=[0]*303
    for edge in edges:
        degree[edge["source"]]+=1
        degree[edge["target"]]+=1
    nodes=[{"tensorIndex":i,"siteIndex":i//3,"fibreLabel":i%3,
            "liftedDegree":degree[i]} for i in range(303)]
    graph={"modelId":"ETQ-303","modelVersion":"3.0.0",
           "schema":"qsol.etq-303.graph-receiver/v1",
           "construction":"cartesian-product-G101-square-C3",
           "vertexCount":303,"edgeCount":len(edges),"connected":True,
           "nodes":nodes,"edges":edges}
    events=[]
    for n in range(303):
        addr=etq_address(n)
        events.append({"sequenceIndex":n,"siteIndex":addr["siteIndex"],
                       "fibreLabel":addr["fibreLabel"],"tensorIndex":addr["tensorIndex"],
                       "transitionPhaseGaussianExponent":addr["phaseExponent"],
                       "transitionPhaseSymbol":addr["phaseSymbol"],
                       "nextSequenceIndex":(n+1)%303,
                       "nextTensorIndex":etq_address((n+1)%303)["tensorIndex"]})
    ev={"modelId":"ETQ-303","modelVersion":"3.0.0",
        "profile":"full-qutrit-event-protocol-v1",
        "schema":"qsol.etq-303.events/v1","events":events,
        "graphContext":{"eventTraversalIsGraphWalk":False},
        "exactStep":{"gaussianExponents":[3,2,3],
                     "gaussianPhaseSymbols":["-i","-1","-i"]}}
    domains={"eventDocument":"ETQ/V3/EVENT-DOCUMENT/v1",
             "liftedEdges":"ETQ/V3/LIFTED-EDGES/v1",
             "events":"ETQ/V3/EVENTS/v1","manifest":"ETQ/V3/MANIFEST/v1"}
    co={"modelId":"ETQ-303","modelVersion":"3.0.0",
        "profile":"full-qutrit-event-protocol-v1",
        "determinism":{"eventDocumentSha256":ETQ_EVENT_SHA,
                       "liftedEdgesSha256":ETQ_EDGES_SHA,
                       "eventsSha256":"x","hashDomains":domains}}
    artifacts=[]
    for name, document in (("contract.json",co),("events.json",ev),("graph.json",graph)):
        raw=json.dumps(document).encode()
        (Path(folder)/name).write_bytes(raw)
        artifacts.append({"filename":name,"sha256":hashlib.sha256(raw).hexdigest(),
                          "byteLength":len(raw)})
    manifest={"modelId":"ETQ-303","modelVersion":"3.0.0",
              "profile":"full-qutrit-event-protocol-v1",
              "schema":"qsol.etq-303.manifest/v1",
              "artifacts":artifacts,"manifestCoreSha256":"mock"}
    (Path(folder)/"manifest.json").write_text(json.dumps(manifest))


def mocked_receipt(domain, data):
    if "EVENT-DOCUMENT" in domain:
        return ETQ_EVENT_SHA
    if "LIFTED-EDGES" in domain:
        return ETQ_EDGES_SHA
    if "EVENTS" in domain:
        return "x"
    return "mock"


class V02Tests(unittest.TestCase):
    def test_golay_verified_walk_and_bipartite_control(self):
        graph=build_tanner()
        walk=validated_walk(graph,"q:00")
        self.assertEqual(len(walk),303)
        self.assertTrue(all(step["target"] in graph[step["source"]] for step in walk))
        self.assertLessEqual(walk_stats(walk)["visitedVertices"],45)
        partitions={node:"qubit" if node.startswith("q:") else "check" for node in graph}
        control=degree_preserving_control(graph,16,partitions)
        self.assertNotEqual(control,graph)
        self.assertEqual({k:len(v) for k,v in control.items()},
                         {k:len(v) for k,v in graph.items()})
        self.assertTrue(all(partitions[a]!=partitions[b] for a,row in control.items() for b in row))
        self.assertEqual(control,degree_preserving_control(graph,16,partitions))
        self.assertEqual(exact_spectral_moments(control)["adjacencyTraceA2"],352)

    def test_reproducible_cross_domain_comparison(self):
        # A purely synthetic symmetric cycle-square graph for fast walk tests.
        graph={str(i):tuple(str((i+d)%303) for d in (-2,-1,1,2)) for i in range(303)}
        etq=ETQBundle(graph,tuple(),{"graph.json":"synthetic"},ETQ_EVENT_SHA,ETQ_EDGES_SHA)
        first=compare(etq,swaps=5)
        self.assertEqual(first["sha256"],compare(etq,swaps=5)["sha256"])
        self.assertEqual(first["payload"]["comparisons"]["etq"]["graph"]["edges"],606)
        self.assertEqual(first["payload"]["comparisons"]["etq"]["walk"]["steps"],303)

    def test_missing_bundle_rejected(self):
        with TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                load_etq_bundle(d)

    def test_synthetic_bundle_cannot_impersonate_published_etq(self):
        with TemporaryDirectory() as d:
            synthetic_bundle(d)
            with self.assertRaisesRegex(ValueError,"event document semantic receipt"):
                load_etq_bundle(d)

    def test_synthetic_mocked_receipt_exercises_adapter_shape_only(self):
        with TemporaryDirectory() as d:
            synthetic_bundle(d)
            with patch.object(etqmod,"_domain_hash",side_effect=mocked_receipt):
                etq=load_etq_bundle(d)
            self.assertEqual(len(etq.events),303)
            self.assertEqual(sum(map(len,etq.adjacency.values()))//2,5364)
            self.assertEqual(len(compare(etq,swaps=3)["sha256"]),64)

    def test_node_metadata_corruption_rejected_even_if_hash_mocked(self):
        with TemporaryDirectory() as d:
            synthetic_bundle(d)
            graphfile=Path(d)/"graph.json"
            graph=json.loads(graphfile.read_text())
            graph["nodes"][0]["liftedDegree"]+=1
            raw=json.dumps(graph).encode()
            graphfile.write_bytes(raw)
            manifestfile=Path(d)/"manifest.json"
            manifest=json.loads(manifestfile.read_text())
            for row in manifest["artifacts"]:
                if row["filename"]=="graph.json":
                    row["sha256"]=hashlib.sha256(raw).hexdigest()
                    row["byteLength"]=len(raw)
            manifestfile.write_text(json.dumps(manifest))
            with patch.object(etqmod,"_domain_hash",side_effect=mocked_receipt):
                with self.assertRaisesRegex(ValueError,"node degrees"):
                    load_etq_bundle(d)

    def test_optional_numpy(self):
        try:
            import numpy
        except ImportError:
            self.skipTest("numpy optional")
        result=auxiliary_spectral(build_tanner())
        self.assertGreaterEqual(result["laplacianGap"],0)
        self.assertEqual(result["precision"],"float64")


if __name__=="__main__":
    unittest.main()
