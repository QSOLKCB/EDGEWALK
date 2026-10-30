"""v0.6 independent-physics adapter: fixed Kepler benchmark and exact label null.

No implication that graph channel counts encode a spacetime signature.
"""
from __future__ import annotations

import csv
import hashlib
import io
import itertools
import json
import math
from pathlib import Path

MODEL_ID = "kepler-earth-anchored-v1"
DATASET_SHA256 = "bf891f3475f2bd1a7b302f030f9cf6f2d70859b919b0b94f56e87eabc8218c27"
SOURCE_URL = "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"
SOURCE_LAST_UPDATED = "2025-03-18"
NAMES = ("Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune")
FIELDS = ("planet", "mean_sun_distance_million_km", "sidereal_period_days")
DOMAIN = b"EDGEWALK/V6/PHYSICAL-EXACT\0"

# Complete registered protocol, fixed independently of runtime results.
PROTOCOL = {
    "id": "kepler-label-permutation-v1",
    "model": MODEL_ID,
    "equation": "P(a)=P_earth*(a/a_earth)^(3/2)",
    "distanceMeaning": "NASA mean Distance from Sun, a proxy for Keplerian semimajor axis",
    "units": {"distance": "million km", "period": "days"},
    "training": ["Earth"], "testPlanets": [name for name in NAMES if name != "Earth"],
    "statistic": "mean[(ln(P_observed)-ln(P_predicted))^2] over 7 held-out rows; smaller is better",
    "null": "All 7! uniformly assigned permutations of the 7 observed periods to the 7 fixed distances",
    "tail": "count(score_permuted<=score_observed)/7!; ties included without Monte Carlo",
    "conditionalCalibration": "Exact for the explicitly defined uniform period-label randomization null",
    "observationalLimitation": "Planets were not randomly assigned periods; exchangeability is not established as a physical data-generating mechanism",
    "registeredAlpha": "0.05 (illustrative, retrospective; public source predates this protocol)",
    "scope": "orbital-data demonstration only; no dark sector, spacetime signature or QEC hypothesis",
}


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _check(cond, message):
    if not cond:
        raise ValueError("EDGEWALK physical: " + message)


def load_observations(path=None):
    """Load exact source transcription only. No downloads or silent data substitution."""
    path = Path(path) if path is not None else Path(__file__).parent / "data" / "nasa_planetary_orbits_2025.csv"
    _check(path.is_file() and not path.is_symlink() and path.stat().st_size <= 8192,
           "observation file missing, symlinked or oversized")
    raw = path.read_bytes()
    _check(hashlib.sha256(raw).hexdigest() == DATASET_SHA256,
           "observations differ from independently recorded NASA transcription checksum")
    try:
        text = raw.decode("utf-8", "strict")
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        _check(tuple(reader.fieldnames or ()) == FIELDS, "CSV columns changed")
        rows = list(reader)
    except (UnicodeError, csv.Error) as exc:
        raise ValueError("invalid observations CSV") from exc
    _check(len(rows) == 8 and tuple(row["planet"] for row in rows) == NAMES,
           "expected exactly eight ordered planets")
    result = []
    for row in rows:
        _check(set(row) == set(FIELDS), "unexpected CSV columns")
        try:
            a = float(row[FIELDS[1]])
            p = float(row[FIELDS[2]])
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid distance/period") from exc
        _check(math.isfinite(a) and math.isfinite(p) and a > 0 and p > 0,
               "nonpositive/nonfinite distance or period")
        result.append((row["planet"], a, p))
    return tuple(result), hashlib.sha256(raw).hexdigest()


def _score(permuted_log_periods, predicted_log_periods):
    return math.fsum((observed - expected) ** 2
                     for observed, expected in zip(permuted_log_periods,
                                                   predicted_log_periods)) / 7


def run_physical_model(model=MODEL_ID, *, observations_path=None):
    """Exact enumeration of 5040 label permutations; not a cosmological test."""
    _check(model == MODEL_ID, "unregistered physical model (no implied adapters)")
    observations, data_hash = load_observations(observations_path)
    earth = observations[2]
    heldout = [row for row in observations if row[0] != "Earth"]
    predictions = [earth[2] * (a / earth[1]) ** 1.5 for _, a, _ in heldout]
    expected = tuple(math.log(p) for p in predictions)
    observed = tuple(math.log(row[2]) for row in heldout)
    observed_score = _score(observed, expected)
    extreme = 0
    total = 0
    for permutation in itertools.permutations(observed):
        extreme += (_score(permutation, expected) <= observed_score)
        total += 1
    _check(total == 5040 and 1 <= extreme <= total, "invalid exact permutation count")
    exact = {
        "schema": "edgewalk.physical-exact/v1", "model": model,
        "protocol": PROTOCOL,
        "observationSha256": data_hash,
        "sourceUrl": SOURCE_URL,
        "sourceLastUpdated": SOURCE_LAST_UPDATED,
        "permutationCount": total, "extremeOrTiedCount": extreme,
    }
    receipt = hashlib.sha256(DOMAIN + _canonical(exact)).hexdigest()
    return {
        "schema": "edgewalk.physical-report/v1", "exactEvidence": exact,
        "receiptDomain": "EDGEWALK/V6/PHYSICAL-EXACT", "receiptSha256": receipt,
        "numericalDiagnostics": {
            "logMeanSquaredError": observed_score,
            "maximumAbsoluteRelativePredictionError": max(
                abs(row[2] / predicted - 1) for row, predicted in zip(heldout, predictions)),
            "predictions": [
                {"planet": row[0], "periodDaysObserved": row[2], "periodDaysPredicted": pred}
                for row, pred in zip(heldout, predictions)
            ],
            "exactConditionalPermutationTail": extreme / total,
        },
        "calibration": {
            "nullExactlyEnumerated": True,
            "conditionalLabelNullValid": True,
            "observationalExchangeabilityEstablished": False,
            "astronomicalInferenceCalibrated": False,
            "reason": "Uniform random period-label assignment is a defined conditional null, not an established physical observation process",
        },
        "findings": {
            "orbitalRelation": "observed fit and conditional-label tail computed; retrospective",
            "physicalDarkSector": "NOT TESTED",
            "physicalSpacetimeQEC": "NOT TESTED",
            "signature3plus2": "NOT TESTED: no spacetime signature follows from engineering channel counts",
        },
    }


def verify_physical_report(report, *, observations_path=None):
    """Rebuild entire report and compare canonical bytes; no self-authenticating inputs."""
    if not isinstance(report, dict):
        return False
    try:
        rebuilt = run_physical_model(report["exactEvidence"]["model"],
                                     observations_path=observations_path)
        return _canonical(report) == _canonical(rebuilt)
    except (KeyError, ValueError, TypeError, OverflowError):
        return False
