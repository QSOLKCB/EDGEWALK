"""EDGEWALK v0.4: exact control ensembles and separately qualified statistics."""
from __future__ import annotations

from hashlib import sha256
from math import comb
from random import Random
from statistics import median
from typing import Mapping

from .core import build_tanner, canonical_bytes, gf2_rref, golay_checks, parity, tanner_metrics
from .analysis import validated_walk, walk_stats

GRAPH_DOMAIN = b"EDGEWALK/V4/GRAPH\0"
EVIDENCE_DOMAIN = b"EDGEWALK/V4/EXPERIMENT\0"
METRICS = ("fourCycles", "walkUniqueEdges", "oneEdgeDeltaTraceA4", "twoEdgeDeltaTraceA4")
VARIANTS = ("reference", "shear-a", "shear-b")


class _CounterRNG:
    """Cross-version deterministic SHA-256 counter sampler with rejection."""
    def __init__(self, seed: int):
        self.key = seed.to_bytes(32, "big")
        self.counter = 0

    def randrange(self, upper: int) -> int:
        if upper <= 0:
            raise ValueError("empty random draw")
        width = max(1, (upper.bit_length() + 7)//8)
        maximum = 1 << (8*width)
        cutoff = maximum - maximum % upper
        while True:
            digest = sha256(self.key + self.counter.to_bytes(8, "big")).digest()
            self.counter += 1
            number = int.from_bytes(digest[:width], "big")
            if number < cutoff:
                return number % upper

    def distinct_pair(self, count: int) -> tuple[int, int]:
        if count < 2:
            raise ValueError("fewer than two choices")
        first = self.randrange(count)
        second = self.randrange(count-1)
        return first, second + (second >= first)


def _seed(seed: int, label: str, sample: int) -> int:
    return int.from_bytes(sha256(f"{seed}|{label}|{sample}".encode("utf-8")).digest(), "big")


def _graph(graph: Mapping[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    normalized = {k: tuple(sorted(v)) for k,v in sorted(graph.items())}
    tanner_metrics(normalized)
    if any(type(k) is not str for k in normalized):
        raise ValueError("graph labels must be strings")
    if any(len(row) == 0 for row in normalized.values()):
        raise ValueError("experiment graphs may not have isolates")
    return normalized


def _edges(graph):
    return tuple(sorted((u,v) for u in graph for v in graph[u] if u < v))


def graph_sha256(graph):
    graph = _graph(graph)
    return sha256(GRAPH_DOMAIN + canonical_bytes({
        "vertices": list(graph), "edges": [list(edge) for edge in _edges(graph)]
    })).hexdigest()


def build_basis_tanner(variant="reference"):
    """Invertible row shears preserve GF(2) CSS rank and orthogonality."""
    if variant not in VARIANTS:
        raise ValueError("unknown Golay check-basis variant")
    if variant == "reference":
        return build_tanner()
    rows = list(golay_checks())
    if variant == "shear-a":
        rows[0] ^= rows[1]
    else:
        for i in (0,2,4,6,8):
            rows[i] ^= rows[i+1]
    if len(gf2_rref(tuple(rows))[1]) != 11 or any(parity(a,b) for a in rows for b in rows):
        raise AssertionError("shear destroyed CSS invariants")
    graph = {f"q:{q:02d}": set() for q in range(23)}
    for channel in ("x","z"):
        for i, row in enumerate(rows):
            check = f"{channel}:{i:02d}"
            graph[check] = set()
            for q in range(23):
                if row & (1 << q):
                    vertex = f"q:{q:02d}"
                    graph[check].add(vertex)
                    graph[vertex].add(check)
    return _graph(graph)


def _connected(graph):
    first = min(graph)
    seen, pending = {first}, [first]
    for vertex in pending:
        for nxt in graph[vertex]:
            if nxt not in seen:
                seen.add(nxt)
                pending.append(nxt)
    return len(seen) == len(graph)


def _rewire(graph, swaps: int, rng: _CounterRNG, channelized=False):
    """Finite degree-preserving 2-switches; matched constraint, not a new code."""
    work = {k: set(v) for k,v in _graph(graph).items()}
    if type(swaps) is not int or not 1 <= swaps <= 512:
        raise ValueError("swaps must be within [1,512]")
    accepted, attempts = 0, 0
    while accepted < swaps and attempts < max(1000, swaps*250):
        attempts += 1
        if channelized:
            channel = ("x:", "z:")[rng.randrange(2)]
            edges = sorted((q,c) for q in work if q.startswith("q:")
                           for c in work[q] if c.startswith(channel))
        else:
            edges = sorted((a,b) for a in work for b in work[a] if a < b)
        if len(edges) < 2:
            break
        i,j = rng.distinct_pair(len(edges))
        a,b = edges[i]
        c,d = edges[j]
        if not channelized:
            if rng.randrange(2): a,b = b,a
            if rng.randrange(2): c,d = d,c
        if len({a,b,c,d}) < 4 or d in work[a] or b in work[c]:
            continue
        for x,y in ((a,b),(c,d)):
            work[x].remove(y)
            work[y].remove(x)
        for x,y in ((a,d),(c,b)):
            work[x].add(y)
            work[y].add(x)
        accepted += 1
    if accepted != swaps:
        raise ValueError(f"only {accepted} of {swaps} switches accepted")
    result = _graph(work)
    if not _connected(result):
        raise ValueError("disconnected control; retry with a different recorded seed")
    if any(len(result[v]) != len(graph[v]) for v in graph):
        raise AssertionError("control changed degree sequence")
    return result, attempts


def lift_etq(base):
    """Graph-only Cartesian product with C3; never an ETQ event document."""
    base = _graph(base)
    if set(base) != {str(j) for j in range(101)}:
        raise ValueError("lift requires indexed 101-vertex base")
    graph = {}
    for j in range(101):
        for a in range(3):
            graph[str(3*j+a)] = tuple(sorted(
                {str(3*int(k)+a) for k in base[str(j)]} |
                {str(3*j+b) for b in range(3) if a != b}))
    return _graph(graph)


def etq_base(graph):
    """Check exact Cartesian topology *before* deriving the base graph."""
    graph = _graph(graph)
    if set(graph) != {str(i) for i in range(303)}:
        raise ValueError("ETQ input must use exactly 303 indexed vertices")
    base = {str(j): tuple(str(k) for k in range(101)
            if k != j and str(3*k) in graph[str(3*j)]) for j in range(101)}
    base = _graph(base)
    if lift_etq(base) != graph:
        raise ValueError("ETQ graph is not an exact Cartesian product")
    return base


def four_cycles(graph):
    """Exact C4 count via common-neighbour bit sets."""
    names = sorted(graph)
    bits = {u: sum(1 << i for i,v in enumerate(names) if v in graph[u]) for u in names}
    total = 0
    for i,u in enumerate(names):
        for v in names[i+1:]:
            common = (bits[u] & bits[v]).bit_count()
            if common >= 2:
                total += comb(common,2)
    if total % 2:
        raise AssertionError("4-cycle count must be an integer")
    return total//2


def trace_a4(graph):
    """Exact trace(A^4) computed from graph combinatorics, not eigenvalues."""
    m = tanner_metrics(dict(graph))["edges"]
    return 2*m + 4*sum(comb(len(row),2) for row in graph.values()) + 8*four_cycles(graph)


def _delete_edges(graph,count):
    work = {k:set(v) for k,v in graph.items()}
    for a,b in _edges(graph)[:count]:
        work[a].remove(b)
        work[b].remove(a)
    # Perturbed graph may contain isolates; graph signature isn't applied here.
    return {k:tuple(sorted(v)) for k,v in sorted(work.items())}


def _measure(graph, events=None, start=None):
    graph = _graph(graph)
    walk = walk_stats(validated_walk(graph, start or min(graph), events=events))
    baseline = trace_a4(graph)
    return {"fourCycles": four_cycles(graph),
            "walkUniqueEdges": walk["uniqueEdges"],
            "oneEdgeDeltaTraceA4": trace_a4(_delete_edges(graph,1))-baseline,
            "twoEdgeDeltaTraceA4": trace_a4(_delete_edges(graph,2))-baseline}


def _percentile(ordered, proportion):
    index = proportion*(len(ordered)-1)
    lo = int(index)
    return ordered[lo] + (ordered[min(lo+1,len(ordered)-1)]-ordered[lo])*(index-lo)


def _bootstrap_mean_interval(sample,seed,draws):
    rng = Random(seed)
    n = len(sample)
    means = sorted(sum(sample[rng.randrange(n)] for _ in range(n))/n for _ in range(draws))
    return [float(_percentile(means,0.025)), float(_percentile(means,0.975))]


def _summarize(exact,bootstrap_draws):
    families, ordered = {}, []
    for label,record in sorted(exact["systems"].items()):
        out = {}
        for metric in METRICS:
            observed = record["observed"][metric]
            sample = [item["metrics"][metric] for item in record["controls"]]
            center = median(sample)
            distance = abs(observed-center)
            tail = (1+sum(abs(x-center) >= distance for x in sample))/(len(sample)+1)
            out[metric] = {
                "observed": observed, "nullMedian": float(center),
                "nullMean": float(sum(sample)/len(sample)),
                "bootstrapNullMeanInterval95": _bootstrap_mean_interval(
                    sample,_seed(exact["config"]["seed"],label+metric,0),bootstrap_draws),
                "empiricalTwoSidedTailFraction": float(tail),
            }
            ordered.append((tail,label,metric))
        families[label] = out
    previous = 0.0
    for i,(tail,label,metric) in enumerate(sorted(ordered)):
        previous = max(previous,min(1.0,(len(ordered)-i)*tail))
        families[label][metric]["exploratoryHolmAdjustedTail"] = previous
    return {"familySize":len(ordered),"metrics":list(METRICS),"systems":families,
            "warning":"Bootstrap intervals describe generated controls; tail fractions and Holm-adjusted ranks are exploratory, not calibrated physical hypothesis tests"}


def run_controlled_experiment(etq=None, *, ensemble_size=16, swaps=16, seed=303,
                              bootstrap_draws=256, variants=VARIANTS):
    """Reproducible integer evidence; noncanonical exploratory statistics."""
    if any(type(x) is not int for x in (ensemble_size,swaps,seed,bootstrap_draws)):
        raise ValueError("experiment settings must be exact integers")
    if (not 4 <= ensemble_size <= 128 or not 1 <= swaps <= 512
            or not 32 <= bootstrap_draws <= 4096 or seed < 0 or seed > 2**32-1):
        raise ValueError("settings outside declared reproducible bounds")
    if (not isinstance(variants,(tuple,list)) or not variants
            or len(set(variants)) != len(variants)
            or any(v not in VARIANTS for v in variants)):
        raise ValueError("invalid unique check-basis variants")
    systems = {"golay/"+variant:build_basis_tanner(variant) for variant in variants}
    events = None
    if etq is not None:
        systems["etq/product"] = _graph(etq.adjacency)
        base = etq_base(systems["etq/product"])
        events = etq.events or None
        if events is not None and len(events) != 303:
            raise ValueError("ETQ event schedule must contain 303 events")
    else:
        base = None
    exact = {
        "schema":"edgewalk.controls.v0.4/exact-v1",
        "config":{"ensembleSize":ensemble_size,"swaps":swaps,"seed":seed,
                  "variants":list(variants),"metrics":list(METRICS),
                  "perturbedEdgeRanks":[0,1],
                  "sampler":"SHA256-counter-uniform-rejection-two-switch-v1",
                  "nullLimit":"finite steps, nonuniform distribution not assumed stationary"},
        "source":{"etq":None if etq is None else {
             "eventDocumentSha256":etq.event_document_receipt,
             "liftedEdgesSha256":etq.graph_edges_receipt,
             "artifactSha256":etq.artifact_sha256}},
        "systems":{}
    }
    for name,graph in sorted(systems.items()):
        start = "0" if name.startswith("etq/") else "q:00"
        original = _measure(graph,events,start)
        controls = []
        seen = {graph_sha256(graph)}
        for i in range(ensemble_size):
            sample_seed = _seed(seed,name,i)
            for retry in range(16):
                rng = _CounterRNG((sample_seed+retry) % (1 << 256))
                try:
                    if name == "etq/product":
                        new_base,attempts = _rewire(base,swaps,rng)
                        candidate = lift_etq(new_base)
                    else:
                        candidate,attempts = _rewire(graph,swaps,rng,channelized=True)
                except ValueError:
                    continue
                digest = graph_sha256(candidate)
                if digest not in seen:
                    break
            else:
                raise ValueError(f"unable to construct {ensemble_size} unique controls for {name}")
            seen.add(digest)
            controls.append({"index":i,"retry":retry,"attempts":attempts,
                             "graphSha256":digest,"metrics":_measure(candidate,events,start)})
        exact["systems"][name] = {
            "sourceGraphSha256":graph_sha256(graph),
            "observed":original, "controls":controls,
            "nullConstraint":("base-101-degree-preserving-cartesian-lift"
                              if name.startswith("etq/") else
                              "check-channel-bipartite-degree-preserving-graph-only"),
        }
    receipt = sha256(EVIDENCE_DOMAIN + canonical_bytes(exact)).hexdigest()
    return {"domain":"EDGEWALK/V4/EXPERIMENT","sha256":receipt,
            "exactEvidence":exact,"exploratoryAnalysis":_summarize(exact,bootstrap_draws),
            "claimBoundary":"Finite algorithmic controls only; no physical spacetime or statistical significance claim"}


def replay_experiment_receipt(record, etq=None):
    """Rebuild the exact controls from their committed seed, not just rehash JSON.

    ETQ input, when present, must be supplied through the validated read-only
    adapter by the caller. Exploratory bootstrap arrays are intentionally ignored.
    """
    try:
        exact = record["exactEvidence"]
        config = exact["config"]
        replay = run_controlled_experiment(
            etq, ensemble_size=config["ensembleSize"], swaps=config["swaps"],
            seed=config["seed"], variants=tuple(config["variants"]),
            bootstrap_draws=32)
        return (record.get("domain") == "EDGEWALK/V4/EXPERIMENT"
                and record.get("sha256") == replay["sha256"]
                and exact == replay["exactEvidence"])
    except (KeyError, TypeError, ValueError, OverflowError):
        return False
