"""Optional float64 spectral stability; NOT a canonical ETQ or EDGEWALK receipt."""
from __future__ import annotations

import math
from collections.abc import Mapping
from .core import build_tanner, tanner_metrics
from .analysis import degree_preserving_control


def _libraries():
    try:
        import numpy as np
        import scipy
        from scipy import sparse
        from scipy.sparse import linalg as spla
    except ImportError as exc:
        raise RuntimeError("v0.3 stability requires optional numpy and scipy") from exc
    return np, scipy, sparse, spla


def _validate(graph: Mapping[str, tuple[str, ...]]):
    tanner_metrics(dict(graph))
    return tuple(sorted(graph))


def _adjacency(graph):
    np, _, sparse, _ = _libraries()
    names = _validate(graph)
    indices = {name: i for i, name in enumerate(names)}
    row, col = [], []
    for a in names:
        for b in graph[a]:
            row.append(indices[a]); col.append(indices[b])
    a = sparse.csr_matrix((np.ones(len(row), dtype=np.float64), (row, col)),
                          shape=(len(names), len(names)))
    return names, a


def nonbacktracking_operator(graph):
    """Hashimoto B[(u,v),(v,w)]=1 iff w!=u, deterministic oriented-edge order."""
    np, _, sparse, _ = _libraries()
    names = _validate(graph)
    arcs = tuple((a, b) for a in names for b in sorted(graph[a]))
    labels = {edge: i for i, edge in enumerate(arcs)}
    row, col = [], []
    for i, (u, v) in enumerate(arcs):
        for w in sorted(graph[v]):
            if w != u:
                row.append(i)
                col.append(labels[(v, w)])
    matrix = sparse.csr_matrix((np.ones(len(row), dtype=np.float64), (row, col)),
                               shape=(len(arcs), len(arcs)))
    if matrix.nnz != sum(len(x) * (len(x) - 1) for x in graph.values()):
        raise AssertionError("nonbacktracking transition count mismatch")
    return arcs, matrix


def nonbacktracking_modes(graph, modes=4, tolerance=1e-7):
    """Leading eigenpairs with residuals; sparse for large nonbacktracking matrices."""
    np, _, _, spla = _libraries()
    if type(modes) is not int or not 1 <= modes <= 8:
        raise ValueError("modes must be in [1,8]")
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("positive finite tolerance required")
    arcs, matrix = nonbacktracking_operator(graph)
    n = len(arcs)
    if n < 3:
        raise ValueError("at least three oriented edges required")
    k = min(modes, n - 2)
    full_dense_eigenvalues = None
    v0 = np.arange(1, n + 1, dtype=np.float64)
    v0 /= np.linalg.norm(v0)
    try:
        if n <= 128:
            full_dense_eigenvalues, full_dense_vectors = np.linalg.eig(matrix.toarray())
            order = sorted(range(len(full_dense_eigenvalues)),
                           key=lambda i: (-abs(full_dense_eigenvalues[i]),
                                          -full_dense_eigenvalues[i].real,
                                          -full_dense_eigenvalues[i].imag))[:k]
            values = full_dense_eigenvalues[order]
            vectors = full_dense_vectors[:, order]
            solver = "numpy.linalg.eig dense"
        else:
            values, vectors = spla.eigs(matrix, k=k, which="LM", v0=v0,
                                        tol=tolerance, maxiter=max(4000, 5 * n))
            order = sorted(range(k), key=lambda i: (-abs(values[i]),
                          -values[i].real, -values[i].imag))
            values, vectors = values[order], vectors[:, order]
            solver = "scipy.sparse.linalg.eigs ARPACK"
    except spla.ArpackNoConvergence as exc:
        raise RuntimeError("nonbacktracking ARPACK did not converge; no fabricated spectrum") from exc
    modes_out = []
    for i, (value, vector) in enumerate(zip(values, vectors.T)):
        vector = vector / np.linalg.norm(vector)
        residual = float(np.linalg.norm(matrix @ vector - value * vector))
        threshold = 10 * tolerance * max(1.0, abs(value))
        returned_collision = any(
            i != j and abs(value - other) <= threshold
            for j, other in enumerate(values)
        )
        # Dense branch: check the FULL eigenspectrum, including discarded modes.
        # A partial sparse ARPACK spectrum cannot certify global multiplicity.
        full_collision = (
            bool(np.count_nonzero(np.abs(full_dense_eigenvalues - value) <= threshold) > 1)
            if full_dense_eigenvalues is not None else None
        )
        collision = returned_collision or full_collision is True
        modes_out.append({"real": float(value.real), "imag": float(value.imag),
                          "magnitude": float(abs(value)), "residualL2": residual,
                          "edgeIPR": None if collision else float(np.sum(np.abs(vector) ** 4)),
                          "nearDegenerateAmongReturned": bool(returned_collision),
                          "nearDegenerateInFullSpectrum": full_collision})
    return {"states": n, "transitions": int(matrix.nnz), "requestedModes": modes,
            "returnedModes": len(modes_out), "solver": solver,
            "precision": "float64/complex128", "tolerance": tolerance,
            "modes": modes_out,
            "note": "partial leading-magnitude spectrum; non-normal eigenvector IPR is basis-dependent, suppressed for detected near-degeneracy; residuals reported"}


