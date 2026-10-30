"""Read-only, receipt-pinned adapter for official ETQ-303 v3.0.0 bundles.

This module never downloads or modifies upstream files. The CRT event sequence
is emphatically NOT a walk in the Cartesian-product graph.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .core import PHASE_EXPONENTS, PHASE_SYMBOLS, etq_address

# Independently published ETQ-303 v3.0.0 exact receipts, NOT EDGEWALK hashes.
ETQ_EVENT_SHA = "d0ab60df11084a230e641d737ec22b2b2ca7d3a3ba5b8759ba669ac4d5254dc0"
ETQ_EDGES_SHA = "7c2c820468e3492932ea2d97331114a0c9644d28f9048b864bc81abca84202cf"
MODEL = "ETQ-303"
VERSION = "3.0.0"
PROFILE = "full-qutrit-event-protocol-v1"


def _reject(value: str) -> None:
    raise ValueError("non-integer/nonfinite JSON number: " + value[:64])


def _pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _integer(value: str) -> int:
    number = int(value)
    if abs(number) > 9007199254740991:
        raise ValueError("unsafe JSON integer")
    return number


def _read(directory: Path, filename: str) -> tuple[dict, bytes]:
    path = directory / filename
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 12_000_000:
        raise ValueError("missing, symlinked or oversized ETQ artifact: " + filename)
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf-8"), parse_float=_reject,
                         parse_constant=_reject, parse_int=_integer,
                         object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid UTF-8 JSON in " + filename) from exc
    if not isinstance(doc, dict):
        raise ValueError("ETQ JSON root must be an object: " + filename)
    return doc, raw


def _domain_hash(domain: str, value: object) -> str:
    if not isinstance(domain, str) or not domain.startswith("ETQ/V3/"):
        raise ValueError("invalid upstream hash domain")
    # ETQ's canonical serializer: sorted objects, compact UTF-8, integer data.
    return hashlib.sha256(domain.encode("utf-8") + b"\0" +
                          json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("ETQ validation: " + message)


def _integer_field(value: object, expected: int, label: str) -> None:
    _require(type(value) is int and value == expected, label)


@dataclass(frozen=True)
class ETQBundle:
    adjacency: dict[str, tuple[str, ...]]
    events: tuple[dict, ...]
    artifact_sha256: dict[str, str]
    event_document_receipt: str
    graph_edges_receipt: str


def load_etq_bundle(directory: str | Path) -> ETQBundle:
    """Validate a generated SONIFICATION build:v3 directory; no network access.

    Required inputs are upstream contract.json, events.json, graph.json and
    manifest.json, not the small examples/etq-303.v3.canonical.json contract.
    """
    root = Path(directory)
    _require(root.is_dir(), "bundle directory missing")
    names = ("contract.json", "events.json", "graph.json", "manifest.json")
    docs = {name: _read(root, name) for name in names}
    contract, events_doc, graph, manifest = (docs[name][0] for name in names)
    hashes = {name: hashlib.sha256(docs[name][1]).hexdigest() for name in names}

    for title, doc in (("contract", contract), ("events", events_doc),
                       ("graph", graph), ("manifest", manifest)):
        _require(doc.get("modelId") == MODEL and doc.get("modelVersion") == VERSION,
                 title + " model identity")
    _require(contract.get("profile") == PROFILE and events_doc.get("profile") == PROFILE
             and manifest.get("profile") == PROFILE, "profile identity")
    _require(events_doc.get("schema") == "qsol.etq-303.events/v1", "event schema")
    _require(graph.get("schema") == "qsol.etq-303.graph-receiver/v1", "graph receiver schema")
    _require(manifest.get("schema") == "qsol.etq-303.manifest/v1", "manifest schema")
    _require(graph.get("construction") == "cartesian-product-G101-square-C3", "graph construction")

    det = contract.get("determinism")
    _require(isinstance(det, dict), "missing commitment table")
    domains = det.get("hashDomains")
    _require(isinstance(domains, dict), "missing hash domains")
    _require(det.get("eventDocumentSha256") == ETQ_EVENT_SHA, "published event commitment")
    _require(det.get("liftedEdgesSha256") == ETQ_EDGES_SHA, "published edge commitment")
    _require(domains.get("eventDocument") == "ETQ/V3/EVENT-DOCUMENT/v1", "event hash domain")
    _require(domains.get("liftedEdges") == "ETQ/V3/LIFTED-EDGES/v1", "edge hash domain")
    _require(_domain_hash(domains["eventDocument"], events_doc) == ETQ_EVENT_SHA,
             "event document semantic receipt")

    artifact_rows = manifest.get("artifacts")
    _require(isinstance(artifact_rows, list), "manifest artifacts")
    artifact_map = {}
    for row in artifact_rows:
        _require(isinstance(row, dict) and isinstance(row.get("filename"), str),
                 "manifest artifact row")
        filename = row["filename"]
        _require(filename not in artifact_map, "duplicate artifact filename")
        artifact_map[filename] = row
    for filename in names[:-1]:
        row = artifact_map.get(filename)
        _require(isinstance(row, dict) and row.get("sha256") == hashes[filename]
                 and type(row.get("byteLength")) is int
                 and row["byteLength"] == len(docs[filename][1]),
                 "manifest file receipt for " + filename)
    manifest_core = dict(manifest)
    manifest_sha = manifest_core.pop("manifestCoreSha256", None)
    _require(manifest_sha == _domain_hash(domains.get("manifest", ""), manifest_core),
             "manifest core receipt")

    events = events_doc.get("events")
    _require(isinstance(events, list) and len(events) == 303, "303 events")
    _require(events_doc.get("graphContext", {}).get("eventTraversalIsGraphWalk") is False,
             "canonical events cannot be treated as graph walks")
    _require(events_doc.get("exactStep", {}).get("gaussianExponents") == list(PHASE_EXPONENTS),
             "Gaussian exponents")
    _require(events_doc.get("exactStep", {}).get("gaussianPhaseSymbols") == list(PHASE_SYMBOLS),
             "Gaussian symbols")
    for n, event in enumerate(events):
        _require(isinstance(event, dict), "event row")
        addr = etq_address(n)
        for field in ("sequenceIndex", "siteIndex", "fibreLabel", "tensorIndex"):
            _integer_field(event.get(field), addr[field], "event " + field)
        _integer_field(event.get("transitionPhaseGaussianExponent"),
                       addr["phaseExponent"], "event exponent")
        _require(event.get("transitionPhaseSymbol") == addr["phaseSymbol"], "event phase")
        _integer_field(event.get("nextSequenceIndex"), (n + 1) % 303, "next sequence")
        _integer_field(event.get("nextTensorIndex"), etq_address((n + 1) % 303)["tensorIndex"],
                       "next tensor")
    _require(_domain_hash(domains.get("events", ""), events) == det.get("eventsSha256"),
             "event array semantic receipt")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    _integer_field(graph.get("vertexCount"), 303, "vertex count")
    _integer_field(graph.get("edgeCount"), 5364, "edge count")
    _require(isinstance(nodes, list) and len(nodes) == 303, "graph nodes")
    _require(isinstance(edges, list) and len(edges) == 5364, "graph edges")
    _require(_domain_hash(domains["liftedEdges"], edges) == ETQ_EDGES_SHA,
             "edge semantic receipt")
    degree = [0] * 303
    neighbors = {str(i): set() for i in range(303)}
    for idx, node in enumerate(nodes):
        _require(isinstance(node, dict), "graph node")
        for field, expected in (("tensorIndex", idx), ("siteIndex", idx // 3),
                                ("fibreLabel", idx % 3)):
            _integer_field(node.get(field), expected, "node " + field)
    previous = (-1, -1)
    for edge in edges:
        _require(isinstance(edge, dict), "edge row")
        source, target, kind = edge.get("source"), edge.get("target"), edge.get("kind")
        _require(type(source) is int and type(target) is int
                 and 0 <= source < target < 303, "edge indices")
        _require((source, target) > previous, "strict sorted unique graph edges")
        previous = (source, target)
        if kind == "base-e8-edge":
            _require(source % 3 == target % 3, "base edge must preserve fibre")
        elif kind == "fibre-c3-edge":
            _require(source // 3 == target // 3 and source % 3 != target % 3,
                     "fibre edge must preserve site")
        else:
            raise ValueError("ETQ validation: unknown edge kind")
        degree[source] += 1
        degree[target] += 1
        neighbors[str(source)].add(str(target))
        neighbors[str(target)].add(str(source))
    _require(min(degree) == 24 and max(degree) == 57, "degree bounds")
    _require(graph.get("connected") is True, "graph connected flag")
    _require(all(type(node.get("liftedDegree")) is int
                 and node["liftedDegree"] == degree[i]
                 for i, node in enumerate(nodes)), "node degrees")
    visited = {"0"}
    queue = ["0"]
    for vertex in queue:
        for other in neighbors[vertex]:
            if other not in visited:
                visited.add(other)
                queue.append(other)
    _require(len(visited) == 303, "graph connectivity")
    return ETQBundle(
        adjacency={v: tuple(sorted(row, key=int)) for v, row in neighbors.items()},
        events=tuple(events),
        artifact_sha256={name: hashes[name] for name in names},
        event_document_receipt=ETQ_EVENT_SHA,
        graph_edges_receipt=ETQ_EDGES_SHA,
    )
