"""Exact Golay CSS and adjacency-verified ETQ-inspired walk baseline.

No external ETQ artifact is modified or impersonated by this module.
"""
from __future__ import annotations

import hashlib
import json

N = 23
GENERATOR_POLYNOMIAL = 0xAE3
GENERATOR_ROWS = tuple(GENERATOR_POLYNOMIAL << i for i in range(12))
PHASE_EXPONENTS = (3, 2, 3)
PHASE_SYMBOLS = ("-i", "-1", "-i")
RECEIPT_DOMAIN = b"EDGEWALK/V1/WALK\x00"


def gf2_rref(rows: tuple[int, ...], width: int = N) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if width <= 0 or any(type(row) is not int or row < 0 or row >= (1 << width) for row in rows):
        raise ValueError("invalid GF(2) rows")
    matrix = list(rows)
    pivots = []
    rank = 0
    for column in range(width):
        selected = next((r for r in range(rank, len(matrix)) if (matrix[r] >> column) & 1), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        for r in range(len(matrix)):
            if r != rank and ((matrix[r] >> column) & 1):
                matrix[r] ^= matrix[rank]
        pivots.append(column)
        rank += 1
        if rank == len(matrix):
            break
    return tuple(matrix[:rank]), tuple(pivots)


def gf2_nullspace(rows: tuple[int, ...], width: int = N) -> tuple[int, ...]:
    reduced, pivots = gf2_rref(rows, width)
    free = [c for c in range(width) if c not in pivots]
    return tuple(
        (1 << col) | sum(((row >> col) & 1) << pivot for row, pivot in zip(reduced, pivots))
        for col in free
    )


def gf2_span(rows: tuple[int, ...]) -> tuple[int, ...]:
    codewords = [0]
    for row in rows:
        codewords += [word ^ row for word in codewords]
    return tuple(codewords)


def parity(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def golay_checks() -> tuple[int, ...]:
    checks = gf2_nullspace(GENERATOR_ROWS)
    if len(checks) != 11 or len(gf2_rref(checks)[1]) != 11:
        raise AssertionError("Golay dual must have rank 11")
    if any(parity(a, b) for a in checks for b in checks):
        raise AssertionError("CSS self-orthogonality violated")
    if any(parity(a, b) for a in checks for b in GENERATOR_ROWS):
        raise AssertionError("dual is not orthogonal to generators")
    return checks


def code_parameters() -> dict[str, int]:
    checks = golay_checks()
    classical = gf2_span(GENERATOR_ROWS)
    stabilizers = set(gf2_span(checks))
    distance = min(word.bit_count() for word in classical if word not in stabilizers)
    classical_distance = min(word.bit_count() for word in classical if word)
    return {
        "classicalN": N,
        "classicalK": len(gf2_rref(GENERATOR_ROWS)[1]),
        "classicalD": classical_distance,
        "quantumN": N,
        "quantumK": N - 2 * len(checks),
        "quantumD": distance,
        "checkRank": len(checks),
    }


def build_tanner() -> dict[str, tuple[str, ...]]:
    """Combined X/Z CSS Tanner graph; 23 shared qubit nodes, 22 check nodes."""
    neighbors: dict[str, set[str]] = {f"q:{q:02d}": set() for q in range(N)}
    checks = golay_checks()
    for channel in ("x", "z"):
        for row_id, row in enumerate(checks):
            check_id = f"{channel}:{row_id:02d}"
            neighbors[check_id] = set()
            for qubit in range(N):
                if (row >> qubit) & 1:
                    node_id = f"q:{qubit:02d}"
                    neighbors[node_id].add(check_id)
                    neighbors[check_id].add(node_id)
    return {key: tuple(sorted(neighbors[key])) for key in sorted(neighbors)}


def tanner_metrics(adjacency: dict[str, tuple[str, ...]]) -> dict[str, int]:
    degrees = [len(v) for v in adjacency.values()]
    if not degrees:
        raise ValueError("empty graph")
    for node, neighbors in adjacency.items():
        if len(neighbors) != len(set(neighbors)) or node in neighbors:
            raise ValueError("invalid Tanner adjacency")
        for other in neighbors:
            if other not in adjacency or node not in adjacency[other]:
                raise ValueError("non-reciprocal Tanner edge")
    return {
        "vertices": len(adjacency),
        "edges": sum(degrees) // 2,
        "minimumDegree": min(degrees),
        "maximumDegree": max(degrees),
        "directedEdges": sum(degrees),
        "nonBacktrackingTransitions": sum(d * (d - 1) for d in degrees),
    }


def etq_address(n: int) -> dict[str, int | str]:
    """An ETQ-303-inspired address projection; NOT an ETQ canonical event receipt."""
    if type(n) is not int or not 0 <= n < 303:
        raise ValueError("event index must be an integer in [0, 302]")
    site = n % 101
    fibre = n % 3
    return {
        "sequenceIndex": n,
        "siteIndex": site,
        "fibreLabel": fibre,
        "tensorIndex": 3 * site + fibre,
        "phaseExponent": PHASE_EXPONENTS[fibre],
        "phaseSymbol": PHASE_SYMBOLS[fibre],
    }


def inverse_etq_address(site: int, fibre: int) -> int:
    if type(site) is not int or type(fibre) is not int or not 0 <= site < 101 or not 0 <= fibre < 3:
        raise ValueError("invalid CRT coordinate")
    return site + 101 * ((2 * (fibre - (site % 3))) % 3)


def run_walk(adjacency: dict[str, tuple[str, ...]] | None = None) -> tuple[dict, ...]:
    """Choose only actual Tanner edges by a deterministic 303-event schedule."""
    graph = build_tanner() if adjacency is None else adjacency
    tanner_metrics(graph)
    current = "q:00"
    if current not in graph:
        raise ValueError("missing start vertex q:00")
    steps = []
    for n in range(303):
        event = etq_address(n)
        choices = tuple(sorted(graph[current]))
        if not choices:
            raise ValueError("isolated vertex in walk")
        idx = (event["siteIndex"] + event["fibreLabel"]) % len(choices)
        target = choices[idx]
        if current not in graph[target]:
            raise AssertionError("non-edge walk step")
        steps.append({"event": event, "from": current, "to": target, "neighborOrdinal": idx})
        current = target
    return tuple(steps)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def walk_receipt(steps: tuple[dict, ...] | None = None) -> dict[str, object]:
    graph = build_tanner()
    events = run_walk(graph) if steps is None else steps
    if len(events) != 303:
        raise ValueError("walk receipt requires exactly 303 events")
    payload = {
        "schema": "edgewalk.golay-etq-aux-walk/v1",
        "graph": "Golay-23 dual-check CSS Tanner X/Z",
        "metrics": tanner_metrics(graph),
        "events": list(events),
        "source": "EDGEWALK-authored ETQ-inspired scheduler, not canonical ETQ event document",
    }
    sha = hashlib.sha256(RECEIPT_DOMAIN + canonical_bytes(payload)).hexdigest()
    return {"payload": payload, "sha256": sha, "domain": "EDGEWALK/V1/WALK"}