def bethe_hessian(graph, r=None):
    """H(r)=(r^2-1)I-rA+D; default r from excess-degree ratio."""
    np, _, sparse, _ = _libraries()
    names, adjacency = _adjacency(graph)
    degrees = np.asarray(adjacency.sum(axis=1)).ravel()
    if r is None:
        r = math.sqrt(max(1.0, float(np.sum(degrees * (degrees - 1)) / np.sum(degrees))))
    if not math.isfinite(r) or r <= 0:
        raise ValueError("r must be positive finite")
    h = ((r * r - 1) * sparse.eye(len(names), format="csr")
         - r * adjacency + sparse.diags(degrees, format="csr"))
    return float(r), h


def symmetric_spectrum(graph, r=None, samples=6):
    np, _, _, spla = _libraries()
    if type(samples) is not int or samples < 1 or samples > 16:
        raise ValueError("samples must be in [1,16]")
    chosen_r, h = bethe_hessian(graph, r=r)
    n = h.shape[0]
    if n <= 160:
        values = np.linalg.eigvalsh(h.toarray())
        selected = values[:samples]
        exact_negative_count = int(np.sum(values < -1e-9))
        solver = "numpy.linalg.eigvalsh full"
    else:
        selected = spla.eigsh(h, k=min(samples, n - 2), which="SA",
                              return_eigenvectors=False, tol=1e-9,
                              v0=np.ones(n) / math.sqrt(n), maxiter=10000)
        selected = np.sort(selected)
        exact_negative_count = None
        solver = "scipy.sparse.linalg.eigsh partial smallest-algebraic"
    return {"r": chosen_r, "size": n, "smallestEigenvalues": [float(x) for x in selected],
            "negativeEigenvalueCountFull": exact_negative_count,
            "negativeWithinSample": int(sum(x < -1e-9 for x in selected)),
            "solver": solver, "precision": "float64", "tolerance": 1e-9,
            "note": "partial ETQ eigenvalue sample does not establish total negative inertia"}


