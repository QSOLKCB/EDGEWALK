"""EDGEWALK CLI with explicit opt-in spectral stability diagnostics."""
import argparse
import json
from .core import code_parameters, walk_receipt


def main():
    parser = argparse.ArgumentParser(description="EDGEWALK deterministic research lab")
    parser.add_argument("--full", action="store_true", help="include all v0.1 walk events")
    parser.add_argument("--physical-model", metavar="MODEL_ID",
                        help="v0.6 evaluate an explicitly registered, provenance-pinned physical adapter")
    parser.add_argument("--physical-data", metavar="CSV",
                        help="optional pinned observation CSV (checksum must match registered source)")
    parser.add_argument("--verify-physical-report", metavar="FILE",
                        help="replay and verify a complete v0.6 JSON report")
    parser.add_argument("--evidence-out", metavar="NEW_DIR",
                        help="v0.5 create a fresh replayable evidence package")
    parser.add_argument("--verify-evidence", metavar="DIR",
                        help="v0.5 verify package digests and rebuild exact controls")
    parser.add_argument("--validate-etq", metavar="DIR",
                        help="v0.5 verify a complete genuine ETQ export")
    parser.add_argument("--trusted-etq-manifest-sha256", metavar="SHA256",
                        help="independently verified full-release manifest digest (required for ETQ gate)")
    parser.add_argument("--etq-bundle", metavar="DIR", help="local SONIFICATION build:v3 output, read-only")
    parser.add_argument("--numerical", action="store_true", help="v0.2 NumPy spectral eigen diagnostics")
    parser.add_argument("--stability", action="store_true", help="v0.3 optional NumPy/SciPy stability report")
    parser.add_argument("--no-nonbacktracking", action="store_true", help="skip expensive v0.3 Hashimoto eigenmodes")
    parser.add_argument("--epsilon", type=float, default=0.01, help="v0.3 potential perturbation (default: 0.01)")
    parser.add_argument("--swaps", type=int, default=16, help="deterministic control 2-switches")
    parser.add_argument("--controls", action="store_true", help="v0.4 exact null ensembles and exploratory summary")
    parser.add_argument("--control-samples", type=int, default=16, help="v0.4 ensemble size [4,128]")
    parser.add_argument("--control-swaps", type=int, default=16, help="v0.4 two-switch count [1,512]")
    parser.add_argument("--control-seed", type=int, default=303, help="v0.4 finite deterministic seed")
    parser.add_argument("--bootstrap-draws", type=int, default=256, help="v0.4 auxiliary bootstrap samples")
    parser.add_argument("--control-variants", default="reference,shear-a,shear-b",
                        help="v0.4 comma-separated Golay basis variants")
    args = parser.parse_args()
    if args.physical_model or args.verify_physical_report:
        if (args.physical_model and args.verify_physical_report
                or args.evidence_out or args.verify_evidence or args.validate_etq
                or args.etq_bundle or args.controls or args.stability or args.numerical
                or args.no_nonbacktracking or args.full or args.swaps != 16
                or args.epsilon != 0.01 or args.control_samples != 16
                or args.control_swaps != 16 or args.control_seed != 303
                or args.bootstrap_draws != 256
                or args.control_variants != "reference,shear-a,shear-b"
                or args.trusted_etq_manifest_sha256):
            parser.error("v0.6 physical actions are separate from ETQ/QEC modes")
        from .physical import run_physical_model, verify_physical_report
        if args.physical_model:
            report = run_physical_model(args.physical_model, observations_path=args.physical_data)
            print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))
        else:
            from pathlib import Path
            path = Path(args.verify_physical_report)
            if not path.is_file() or path.is_symlink() or path.stat().st_size > 65536:
                parser.error("missing/symlinked/oversized physical report")
            from .physical import _canonical
            def unique_pairs(pairs):
                obj = {}
                for key, value in pairs:
                    if key in obj:
                        raise ValueError("duplicate physical report JSON key")
                    obj[key] = value
                return obj
            try:
                raw = path.read_bytes()
                report = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                                    parse_constant=lambda value: (_ for _ in ()).throw(
                                        ValueError("non-finite JSON constant")))
                # CLI-generated JSON ends in one newline; otherwise require
                # canonical bytes and never treat a parser-normalized duplicate
                # or reformatted report as the same submitted evidence.
                core = raw[:-1] if raw.endswith(b"\n") else raw
                if core != _canonical(report):
                    raise ValueError("noncanonical physical report bytes")
            except (UnicodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
                parser.error("invalid physical report JSON: " + str(exc))
            valid = verify_physical_report(report, observations_path=args.physical_data)
            print(json.dumps({"verified": valid, "model": "kepler-earth-anchored-v1"}))
            if not valid:
                raise SystemExit(1)
        return
    if args.physical_data:
        parser.error("--physical-data requires a v0.6 physical action")
    if sum(bool(x) for x in (args.evidence_out, args.verify_evidence, args.validate_etq)) > 1:
        parser.error("choose only one v0.5 action")
    if args.trusted_etq_manifest_sha256 and not (
            args.validate_etq or ((args.evidence_out or args.verify_evidence) and args.etq_bundle)):
        parser.error("--trusted-etq-manifest-sha256 requires an ETQ v0.5 evidence/validation action")
    if args.evidence_out or args.verify_evidence or args.validate_etq:
        if (args.full or args.numerical or args.stability or args.no_nonbacktracking
                or args.controls or args.swaps != 16 or args.epsilon != 0.01):
            parser.error("v0.5 evidence actions cannot combine with legacy analysis modes")
        from .evidence import (verify_etq_release, write_evidence_package,
                               verify_evidence_package)
        if args.validate_etq:
            if args.etq_bundle or args.control_samples != 16 or args.control_swaps != 16:
                parser.error("--validate-etq is standalone")
            result = verify_etq_release(args.validate_etq,
                                        trusted_manifest_sha256=args.trusted_etq_manifest_sha256)
        elif args.verify_evidence:
            if (args.control_samples != 16 or args.control_swaps != 16
                    or args.control_seed != 303 or args.bootstrap_draws != 256
                    or args.control_variants != "reference,shear-a,shear-b"):
                parser.error("--verify-evidence replays the settings in the package")
            result = verify_evidence_package(args.verify_evidence, etq_directory=args.etq_bundle,
                                             trusted_etq_manifest_sha256=args.trusted_etq_manifest_sha256)
        else:
            result = write_evidence_package(
                args.evidence_out, etq_directory=args.etq_bundle,
                ensemble_size=args.control_samples, swaps=args.control_swaps,
                seed=args.control_seed, bootstrap_draws=args.bootstrap_draws,
                variants=tuple(args.control_variants.split(",")),
                trusted_etq_manifest_sha256=args.trusted_etq_manifest_sha256)
        print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    control_options_changed = (args.control_samples != 16 or args.control_swaps != 16
                               or args.control_seed != 303 or args.bootstrap_draws != 256
                               or args.control_variants != "reference,shear-a,shear-b")
    if args.controls:
        if (args.full or args.numerical or args.stability or args.no_nonbacktracking
                or args.swaps != 16 or args.epsilon != 0.01):
            parser.error("--controls is separate from --full, --numerical and --stability")
        from .controls import run_controlled_experiment
        etq = None
        if args.etq_bundle:
            from .etq import load_etq_bundle
            etq = load_etq_bundle(args.etq_bundle)
        result = run_controlled_experiment(
            etq, ensemble_size=args.control_samples, swaps=args.control_swaps,
            seed=args.control_seed, bootstrap_draws=args.bootstrap_draws,
            variants=tuple(args.control_variants.split(",")))
        print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    if control_options_changed:
        parser.error("v0.4 control options require --controls")
    if args.etq_bundle:
        if args.full or (args.no_nonbacktracking and not args.stability):
            parser.error("--full is baseline-only; --no-nonbacktracking requires --stability")
        from .analysis import compare
        from .etq import load_etq_bundle
        etq = load_etq_bundle(args.etq_bundle)
        report = compare(etq, numerical=args.numerical, swaps=args.swaps)
        if args.stability:
            from .stability import stability_report
            report["stabilityAuxiliary"] = stability_report(
                etq, include_nonbacktracking=not args.no_nonbacktracking,
                epsilon=args.epsilon, swaps=args.swaps)
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    if args.numerical or args.stability or args.no_nonbacktracking or args.swaps != 16 or args.epsilon != 0.01:
        parser.error("spectral and control options require --etq-bundle")
    record = walk_receipt()
    payload = record["payload"]
    report = {"schema": payload["schema"], "code": code_parameters(),
              "graph": payload["metrics"], "events": len(payload["events"]),
              "receiptDomain": record["domain"], "receiptSha256": record["sha256"],
              "scope": payload["source"]}
    if args.full:
        report["walk"] = payload["events"]
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
