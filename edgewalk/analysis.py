"""Deterministic auxiliary graph comparisons; never modifies code or ETQ identities."""
from __future__ import annotations

import hashlib
from typing import Mapping

from .core import build_tanner, canonical_bytes, etq_address, tanner_metrics
from .etq import ETQBundle

DOMAIN = b"EDGEWALK/V2/COMPARISON\0"


def validated_walk(graph: Mapping[str, tuple[str, ...]], start: str, count: int = 303) -> tuple[dict, ...]:
    """Walk actual graph edges, with ETQ event addresses as an auxiliary clock."""
    tanner_metrics(dict(graph))
    if start not in graph:
        raise ValueError("start node absent")
    current = start
    steps = []
    for n in range(count):
        event = etq_address(n)
        options = tuple(sorted(graph[current]))
        if not options:
            raise ValueError("isolated vertex")
        ordinal = (event["siteIndex"] + event["fibreLabel"]) % len(options)
        nxt = options[ordinal]
        if current not in graph[nxt] or nxt == current:
            raise AssertionError("invalid graph edge")
        steps.append({"sequenceIndex": n, "source": current, "target": nxt,
                      "neighborOrdinal": ordinal, "fibreLabel": event["fibreLabel"]})
        current = nxt
    return tuple(steps)


def walk_stats(steps: tuple[dict, ...]) -> dict[str, int]:
    edges = [tuple(sorted((s["source"], s["target"]))) for s in steps]
    vertices = {steps[0]["source"]} if steps else set()
    vertices.update(s["target"] for s in steps)
    return {
        "steps": len(steps),
        "visitedVertices": len(vertices),
        "uniqueEdges": len(set(edges)),
        "immediateBacktracks": sum(steps[i - 1]["source"] == steps[i]["target"] for i in range(1, len(steps))),
    }


def exact_spectral_moments(graph: Mapping[str, tuple[str, ...]]) -> dict[str, int]:
    """Exact traces: Tr(A²)=2m; Tr(L)=sum d; Tr(L²)=sum d²+2m."""
    metrics = tanner_metrics(dict(graph))
    degrees = [len(row) for row in graph.values()]
    return {
        "adjacencyTraceA2": 2 * metrics["edges"],
        "laplacianTraceL": sum(degrees),
        "laplacianTraceL2": sum(d * d for d in degrees) + sum(degrees),
        "nonBacktrackingStates": sum(degrees),
        "nonBacktrackingTransitions": sum(d * (d - 1) for d in degrees),
    }