def laplacian_projectors(graph, atol=1e-8, rtol=1e-8):
    """Full Laplacian eigenspace projectors invariant to rotations inside a cluster."""
    np, _, sparse, _ = _libraries()
    if not math.isfinite(atol) or not math.isfinite(rtol) or atol < 0 or rtol < 0:
        raise ValueError("invalid eigenspace clustering tolerance")
    names, adjacency = _adjacency(graph)
    if len(names) > 384:
        raise ValueError("full projectors limited to 384 vertices")
    degree = np.asarray(adjacency.sum(axis=1)).ravel()
    laplacian = (sparse.diags(degree) - adjacency).toarray()
    values, vectors = np.linalg.eigh(laplacian)
    groups = []
    i = 0
    while i < len(names):
        j = i + 1
        while j < len(names) and abs(values[j] - values[i]) <= atol + rtol * max(abs(values[i]), abs(values[j])):
            j += 1
        vec = vectors[:, i:j]
        diag = np.sum(vec * vec, axis=1)
        support = float((np.sum(diag) ** 2) / np.sum(diag * diag))
        groups.append({"eigenvalue": float(np.mean(values[i:j])), "multiplicity": j - i,
                       "projectorDiagonal": [float(x) for x in diag],
                       "effectiveVertexSupport": support,
                       "traceError": float(abs(np.sum(diag) - (j - i))),
                       "idempotenceResidualFro": float(np.linalg.norm((vec.T @ vec) - np.eye(j - i)))})
        i = j
    return {"size": len(names), "vertices": list(names), "groups": groups,
            "tolerance": {"atol": atol, "rtol": rtol},
            "precision": "float64", "solver": "numpy.linalg.eigh",
            "note": "full Laplacian projector groups; rotation-invariant within tolerance-defined groups"}


def verify_etq_spectral_shift(graph, tolerance=1e-8):
    """Check exact Cartesian topology then numerical {lambda,lambda+3,lambda+3}."""
    np, _, _, _ = _libraries()
    names = _validate(graph)
    if names != tuple(str(i) for i in sorted(range(303), key=lambda j: str(j))):
        raise ValueError("ETQ requires all 303 canonical tensor indices")
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("invalid shift tolerance")
    base = {j: {k for k in range(101) if k != j and str(3 * k) in graph[str(3 * j)]}
            for j in range(101)}
    expected = {}
    for j in range(101):
        for a in range(3):
            expected[str(3*j+a)] = {str(3*k+a) for k in base[j]} | {
                str(3*j+b) for b in range(3) if b != a}
    if any(set(graph[node]) != expected[node] for node in expected):
        raise ValueError("ETQ graph is not exactly G_101 Cartesian C3")
    a_base = np.zeros((101, 101), dtype=np.float64)
    for j in range(101):
        for k in base[j]:
            a_base[j, k] = 1.0
    degrees = a_base.sum(axis=1)
    base_vals = np.linalg.eigvalsh(np.diag(degrees) - a_base)
    predicted = np.sort(np.concatenate((base_vals, base_vals + 3, base_vals + 3)))
    _, adjacency = _adjacency(graph)
    full = adjacency.toarray()
    actual = np.linalg.eigvalsh(np.diag(full.sum(axis=1)) - full)
    error = float(np.max(np.abs(actual - predicted)))
    if error > tolerance:
        raise AssertionError("ETQ Cartesian spectral shift exceeded tolerance")
    return {"topologyExact": True, "eigenvalueCount": 303,
            "baseVertexCount": 101, "baseEigenvalueCount": 101,
            "maxAbsEigenvalueShiftError": error, "tolerance": tolerance,
            "predictedShifts": [0, 3, 3], "solver": "numpy.linalg.eigvalsh",
            "precision": "float64", "note": "graph product proof is combinatorial; eigenvalue error is numerical"}


def bp_messages(channel="x", graph=None):
    """Directed variable-to-check edges of one CSS channel, never mixed X/Z BP."""
    if channel not in ("x", "z"):
        raise ValueError("BP channel must be 'x' or 'z'")
    graph = build_tanner() if graph is None else graph
    _validate(graph)
    checks = sorted(name for name in graph if name.startswith(channel + ":"))
    variables = sorted(name for name in graph if name.startswith("q:"))
    if not checks or not variables:
        raise ValueError("incomplete Tanner channel")
    if any(not name.startswith("q:") for c in checks for name in graph[c]):
        raise ValueError("invalid check neighbours")
    edges = tuple((v, c) for v in variables for c in sorted(graph[v]) if c in checks)
    if not edges or any(len([u for u in graph[c] if u.startswith("q:")]) < 2 for c in checks):
        raise ValueError("check degree below two")
    return graph, checks, edges


