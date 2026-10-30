#!/usr/bin/env python3
"""Conservative GNATprove report assessor. NOT a compiler or self-authenticating proof."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys


def assess_report(text: str) -> dict:
    result = {"schema": "edgewalk.spark-gnatprove-assessment/v1",
              "status": "UNVERIFIED", "totalChecks": None,
              "justifiedChecks": None, "unprovedChecks": None,
              "obligations": []}
    header = next((line for line in text.splitlines()
                   if "SPARK Analysis results" in line and
                   "Justified" in line and "Unproved" in line), None)
    if header is None:
        result["obligations"].append("Missing GNATprove summary table")
        return result
    justified_at = header.index("Justified")
    unproved_at = header.index("Unproved")
    table = [line for line in text.splitlines()
             if line.lstrip().startswith(("Total ", "Run-time Checks ", "Functional Contracts "))]
    rows = {}
    for line in table:
        label = next((label for label in ("Total", "Run-time Checks", "Functional Contracts")
                      if re.match(r"^\s*" + re.escape(label) + r"\s+", line)), None)
        if label is None:
            continue
        match = re.match(r"^\s*" + re.escape(label) + r"\s+(\d+)", line)
        if match is None:
            continue
        def column_int(column):
            if column == ".":
                return 0
            m = re.match(r"^(\d+)(?:\s|$)", column)
            return int(m.group(1)) if m else None
        rows[label] = (int(match.group(1)),
                       column_int(line[justified_at:unproved_at].strip()),
                       column_int(line[unproved_at:].strip()))
    if not {"Total", "Run-time Checks", "Functional Contracts"} <= set(rows):
        result["obligations"].append("Missing required proof categories")
        return result
    total, justified, unproved = rows["Total"]
    result.update(totalChecks=total, justifiedChecks=justified, unprovedChecks=unproved)
    if total <= 0 or rows["Run-time Checks"][0] <= 0 or rows["Functional Contracts"][0] <= 0:
        result["obligations"].append("Expected SPARK verification conditions were not generated")
    if any(col is None for row in rows.values() for col in row):
        result["obligations"].append("Unrecognized GNATprove summary columns")
    if (justified is not None and justified != 0) or (unproved is not None and unproved != 0):
        result["obligations"].append("Justified or unproved obligations remain")
    if re.search(r"(?im)\b(error:|warning: no checks generated|analysis .* skipped)\b", text):
        result["obligations"].append("GNATprove emitted error/skip/no-check indication")
    if not re.search(r"gnatprove|SPARK Pro|FSF", text, re.I):
        result["obligations"].append("No credible tool invocation information")
    if not result["obligations"]:
        result["status"] = "REVIEW_REQUIRED"
        result["obligations"].append(
            "Review original GNATprove output header, per-unit analysis, toolchain digests and source SHA. Parsed summary alone cannot certify proofs.")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    if not args.report.is_file():
        status = {"status":"NOT_RUN", "obligations":["No original GNATprove report"]}
    else:
        status = assess_report(args.report.read_text(encoding="utf-8"))
    output = json.dumps(status, sort_keys=True, indent=2) + "\n"
    if args.out is not None:
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if status["status"] == "REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    sys.exit(main())
