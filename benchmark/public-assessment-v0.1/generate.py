#!/usr/bin/env python3
"""Own the deterministic input corpus for Wald Public Assessment 0.1.

The runner calls this script before `wald backtest`; it creates only synthetic,
pseudonymous JSONL inputs and checks their hashes against `assessment.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


SEED = "wald-public-assessment-v0.1:104729"
CALIBRATION_START = datetime(2024, 1, 1, 0, 30, tzinfo=timezone.utc)
EVALUATION_START = datetime(2024, 7, 1, 0, 30, tzinfo=timezone.utc)
INTERVAL = timedelta(hours=2)
OBSERVATION_LAG = timedelta(days=120)

CALIBRATION_SCENARIOS = {
    "familiarBenign": 540,
    "familiarAdverse": 6,
    "suspiciousAdverse": 54,
}
EVALUATION_SCENARIOS = {
    "familiarBenign": 520,
    "familiarAdverse": 6,
    "suspiciousAdverse": 54,
    "unfamiliarBenign": 20,
}

FILES = ("alerts.jsonl", "events.jsonl", "labels.jsonl", "references.jsonl", "state.jsonl")


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def seeded_bytes(*parts: object) -> bytes:
    material = ":".join([SEED, *(str(part) for part in parts)])
    return hashlib.sha256(material.encode("utf-8")).digest()


def ordered_scenarios(name: str, counts: dict[str, int]) -> list[str]:
    rows = [(scenario, ordinal) for scenario, count in counts.items() for ordinal in range(count)]
    rows.sort(key=lambda row: seeded_bytes(name, row[0], row[1]))
    return [scenario for scenario, _ in rows]


def line(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def amount(index: int, scenario: str) -> str:
    if scenario == "unfamiliarBenign":
        cents = 18_000 + int.from_bytes(seeded_bytes("amount", index)[:2], "big") % 1_500
    elif scenario == "suspiciousAdverse":
        cents = 24_000 + int.from_bytes(seeded_bytes("amount", index)[:2], "big") % 8_000
    else:
        cents = 4_000 + int.from_bytes(seeded_bytes("amount", index)[:2], "big") % 5_000
    return f"{cents // 100}.{cents % 100:02d}"


def feed_events(periods: Iterable[tuple[str, datetime, datetime]]) -> list[object]:
    """Keep every feed the active fraud facts read inside its freshness bound."""
    rows: list[object] = []
    specs = (
        ("authentication.failed", timedelta(hours=12)),
        ("device.changed", timedelta(hours=12)),
        ("password.reset", timedelta(days=3)),
    )
    for period, first_alert, last_alert in periods:
        for event_type, interval in specs:
            moment = first_alert - timedelta(minutes=30)
            sequence = 0
            while moment <= last_alert:
                rows.append(
                    {
                        "data": {},
                        "entityId": "feed-sentinel",
                        "entityType": "account",
                        "eventId": f"feed-{period}-{event_type.replace('.', '-')}-{sequence:05d}",
                        "eventType": event_type,
                        "occurredAt": iso(moment),
                    }
                )
                moment += interval
                sequence += 1
    return rows


def fixture_rows() -> dict[str, list[object]]:
    scenarios = [
        (CALIBRATION_START + i * INTERVAL, scenario, "calibration")
        for i, scenario in enumerate(ordered_scenarios("calibration", CALIBRATION_SCENARIOS))
    ]
    scenarios.extend(
        (EVALUATION_START + i * INTERVAL, scenario, "evaluation")
        for i, scenario in enumerate(ordered_scenarios("evaluation", EVALUATION_SCENARIOS))
    )

    last_calibration_alert = CALIBRATION_START + (sum(CALIBRATION_SCENARIOS.values()) - 1) * INTERVAL
    last_evaluation_alert = EVALUATION_START + (sum(EVALUATION_SCENARIOS.values()) - 1) * INTERVAL
    events: list[object] = feed_events(
        (
            ("calibration", CALIBRATION_START, last_calibration_alert),
            ("evaluation", EVALUATION_START, last_evaluation_alert),
        )
    )
    alerts: list[object] = []
    labels: list[object] = []
    states: list[object] = []
    trusted_devices = [f"trusted-device-{index:02d}" for index in range(8)]
    monitored_beneficiaries = [f"monitored-beneficiary-{index:02d}" for index in range(4)]

    for index, (raised_at, scenario, phase) in enumerate(scenarios):
        account = f"acct-{index:04d}"
        alert_id = f"alert-{index:04d}"
        current_event = f"payment-{index:04d}"
        suspicious = scenario == "suspiciousAdverse"
        unfamiliar = scenario == "unfamiliarBenign"
        benign = scenario in {"familiarBenign", "unfamiliarBenign"}
        risk_tier = "medium" if unfamiliar else ("high" if suspicious else "low")
        current_amount = amount(index, scenario)
        if suspicious:
            beneficiary = monitored_beneficiaries[index % len(monitored_beneficiaries)]
            device = f"risk-device-{index % 4:02d}"
        elif unfamiliar:
            beneficiary = f"novel-beneficiary-{index:04d}"
            device = f"novel-device-{index:04d}"
        else:
            beneficiary = f"ordinary-beneficiary-{index:04d}"
            device = trusted_devices[index % len(trusted_devices)]

        states.append(
            {
                "data": {"accountAgeDays": 820 + index % 700, "kycTier": "standard", "riskTier": risk_tier},
                "effectiveAt": iso(raised_at - timedelta(days=1)),
                "entityId": account,
                "source": "customerProfile",
                "stateRevisionId": f"profile-{index:04d}",
            }
        )

        common = {
            "beneficiaryId": beneficiary,
            "channel": "mobile",
            "corridor": "domestic" if not unfamiliar else "cross-border",
            "crossBorder": unfamiliar,
            "currency": "USD",
            "deviceId": device,
            "direction": "outbound",
        }
        for suffix, days, prior_amount in (("old", 60, "100.00"), ("recent", 20, "95.00")):
            events.append(
                {
                    "data": common,
                    "entityId": account,
                    "entityType": "account",
                    "eventId": f"{current_event}-{suffix}",
                    "eventType": "payment.sent",
                    "occurredAt": iso(raised_at - timedelta(days=days)),
                    "value": prior_amount,
                }
            )
        if suspicious:
            for minutes in (20, 10):
                events.append(
                    {
                        "data": {},
                        "entityId": account,
                        "entityType": "account",
                        "eventId": f"auth-{index:04d}-{minutes}",
                        "eventType": "authentication.failed",
                        "occurredAt": iso(raised_at - timedelta(minutes=minutes)),
                    }
                )
            events.append(
                {
                    "data": {},
                    "entityId": account,
                    "entityType": "account",
                    "eventId": f"change-{index:04d}",
                    "eventType": "device.changed",
                    "occurredAt": iso(raised_at - timedelta(hours=1)),
                }
            )
        events.append(
            {
                "data": common,
                "entityId": account,
                "entityType": "account",
                "eventId": current_event,
                "eventType": "payment.sent",
                "occurredAt": iso(raised_at - timedelta(seconds=1)),
                "value": current_amount,
            }
        )

        alerts.append(
            {
                "alertClass": "fraud",
                "alertId": alert_id,
                "entityId": account,
                "eventId": current_event,
                "exposure": {"amount": current_amount, "currency": "USD"},
                "raisedAt": iso(raised_at),
                "reportedPattern": "account_takeover" if suspicious else "app_scam",
                "sourceDisposition": "review",
                "sourceScore": "0.92" if suspicious else "0.18",
                "sourceSystem": "synthetic-monitor",
                "triggeringRules": ["credential-risk"] if suspicious else ["payment-anomaly"],
            }
        )
        labels.append(
            {
                "alertKey": f"synthetic-monitor:{alert_id}",
                "heldMinutes": 18 + int.from_bytes(seeded_bytes("held", index)[:2], "big") % 163,
                "observedAt": iso(raised_at + OBSERVATION_LAG),
                "outcome": "falsePositive" if benign else "fraud",
                "source": "confirmedInvestigation",
            }
        )

    references = [
        {"keys": sorted(monitored_beneficiaries), "setId": "monitoredBeneficiaries"},
        {"keys": sorted(trusted_devices), "setId": "trustedDevices"},
    ]
    events.sort(key=lambda event: (event["occurredAt"], event["eventId"]))
    return {
        "alerts.jsonl": alerts,
        "events.jsonl": events,
        "labels.jsonl": labels,
        "references.jsonl": references,
        "state.jsonl": states,
    }


def write_rows(output: Path, rows: dict[str, list[object]]) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for name in FILES:
        content = "".join(line(value) for value in rows[name]).encode("utf-8")
        (output / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    return hashes


def verify(manifest_path: Path, hashes: dict[str, str], rows: dict[str, list[object]]) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("files", {})
    if expected != hashes:
        details = json.dumps({"expected": expected, "actual": hashes}, indent=2, sort_keys=True)
        raise SystemExit(f"Generated fixture does not match {manifest_path}:\n{details}")
    if manifest.get("seed") != SEED:
        raise SystemExit(f"Generator seed does not match {manifest_path}")
    label_counts = Counter(row["outcome"] for row in rows["labels.jsonl"])
    if len(rows["alerts.jsonl"]) != manifest.get("alerts") or len(rows["labels.jsonl"]) != manifest.get("alerts"):
        raise SystemExit("Generated alert and label counts do not match assessment.json")
    if dict(sorted(label_counts.items())) != manifest.get("outcomes"):
        raise SystemExit("Generated outcome counts do not match assessment.json")


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and verify the Wald Public Assessment 0.1 fixture")
    parser.add_argument("--output", type=Path, required=True, help="Directory to receive the generated JSONL files")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("assessment.json"),
        help="Fixture definition and expected file hashes",
    )
    parser.add_argument("--print-hashes", action="store_true", help="Print generated hashes before verification")
    return parser.parse_args(arguments)


def main() -> None:
    args = parse_args()
    rows = fixture_rows()
    hashes = write_rows(args.output, rows)
    if args.print_hashes:
        print(json.dumps(hashes, indent=2, sort_keys=True))
    verify(args.manifest, hashes, rows)
    (args.output / "assessment.json").write_bytes(args.manifest.read_bytes())
    print(f"Generated and verified {len(rows['alerts.jsonl'])} labeled alerts in {args.output}")


if __name__ == "__main__":
    main()
