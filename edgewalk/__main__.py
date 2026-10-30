"""Small CLI for deterministic EDGEWALK diagnostics."""
import argparse
import json

from .core import code_parameters, walk_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="EDGEWALK v0.1 reference baseline")
    parser.add_argument("--full", action="store_true", help="include all 303 transition events")
    args = parser.parse_args()
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
