"""EDGEWALK CLI: baseline retained; ETQ comparison is explicit opt-in."""
import argparse
import json

from .core import code_parameters, walk_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="EDGEWALK deterministic research lab")
    parser.add_argument("--full", action="store_true", help="include all v0.1 walk events")
    parser.add_argument("--etq-bundle", metavar="DIR", help="local SONIFICATION build:v3 output (read-only)")
    parser.add_argument("--numerical", action="store_true", help="opt-in NumPy spectral eigen diagnostics")
    parser.add_argument("--swaps", type=int, default=16, help="degree-preserving diagnostic swaps (default: 16)")
    args = parser.parse_args()
    if args.etq_bundle:
        from .analysis import compare
        from .etq import load_etq_bundle
        if args.full:
            parser.error("--full is only valid with the v0.1 baseline")
        report = compare(load_etq_bundle(args.etq_bundle), numerical=args.numerical, swaps=args.swaps)
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))
        return
    if args.numerical or args.swaps != 16:
        parser.error("--numerical and --swaps require --etq-bundle")
    record = walk_receipt()
    payload = record["payload"]
    report = {
        "schema": payload["schema"],
        "code": code_parameters(),
        "graph": payload["metrics"],
        "events": len(payload["events"]),
        "receiptDomain": record["domain"],
        "receiptSha256": record["sha256"],
        "scope": payload["source"],
    }
    if args.full:
        report["walk"] = payload["events"]
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
