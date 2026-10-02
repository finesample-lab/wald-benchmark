#!/usr/bin/env python3
"""Independently verify this benchmark's pack, inputs, and Wald outputs.

The shell runner calls this stdlib-only program after `wald backtest`. It does
not import the generator or Wald; it checks byte hashes, canonical statements,
declared arithmetic, and the deliberately narrow non-live scope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Warranty assessment verification failed: {message}")


def files_below(directory: Path) -> dict[str, str]:
    require(directory.is_dir(), f"directory is missing: {directory}")
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def verify_entries(entries: Any, base: Path, kind: str) -> dict[str, dict[str, Any]]:
    require(isinstance(entries, list), f"manifest {kind} must be an array")
    found: dict[str, dict[str, Any]] = {}
    for entry in entries:
        require(isinstance(entry, dict), f"manifest {kind} entry must be an object")
        path = entry.get("path")
        require(isinstance(path, str) and path and Path(path).name == path, f"invalid {kind} path {path!r}")
        require(path not in found, f"duplicate {kind} path {path}")
        content = (base / path).read_bytes()
        require(entry.get("bytes") == len(content), f"{kind} byte count differs for {path}")
        require(entry.get("sha256") == sha256(content), f"{kind} SHA-256 differs for {path}")
        found[path] = entry
    return found


def verify_pack(definition: dict[str, Any], pack: Path, manifest: dict[str, Any]) -> None:
    expected_files = definition.get("packFiles")
    require(isinstance(expected_files, dict) and expected_files, "assessment.json has no pack-file baseline")
    require(files_below(pack) == expected_files, "published pack bytes differ from assessment.json")

    digest_lines = (pack / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    digest_inventory: dict[str, str] = {}
    for line_number, line in enumerate(digest_lines, start=1):
        parts = line.split("  ", 1)
        require(len(parts) == 2 and len(parts[0]) == 64, f"invalid pack manifest line {line_number}")
        digest, path = parts
        require(path not in digest_inventory, f"duplicate pack manifest path {path}")
        digest_inventory[path] = digest
    expected_inventory = {path: digest for path, digest in expected_files.items() if path != "MANIFEST.sha256"}
    require(digest_inventory == expected_inventory, "pack digest inventory is incomplete or differs")

    metadata = json.loads((pack / "pack.json").read_text(encoding="utf-8"))
    require(metadata.get("id") == definition.get("pack"), "pack identity differs")
    require(metadata.get("version") == definition.get("packVersion"), "pack version differs")
    require(metadata.get("license") == "MIT", "pack metadata does not declare its MIT licence")

    decision_pack = {
        "catalog": json.loads((pack / "catalog.json").read_text(encoding="utf-8")),
        "domain": json.loads((pack / "domain.json").read_text(encoding="utf-8")),
        "facts": json.loads((pack / "facts.json").read_text(encoding="utf-8")),
        "releaseConditions": json.loads((pack / "release-conditions.json").read_text(encoding="utf-8")),
    }
    pack_hash = sha256(canonical(decision_pack))
    require(pack_hash == definition.get("expected", {}).get("packSha256"), "runtime decision-pack hash differs")
    require(manifest.get("pack", {}).get("sha256") == pack_hash, "assessment manifest names a different pack")


def verify_threshold_override(definition: dict[str, Any], fixture: Path, pack: Path) -> None:
    published = json.loads((pack / "settings" / "thresholds.json").read_text(encoding="utf-8"))
    expected = dict(published)
    expected["minCalibrationSamples"] = definition.get("minCalibrationSamples")
    generated = json.loads((fixture / "thresholds.json").read_text(encoding="utf-8"))
    require(generated == expected, "fixture changes more than the declared calibration-sample minimum")


def wilson(adverse: int, total: int) -> tuple[str, str]:
    require(total > 0 and 0 <= adverse <= total, "invalid Wilson inputs")
    z = 1.959963984540054
    p = adverse / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = p + z2 / (2.0 * total)
    margin = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)
    return f"{max(0.0, (center - margin) / denominator):.6f}", f"{min(1.0, (center + margin) / denominator):.6f}"


def verify(definition_path: Path, fixture: Path, pack: Path, result: Path) -> None:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    manifest = json.loads((result / "assessment-manifest.json").read_text(encoding="utf-8"))

    claimed_statement = manifest.get("assessmentStatementSha256")
    statement = dict(manifest)
    statement.pop("assessmentStatementSha256", None)
    require(claimed_statement == sha256(canonical(statement)), "assessmentStatementSha256 is not canonical")

    inputs = verify_entries(manifest.get("dataset", {}).get("files"), fixture, "input")
    outputs = verify_entries(manifest.get("outputs"), result, "output")
    expected_input_names = set(definition.get("files", {})) | {"assessment.json"}
    require(set(inputs) == expected_input_names, "manifest input inventory differs from the pinned fixture")
    require(set(files_below(fixture)) == expected_input_names, "fixture contains unbound files")
    for path, digest in definition.get("files", {}).items():
        require(inputs[path].get("sha256") == f"sha256:{digest}", f"manifest does not bind pinned input {path}")
    require(inputs["assessment.json"].get("sha256") == sha256(definition_path.read_bytes()), "assessment.json is unbound")

    actual_result_names = set(files_below(result))
    require(actual_result_names == set(outputs) | {"assessment-manifest.json"}, "result contains an unbound output")
    report = json.loads((result / "backtest.json").read_text(encoding="utf-8"))
    result_summary = manifest.get("result")
    require(isinstance(result_summary, dict), "manifest result must be an object")
    result_hash = sha256(canonical(report))
    require(result_summary.get("sha256") == result_hash, "manifest result SHA-256 differs")

    verify_pack(definition, pack, manifest)
    verify_threshold_override(definition, fixture, pack)
    expected = definition.get("expected")
    require(isinstance(expected, dict) and expected, "assessment.json has no expected baseline")
    require(result_hash == expected.get("resultSha256"), "result differs from the pinned baseline")
    require(manifest.get("evaluator", {}).get("waldVersion") == definition.get("version"), "Wald version differs")

    scope = manifest.get("scope", {})
    require(scope.get("counterfactual") is True, "manifest does not identify the counterfactual scope")
    for field in ("liveAction", "blindSamplingExercised", "liveAuthorityGranted", "liveQueueChanged"):
        require(scope.get(field) is False, f"manifest unexpectedly claims {field}")
    limitations = manifest.get("limitations", [])
    require(
        "This backtest does not exercise blind sampling, grant live release authority, or change a live queue."
        in limitations,
        "manifest omits the live-authority limitation",
    )

    split = report.get("split")
    require(isinstance(split, dict), "report has no chronological split")
    require(split.get("calibrationAlerts") == definition.get("calibrationAlerts"), "calibration count differs")
    require(split.get("evaluationAlerts") == definition.get("evaluationAlerts"), "evaluation count differs")
    require(split.get("evaluationFrom") == definition.get("splitAt"), "evaluation boundary differs")
    require(split.get("equalTimestampsCrossBoundary") is False, "equal timestamps crossed the boundary")
    maturity = report.get("labelMaturity", {})
    require(maturity.get("evaluationCutoff") == definition.get("asOf"), "label maturity cutoff differs")
    require(maturity.get("calibrationLateExcluded") == 0, "calibration labels were not mature")
    require(maturity.get("evaluationLateExcluded") == 0, "evaluation labels were not mature")

    calibration = report.get("calibrationFit")
    require(isinstance(calibration, dict) and calibration.get("active") is True, "calibration fit is not active")
    minimum = definition.get("minCalibrationSamples")
    require(minimum == 150, "unexpected compact-track calibration minimum")
    require(calibration.get("sampleSize", 0) >= minimum, "calibration fit used too few labels")
    require(calibration.get("historicalSamples", 0) >= minimum, "calibration history used too few labels")
    require(report.get("domain") == "warrantyTriage", "unexpected decision domain")
    require(report.get("outcomes", {}).get("adverse", {}).get("key") == "abuse_confirmed", "adverse word differs")
    require(report.get("outcomes", {}).get("benign", {}).get("key") == "no_abuse_found", "benign word differs")
    require(report.get("eventsRejected") == 0, "one or more input events were rejected")
    require(report.get("modelAnswers") is False, "benchmark unexpectedly used recorded model answers")

    for field in (
        "evaluationAlerts",
        "evaluationLabeled",
        "wouldReleaseLabeled",
        "wouldReleaseAdverse",
    ):
        require(report.get(field) == expected.get(field), f"report metric {field} differs")
        require(result_summary.get(field) == expected.get(field), f"manifest metric {field} differs")
    for field in (
        "wouldRelease",
        "wouldReleaseBenign",
        "wouldReleaseWithoutFamiliarity",
        "wouldReleaseWithoutFamiliarityAdverse",
    ):
        require(report.get(field) == expected.get(field), f"report metric {field} differs")

    release = report.get("labeledRelease", {})
    adverse = release.get("adverse")
    denominator = release.get("denominator")
    require(adverse == report.get("wouldReleaseAdverse"), "release adverse numerator differs")
    require(denominator == report.get("wouldReleaseLabeled"), "release denominator differs")
    require(release.get("adverseRate") == f"{adverse / denominator:.6f}", "adverse point estimate differs")
    lower, upper = wilson(adverse, denominator)
    require(release.get("adverseRateWilson95Lower") == lower, "Wilson lower bound differs")
    require(release.get("adverseRateWilson95Upper") == upper, "Wilson upper bound differs")

    review = report.get("reviewTimeArithmetic", {})
    minutes = expected.get("illustrativeReviewMinutes")
    require(review.get("laterBenignReleaseCandidates") == report.get("wouldReleaseBenign"), "review count differs")
    require(review.get("assumedMinutesPerReview") == definition.get("minutesPerReview"), "review assumption differs")
    require(
        minutes == report.get("wouldReleaseBenign") * definition.get("minutesPerReview"),
        "illustrative review arithmetic is inconsistent",
    )
    require(review.get("illustrativeReviewMinutes") == minutes, "illustrative review minutes differ")
    require(report.get("analystMinutesSaved") == minutes, "compatibility review-minutes alias differs")
    require(result_summary.get("reviewTimeArithmetic") == review, "manifest review arithmetic differs")
    require(result_summary.get("analystMinutesSaved") == minutes, "manifest compatibility alias differs")

    narration = report.get("narrationCoverage", {})
    require(narration.get("evaluation", {}).get("narration") == 0, "structured pack unexpectedly used narration")
    require(
        narration.get("evaluation", {}).get("structured") == definition.get("evaluationAlerts"),
        "structured evaluation coverage differs",
    )

    markdown = (result / "backtest.md").read_text(encoding="utf-8")
    require(f"{adverse}/{denominator} were abuse confirmed" in markdown, "Markdown omits the adverse fraction")
    require(
        "under a binomial model, the two-sided 95% Wilson interval" in markdown,
        "Markdown omits the binomial-model Wilson caveat",
    )
    require(
        f"over the {report['wouldReleaseBenign']} release candidates later labeled no abuse found" in markdown,
        "Markdown omits the later-benign arithmetic population",
    )
    require("This is not an observed saving" in markdown, "Markdown presents arithmetic as observed savings")
    require(
        "does not exercise blind sampling, grant live release authority, or change a live queue" in markdown,
        "Markdown omits the live-authority limitation",
    )

    print(f"Verified warranty-claim composition benchmark: {result_hash}")


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the warranty-claim composition benchmark")
    parser.add_argument("--definition", type=Path, required=True, help="Pinned assessment.json definition")
    parser.add_argument("--fixture", type=Path, required=True, help="Generated input directory")
    parser.add_argument("--pack", type=Path, required=True, help="Published warranty decision-pack directory")
    parser.add_argument("--result", type=Path, required=True, help="Wald assessment output directory")
    return parser.parse_args(arguments)


def main() -> None:
    args = parse_args()
    verify(args.definition, args.fixture, args.pack, args.result)


if __name__ == "__main__":
    main()
