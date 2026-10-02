#!/usr/bin/env python3
"""Own the deterministic warranty-claim history used by this benchmark.

The runner calls this script before `wald backtest`; it writes only synthetic,
pseudonymous JSONL inputs, pins their bytes, and verifies the separate public
decision pack without importing Wald or its implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


SEED = "wald-warranty-claim-triage-v0.1:104729"
CALIBRATION_START = datetime(2025, 1, 1, 0, 30, tzinfo=timezone.utc)
EVALUATION_START = datetime(2025, 6, 1, 0, 30, tzinfo=timezone.utc)
INTERVAL = timedelta(hours=2)
OBSERVATION_LAG = timedelta(days=120)

CALIBRATION_SCENARIOS = {
    "familiarBenign": 164,
    "familiarAdverse": 3,
    "obviousAdverse": 33,
}
EVALUATION_SCENARIOS = {
    "familiarBenign": 150,
    "familiarAdverse": 3,
    "obviousAdverse": 37,
    "unfamiliarBenign": 10,
}
JSONL_FILES = (
    "alerts.jsonl",
    "events.jsonl",
    "labels.jsonl",
    "references.jsonl",
    "state.jsonl",
)
FIXTURE_FILES = (*JSONL_FILES, "thresholds.json")


def iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def seeded_bytes(*parts: object) -> bytes:
    material = ":".join([SEED, *(str(part) for part in parts)])
    return hashlib.sha256(material.encode("utf-8")).digest()


def ordered_scenarios(period: str, counts: dict[str, int]) -> list[str]:
    rows = [(scenario, ordinal) for scenario, count in counts.items() for ordinal in range(count)]
    rows.sort(key=lambda row: seeded_bytes(period, row[0], row[1]))
    return [scenario for scenario, _ in rows]


def line(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def amount(index: int, scenario: str) -> str:
    base = 12_000 if scenario == "unfamiliarBenign" else 4_000
    cents = base + int.from_bytes(seeded_bytes("amount", index)[:2], "big") % 3_000
    return f"{cents // 100}.{cents % 100:02d}"


def feed_events(periods: Iterable[tuple[str, datetime, datetime]]) -> list[dict[str, Any]]:
    """Keep each feed read by the pack inside its declared freshness bound."""
    rows: list[dict[str, Any]] = []
    specs = (
        ("claim.investigated", timedelta(days=15)),
        ("purchase.completed", timedelta(days=3)),
        ("service.completed", timedelta(days=3)),
        ("product.registered", timedelta(days=15)),
    )
    for period, first_alert, last_alert in periods:
        for event_type, interval in specs:
            moment = first_alert - timedelta(minutes=30)
            sequence = 0
            while moment <= last_alert:
                data: dict[str, Any] = {}
                if event_type == "claim.investigated":
                    data["investigationFinding"] = "inconclusive"
                if event_type == "product.registered":
                    data["serialNumber"] = f"SERIAL-FEED-{period}-{sequence:03d}"
                rows.append(
                    {
                        "data": data,
                        "entityId": f"customer-feed-{period}",
                        "entityType": "customer",
                        "eventId": f"feed-{period}-{event_type.replace('.', '-')}-{sequence:03d}",
                        "eventType": event_type,
                        "occurredAt": iso(moment),
                    }
                )
                moment += interval
                sequence += 1
    return rows


def claim_event(
    *,
    event_id: str,
    customer: str,
    serial: str,
    occurred_at: datetime,
    claim_amount: str,
) -> dict[str, Any]:
    return {
        "data": {
            "amount": claim_amount,
            "channel": "online",
            "claimId": event_id,
            "currency": "USD",
            "failureCode": "battery",
            "productCategory": "headphones",
            "serialNumber": serial,
        },
        "entityId": customer,
        "entityType": "customer",
        "eventId": event_id,
        "eventType": "claim.filed",
        "occurredAt": iso(occurred_at),
    }


def fixture_rows(thresholds: dict[str, Any]) -> dict[str, Any]:
    scenarios = [
        (CALIBRATION_START + i * INTERVAL, scenario, "calibration")
        for i, scenario in enumerate(ordered_scenarios("calibration", CALIBRATION_SCENARIOS))
    ]
    scenarios.extend(
        (EVALUATION_START + i * INTERVAL, scenario, "evaluation")
        for i, scenario in enumerate(ordered_scenarios("evaluation", EVALUATION_SCENARIOS))
    )

    last_calibration = CALIBRATION_START + (sum(CALIBRATION_SCENARIOS.values()) - 1) * INTERVAL
    last_evaluation = EVALUATION_START + (sum(EVALUATION_SCENARIOS.values()) - 1) * INTERVAL
    events = feed_events(
        (
            ("calibration", CALIBRATION_START, last_calibration),
            ("evaluation", EVALUATION_START, last_evaluation),
        )
    )
    alerts: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    states: list[dict[str, Any]] = []
    listed_serials: list[str] = []

    for index, (raised_at, scenario, _period) in enumerate(scenarios):
        customer = f"customer-{index:04d}"
        serial = f"SERIAL-{index:04d}"
        old_serial = f"SERIAL-OLD-{index:04d}"
        alert_id = f"warranty-alert-{index:04d}"
        current_event_id = f"claim-{index:04d}"
        obvious = scenario == "obviousAdverse"
        unfamiliar = scenario == "unfamiliarBenign"
        benign = scenario in {"familiarBenign", "unfamiliarBenign"}
        claim_amount = amount(index, scenario)

        states.append(
            {
                "data": {"tenureDays": 10 if unfamiliar else 720, "tier": "gold" if not obvious else "standard"},
                "effectiveAt": iso(raised_at - timedelta(days=1)),
                "entityId": customer,
                "source": "customerProfile",
                "stateRevisionId": f"profile-{index:04d}",
            }
        )
        events.append(
            {
                "data": {"serialNumber": serial},
                "entityId": customer,
                "entityType": "customer",
                "eventId": f"registration-{index:04d}",
                "eventType": "product.registered",
                "occurredAt": iso(raised_at - timedelta(days=60)),
            }
        )
        events.append(
            {
                "data": {},
                "entityId": customer,
                "entityType": "customer",
                "eventId": f"purchase-{index:04d}",
                "eventType": "purchase.completed",
                "occurredAt": iso(raised_at - timedelta(days=45)),
            }
        )
        events.append(
            claim_event(
                event_id=f"prior-claim-{index:04d}",
                customer=customer,
                serial=old_serial,
                occurred_at=raised_at - timedelta(days=20 if obvious else 45),
                claim_amount="39.00",
            )
        )

        if obvious:
            listed_serials.append(serial)
            events.append(
                claim_event(
                    event_id=f"serial-prior-claim-{index:04d}",
                    customer=f"customer-prior-{index:04d}",
                    serial=serial,
                    occurred_at=raised_at - timedelta(days=15),
                    claim_amount="59.00",
                )
            )
            events.append(
                {
                    "data": {"investigationFinding": "abuse_confirmed"},
                    "entityId": customer,
                    "entityType": "customer",
                    "eventId": f"investigation-{index:04d}",
                    "eventType": "claim.investigated",
                    "occurredAt": iso(raised_at - timedelta(days=10)),
                }
            )

        events.append(
            claim_event(
                event_id=current_event_id,
                customer=customer,
                serial=serial,
                occurred_at=raised_at - timedelta(seconds=1),
                claim_amount=claim_amount,
            )
        )
        alert: dict[str, Any] = {
            "alertClass": "claimRisk",
            "alertId": alert_id,
            "entityId": customer,
            "eventId": current_event_id,
            "exposure": {"amount": claim_amount, "currency": "USD"},
            "raisedAt": iso(raised_at),
            "sourceDisposition": "review",
            "sourceScore": "0.94" if obvious else "0.16",
            "sourceSystem": "synthetic-warranty-monitor",
            "triggeringRules": ["reviewed-serial"] if obvious else ["claim-screen"],
        }
        if obvious:
            alert["reportedPattern"] = "serial_recycling"
        alerts.append(alert)
        labels.append(
            {
                "alertKey": f"synthetic-warranty-monitor:{alert_id}",
                "heldMinutes": 20 + int.from_bytes(seeded_bytes("held", index)[:2], "big") % 161,
                "observedAt": iso(raised_at + OBSERVATION_LAG),
                "outcome": "no_abuse_found" if benign else "abuse_confirmed",
                "source": "claimInvestigation",
            }
        )

    events.sort(key=lambda event: (event["occurredAt"], event["eventId"]))
    references = [{"keys": sorted(listed_serials), "setId": "abuseSerials"}]
    return {
        "alerts.jsonl": alerts,
        "events.jsonl": events,
        "labels.jsonl": labels,
        "references.jsonl": references,
        "state.jsonl": states,
        "thresholds.json": thresholds,
    }


def payloads(rows: dict[str, Any]) -> dict[str, bytes]:
    result = {
        name: "".join(line(value) for value in rows[name]).encode("utf-8")
        for name in JSONL_FILES
    }
    result["thresholds.json"] = (
        json.dumps(rows["thresholds.json"], indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    return result


def write_payloads(output: Path, contents: dict[str, bytes]) -> dict[str, str]:
    output.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for name in FIXTURE_FILES:
        content = contents[name]
        (output / name).write_bytes(content)
        hashes[name] = hashlib.sha256(content).hexdigest()
    return hashes


def directory_hashes(directory: Path) -> dict[str, str]:
    if not directory.is_dir():
        raise SystemExit(f"Pack directory does not exist: {directory}")
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def verify(definition_path: Path, pack: Path, hashes: dict[str, str], rows: dict[str, Any]) -> None:
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    if definition.get("files") != hashes:
        detail = json.dumps({"expected": definition.get("files"), "actual": hashes}, indent=2, sort_keys=True)
        raise SystemExit(f"Generated fixture does not match {definition_path}:\n{detail}")
    actual_pack_hashes = directory_hashes(pack)
    if definition.get("packFiles") != actual_pack_hashes:
        detail = json.dumps(
            {"expected": definition.get("packFiles"), "actual": actual_pack_hashes}, indent=2, sort_keys=True
        )
        raise SystemExit(f"Public pack does not match {definition_path}:\n{detail}")
    if definition.get("seed") != SEED:
        raise SystemExit(f"Generator seed does not match {definition_path}")
    if rows["thresholds.json"]["minCalibrationSamples"] != definition.get("minCalibrationSamples"):
        raise SystemExit("Generated calibration minimum does not match assessment.json")
    labels = rows["labels.jsonl"]
    counts = Counter(row["outcome"] for row in labels)
    if len(rows["alerts.jsonl"]) != definition.get("alerts") or len(labels) != definition.get("alerts"):
        raise SystemExit("Generated alert and label counts do not match assessment.json")
    if dict(sorted(counts.items())) != definition.get("outcomes"):
        raise SystemExit("Generated outcome counts do not match assessment.json")
    composition = {
        "calibration": CALIBRATION_SCENARIOS,
        "evaluation": EVALUATION_SCENARIOS,
    }
    if definition.get("composition") != composition:
        raise SystemExit("Scenario composition does not match assessment.json")


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the synthetic warranty-claim benchmark history")
    parser.add_argument("--output", type=Path, required=True, help="Directory to receive generated inputs")
    parser.add_argument(
        "--definition",
        type=Path,
        default=Path(__file__).with_name("assessment.json"),
        help="Fixture definition and expected byte hashes",
    )
    parser.add_argument("--pack", type=Path, required=True, help="Published warranty decision-pack directory")
    parser.add_argument("--print-hashes", action="store_true", help="Print generated fixture and pack hashes")
    return parser.parse_args(arguments)


def main() -> None:
    args = parse_args()
    definition = json.loads(args.definition.read_text(encoding="utf-8"))
    thresholds = json.loads((args.pack / "settings" / "thresholds.json").read_text(encoding="utf-8"))
    thresholds["minCalibrationSamples"] = definition.get("minCalibrationSamples")
    rows = fixture_rows(thresholds)
    hashes = write_payloads(args.output, payloads(rows))
    if args.print_hashes:
        print(json.dumps({"files": hashes, "packFiles": directory_hashes(args.pack)}, indent=2, sort_keys=True))
    verify(args.definition, args.pack, hashes, rows)
    (args.output / "assessment.json").write_bytes(args.definition.read_bytes())
    print(f"Generated and verified {len(rows['alerts.jsonl'])} labeled warranty claims in {args.output}")


if __name__ == "__main__":
    main()