def degree_preserving_control(graph: Mapping[str, tuple[str, ...]], swaps: int = 16,
                              partition: Mapping[str, str] | None = None) -> dict[str, tuple[str, ...]]:
    """Deterministic two-switch control; preserves degrees but not physical validity."""
    if type(swaps) is not int or swaps < 0 or swaps > 256:
        raise ValueError("invalid swaps")
    tanner_metrics(dict(graph))
    work = {a: set(row) for a, row in graph.items()}
    done = 0
    for attempt in range(20000):
        if done >= swaps:
            break
        edges = sorted((a, b) for a in work for b in work[a] if a < b)
        if len(edges) < 2:
            break
        ab = edges[(attempt * 37 + 3) % len(edges)]
        cd = edges[(attempt * 61 + len(edges) // 2) % len(edges)]
        a, b = ab
        c, d = cd
        if len({a, b, c, d}) != 4:
            continue
        candidates = ((a, d), (c, b))
        if partition is not None:
            if any(partition.get(x) == partition.get(y) for x, y in candidates):
                candidates = ((a, c), (b, d))
            if any(partition.get(x) == partition.get(y) for x, y in candidates):
                continue
        elif attempt % 2:
            candidates = ((a, c), (b, d))
        if any(x == y or y in work[x] for x, y in candidates):
            continue
        for x, y in (ab, cd):
            work[x].remove(y)
            work[y].remove(x)
        for x, y in candidates:
            work[x].add(y)
            work[y].add(x)
        done += 1
    if done == 0 and swaps:
        raise ValueError("no legal degree-preserving swaps")
    result = {a: tuple(sorted(row)) for a, row in sorted(work.items())}
    tanner_metrics(result)
    if {a: len(row) for a, row in graph.items()} != {a: len(row) for a, row in result.items()}:
        raise AssertionError("control changed degree sequence")
    return result


def auxiliary_spectral(graph: Mapping[str, tuple[str, ...]]) -> dict[str, object]:
    """Optional numerical eigen diagnostics; excluded from identity-bearing receipts."""
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("numerical diagnostics require optional numpy") from exc
    names = sorted(graph)
    lookup = {name: i for i, name in enumerate(names)}
    adjacency = np.zeros((len(names), len(names)), dtype=np.float64)
    for node, row in graph.items():
        for dest in row:
            adjacency[lookup[node], lookup[dest]] = 1.0
    laplacian = np.diag(adjacency.sum(axis=1)) - adjacency
    lambdas = np.linalg.eigvalsh(laplacian)
    values, vectors = np.linalg.eigh(adjacency)
    vec = vectors[:, -1]
    return {"precision": "float64", "solver": "numpy.linalg.eigh/eigvalsh",
            "laplacianGap": float(lambdas[1]),
            "laplacianMaximum": float(lambdas[-1]),
            "adjacencySpectralRadius": float(max(abs(values[0]), abs(values[-1]))),
            "principalAdjacencyIPR": float(np.sum(vec ** 4)),
            "note": "auxiliary floating diagnostics; not identity-bearing; degeneracies may change eigenvector IPR"}


def compare(etq: ETQBundle, numerical: bool = False, swaps: int = 16) -> dict[str, object]:
    """Cross-system graph comparison with explicitly labelled degree-preserving controls."""
    golay = build_tanner()
    etq_graph = etq.adjacency
    parts = {node: "q" if node.startswith("q:") else "check" for node in golay}
    graphs = {"golay": golay, "etq": etq_graph}
    controls = {
        "golay": degree_preserving_control(golay, swaps, parts),
        "etq": degree_preserving_control(etq_graph, swaps),
    }
    result = {}
    for name in ("golay", "etq"):
        original, control = graphs[name], controls[name]
        start = "q:00" if name == "golay" else "0"
        entry = {
            "graph": tanner_metrics(original),
            "spectralMoments": exact_spectral_moments(original),
            "walk": walk_stats(validated_walk(original, start)),
            "degreePreservingControl": {
                "graph": tanner_metrics(control),
                "spectralMoments": exact_spectral_moments(control),
                "walk": walk_stats(validated_walk(control, start)),
                "requestedSwaps": swaps,
                "limitation": "graph-topology null only; NOT a valid CSS code or ETQ graph identity",
            },
        }
        if numerical:
            entry["auxiliaryNumerics"] = auxiliary_spectral(original)
            entry["degreePreservingControl"]["auxiliaryNumerics"] = auxiliary_spectral(control)
        result[name] = entry
    payload = {
        "schema": "edgewalk.cross-domain-comparison/v1",
        "etqSource": {"eventDocumentSha256": etq.event_document_receipt,
                      "liftedEdgesSha256": etq.graph_edges_receipt,
                      "artifactSha256": etq.artifact_sha256},
        "comparisons": result,
        "interpretation": "Descriptive structural measurements only; no evidence of shared physics or statistical significance",
    }
    # Numeric eigensolvers must never contaminate exact integer receipts.
    exact = {"schema": payload["schema"], "etqSource": payload["etqSource"],
             "comparisons": {key: {k: v for k, v in record.items() if k != "auxiliaryNumerics"}
                             for key, record in result.items()},
             "interpretation": payload["interpretation"]}
    for record in exact["comparisons"].values():
        record["degreePreservingControl"] = {k: v for k, v in record["degreePreservingControl"].items()
                                            if k != "auxiliaryNumerics"}
    return {"domain": "EDGEWALK/V2/COMPARISON",
            "sha256": hashlib.sha256(DOMAIN + canonical_bytes(exact)).hexdigest(),
            "payload": payload}
