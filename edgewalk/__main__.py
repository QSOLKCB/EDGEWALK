"""EDGEWALK CLI with explicit opt-in spectral stability diagnostics."""
import argparse
import json
from .core import code_parameters, walk_receipt


def main():
    parser = argparse.ArgumentParser(description="EDGEWALK deterministic research lab")
    parser.add_argument("--full", action="store_true", help="include all v0.1 walk events")
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