def _bp_map(channel, messages, llr):
    """Sum-product scalar variable-to-check update and analytic Jacobian."""
    np, _, _, _ = _libraries()
    graph, _, arcs = bp_messages(channel)
    x = np.asarray(messages, dtype=np.float64)
    if x.shape != (len(arcs),) or not np.all(np.isfinite(x)) or np.max(np.abs(x)) > 30:
        raise ValueError("bad finite BP message vector")
    if not math.isfinite(llr) or abs(llr) > 30:
        raise ValueError("invalid BP llr")
    index = {arc: i for i, arc in enumerate(arcs)}
    out = np.full(len(arcs), float(llr))
    jac = np.zeros((len(arcs), len(arcs)), dtype=np.float64)
    for (v, c), idx in index.items():
        for other in sorted(name for name in graph[v] if name.startswith(channel + ":") and name != c):
            others = tuple(u for u in graph[other] if u != v)
            t = [math.tanh(float(x[index[(u,other)]]) / 2) for u in others]
            prod = math.prod(t)
            out[idx] += 2 * math.atanh(prod)
            for pos, u in enumerate(others):
                prod_except = math.prod(t[:pos] + t[pos+1:])
                jac[idx, index[(u,other)]] += prod_except * (1-t[pos]**2) / (1-prod**2)
    return out, jac


def bp_update_and_jacobian(channel="x", message=1.0, llr=0.5, damping=1.0):
    """Uniform trial-point one-step amplification; not decoder performance."""
    np, _, _, _ = _libraries()
    if not math.isfinite(message) or abs(message) > 30:
        raise ValueError("invalid trial message")
    if not math.isfinite(damping) or not 0 < damping <= 1:
        raise ValueError("invalid damping")
    _, _, arcs = bp_messages(channel)
    f, jac = _bp_map(channel, np.full(len(arcs), message), llr)
    linearized = (1-damping) * np.eye(len(arcs)) + damping * jac
    radius = float(np.max(np.abs(np.linalg.eigvals(linearized))))
    residual = float(np.max(np.abs(f-message)))
    return {"channel": channel, "messages": len(arcs), "trialMessage": message,
            "llr": llr, "damping": damping, "localJacobianSpectralRadius": radius,
            "fixedPointResidualInfinity": residual, "fixedPointQualified": residual <= 1e-8,
            "localContractionProxy": radius < 1, "jacobian": jac,
            "note": "trial point; local amplification is not a fixed-point or FER claim"}


def bp_fixed_point_probe(channel="x", llr=0.5, damping=0.5,
                         atol=1e-10, max_iterations=1000):
    """Find an actual scalar BP fixed point or withhold stability verdict."""
    np, _, _, _ = _libraries()
    if not math.isfinite(damping) or not 0 < damping <= 1:
        raise ValueError("invalid damping")
    if not math.isfinite(atol) or not 0 < atol <= 1e-4:
        raise ValueError("invalid fixed-point tolerance")
    if type(max_iterations) is not int or not 1 <= max_iterations <= 10000:
        raise ValueError("invalid maximum iterations")
    _, _, arcs = bp_messages(channel)
    point = np.full(len(arcs), float(llr))
    converged = False
    message_bound_exceeded = False
    for iteration in range(1, max_iterations+1):
        step, _ = _bp_map(channel, point, llr)
        delta = step-point
        if np.max(np.abs(delta)) <= atol:
            converged = True
            break
        candidate = point + damping * delta
        if not np.all(np.isfinite(candidate)) or np.max(np.abs(candidate)) > 30:
            message_bound_exceeded = True
            break
        point = candidate
    # The last admissible iterate remains available even if the proposed
    # update crossed the message bound. No fixed-point claim is made then.
    step, jac = _bp_map(channel, point, llr)
    residual = float(np.max(np.abs(step-point)))
    qualified = bool(converged and residual <= atol)
    linearized = (1-damping) * np.eye(len(arcs)) + damping*jac
    radius = float(np.max(np.abs(np.linalg.eigvals(linearized))))
    return {"channel": channel, "messages": len(arcs), "iterations": iteration,
            "maxIterations": max_iterations, "llr": llr, "damping": damping,
            "fixedPointResidualInfinity": residual, "fixedPointQualified": qualified,
            "jacobianSpectralRadius": radius,
            "locallyAttracting": (radius < 1) if qualified else None,
            "messageBoundExceeded": message_bound_exceeded,
            "terminationReason": ("message-bound" if message_bound_exceeded
                                  else "fixed-point" if qualified else "iteration-limit"),
            "precision": "float64",
            "note": "stability of an authored homogeneous-LLR scalar BP fixed point, not quantum dynamics/FER"}


