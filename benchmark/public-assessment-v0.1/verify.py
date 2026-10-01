#!/usr/bin/env python3
"""Verifies the public benchmark's inputs, outputs, and declared result.

The shell runner calls this after `wald backtest`; it independently checks
ordinary SHA-256 hashes and Wald's canonical assessment statement and result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Assessment verification failed: {message}")


def verify_file_entries(entries: Any, base: Path, kind: str) -> None:
    require(isinstance(entries, list), f"manifest {kind} must be an array")
    seen: set[str] = set()
    for entry in entries:
        require(isinstance(entry, dict), f"manifest {kind} entry must be an object")
        path = entry.get("path")
        require(isinstance(path, str) and path and Path(path).name == path, f"invalid {kind} path {path!r}")
        require(path not in seen, f"duplicate {kind} path {path}")
        seen.add(path)
        content = (base / path).read_bytes()
        require(entry.get("bytes") == len(content), f"{kind} byte count differs for {path}")
        require(entry.get("sha256") == sha256(content), f"{kind} SHA-256 differs for {path}")


def verify(definition_path: Path, fixture: Path, result: Path) -> None:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    manifest_path = result / "assessment-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    claimed_statement = manifest.get("assessmentStatementSha256")
    statement = dict(manifest)
    statement.pop("assessmentStatementSha256", None)
    require(claimed_statement == sha256(canonical(statement)), "assessmentStatementSha256 is not canonical")

    inputs = manifest.get("dataset", {}).get("files")
    outputs = manifest.get("outputs")
    verify_file_entries(inputs, fixture, "input")
    verify_file_entries(outputs, result, "output")

    input_hashes = {entry["path"]: entry["sha256"] for entry in inputs}
    for path, digest in definition.get("files", {}).items():
        require(input_hashes.get(path) == f"sha256:{digest}", f"manifest does not bind pinned input {path}")
    require("assessment.json" in input_hashes, "manifest does not bind assessment.json")

    report = json.loads((result / "backtest.json").read_text(encoding="utf-8"))
    result_summary = manifest.get("result")
    require(isinstance(result_summary, dict), "manifest result must be an object")
    require(result_summary.get("sha256") == sha256(canonical(report)), "manifest result SHA-256 differs")
    split = report.get("split")
    require(isinstance(split, dict), "report has no chronological split")
    require(
        split.get("calibrationAlerts") == definition.get("calibrationAlerts"),
        "report calibration count differs from assessment.json",
    )
    require(
        split.get("evaluationAlerts") == definition.get("evaluationAlerts"),
        "report evaluation count differs from assessment.json",
    )
    require(split.get("evaluationFrom") == definition.get("splitAt"), "report split differs from assessment.json")
    calibration = report.get("calibrationFit")
    require(isinstance(calibration, dict), "report has no calibrationFit evidence")
    require(calibration.get("active") is True, "calibration fit is not active")
    require(calibration.get("sampleSize", 0) >= 500, "calibration fit used fewer than 500 labels")
    require(calibration.get("historicalSamples", 0) >= 500, "calibration fit used fewer than 500 historical labels")

    expected = definition.get("expected")
    require(isinstance(expected, dict) and expected, "assessment.json has no expected result baseline")
    require(
        manifest.get("evaluator", {}).get("waldVersion") == definition.get("version"),
        "evaluator Wald version differs from the 0.1 definition",
    )
    require(manifest.get("pack", {}).get("sha256") == expected.get("packSha256"), "pack differs from the 0.1 baseline")
    require(result_summary.get("sha256") == expected.get("resultSha256"), "result differs from the 0.1 baseline")
    for field in (
        "evaluationAlerts",
        "evaluationLabeled",
        "wouldReleaseLabeled",
        "wouldReleaseAdverse",
        "analystMinutesSaved",
    ):
        require(result_summary.get(field) == expected.get(field), f"headline metric {field} differs from the 0.1 baseline")
        require(report.get(field) == expected.get(field), f"backtest metric {field} differs from the 0.1 baseline")

    print(f"Verified Wald Public Benchmark 0.1: {result_summary['sha256']}")


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a Wald Public Benchmark 0.1 result")
    parser.add_argument("--fixture", type=Path, required=True, help="Generated fixture directory")
    parser.add_argument("--result", type=Path, required=True, help="Wald assessment output directory")
    parser.add_argument("--definition", type=Path, required=True, help="Pinned assessment.json definition")
    return parser.parse_args(arguments)


def main() -> None:
    args = parse_args()
    verify(args.definition, args.fixture, args.result)


if __name__ == "__main__":
    main()