def paired_bethe_perturbation(graph, epsilon=0.01, swaps=16, partition=None, r=None):
    """Matched positive diagonal perturbations on original and degree-preserving control."""
    np, _, _, _ = _libraries()
    if not math.isfinite(epsilon) or not 0 < epsilon <= 0.5:
        raise ValueError("epsilon must be in (0,0.5]")
    control = degree_preserving_control(graph, swaps=swaps, partition=partition)
    chosen_r, _ = bethe_hessian(graph, r)
    results = {}
    for title, target in (("original",graph),("degreePreservingControl",control)):
        _, h = bethe_hessian(target, chosen_r)
        matrix = h.toarray()
        if matrix.shape[0] > 384:
            raise ValueError("paired full-spectrum perturbation limited to 384 vertices")
        baseline = float(np.linalg.eigvalsh(matrix)[0])
        matrix[0,0] += epsilon
        modified = float(np.linalg.eigvalsh(matrix)[0])
        results[title] = {"minimumBetheEigenvalue": baseline,
                          "perturbedMinimumEigenvalue": modified, "delta": modified-baseline}
    return {"epsilon": epsilon, "r": chosen_r, "anchorVertex": sorted(graph)[0],
            "requestedSwaps": swaps, "systems": results, "precision": "float64",
            "note": "descriptive graph potential perturbation, no p-value or physical interpretation"}


def stability_report(etq, include_nonbacktracking=True, epsilon=0.01, swaps=16):
    """JSON-safe auxiliary report; v0.2 receipt identity remains unchanged."""
    np, scipy, _, _ = _libraries()
    golay = build_tanner()
    partition = {a: "qubit" if a.startswith("q:") else "check" for a in golay}
    systems = {}
    for name, graph in (("golay", golay), ("etq", etq.adjacency)):
        projector = laplacian_projectors(graph)
        compact = {k:v for k,v in projector.items() if k != "groups"}
        compact["groups"] = [{k:v for k,v in g.items() if k != "projectorDiagonal"}
                             for g in projector["groups"]]
        entry = {"betheHessian": symmetric_spectrum(graph),
                 "laplacianProjectors": compact,
                 "pairedPotentialPerturbation": paired_bethe_perturbation(
                     graph, epsilon=epsilon, swaps=swaps,
                     partition=partition if name=="golay" else None)}
        if include_nonbacktracking:
            entry["nonBacktrackingModes"] = nonbacktracking_modes(graph)
        if name == "etq":
            entry["cartesianShiftVerification"] = verify_etq_spectral_shift(graph)
        else:
            entry["bpChannels"] = {
                c: {"trialPoint": {k:v for k,v in bp_update_and_jacobian(c).items() if k!="jacobian"},
                    "fixedPoint": bp_fixed_point_probe(c)}
                for c in ("x","z")}
        systems[name] = entry
    return {"schema": "edgewalk.stability.v0.3/auxiliary", "identityBearing": False,
            "numpyVersion": np.__version__, "scipyVersion": scipy.__version__,
            "systems": systems,
            "claimBoundary": "numerical graph/stability diagnostics, not proof of common physics or a new ETQ receipt"}
