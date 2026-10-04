#!/usr/bin/env python3
"""Prove one source-free runtime journey against the exact release image.

This release check imports the public startup kit, uses only its normal CLI/API
boundaries, and verifies exported evidence offline. It owns a unique temporary
Compose project and removes only that project's resources. It records synthetic
reviews for this test, never customer outcomes or artificial release authority.
"""

import argparse
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid

# Leave the distributed kit byte-for-byte unchanged when importing its helper.
sys.dont_write_bytecode = True


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def docker(*args):
    result = subprocess.run(["docker", *args], capture_output=True, text=True)
    require(result.returncode == 0, result.stderr.strip() or "Docker command failed")
    return result.stdout


def poll(read, ready, description):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        value = read()
        if ready(value):
            return value
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {description}")


def run(image, output):
    # A unique name and an OS-selected local port keep the check separate from
    # an evaluator's normal wald-preview project and existing Docker services.
    project = "wald-preview-check-" + uuid.uuid4().hex[:12]
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    spec = importlib.util.spec_from_file_location("wald_preview", Path(__file__).with_name("wald-preview.py"))
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    preview = kit.Preview(image=image, project=project, port=port)
    output.mkdir(parents=True, exist_ok=False)
    report = {"image": image, "project": project, "inputKind": "synthetic", "checks": [], "result": "failed"}

    def passed(name):
        report["checks"].append(name)
        print(f"PASS {name}", flush=True)

    try:
        sample = preview.up(sample=True)
        credentials = preview.load_credentials()
        identity = json.loads(docker("image", "inspect", image))[0]
        report["imageId"] = identity["Id"]
        report["platform"] = identity["Os"] + "/" + identity["Architecture"]
        container = json.loads(docker("inspect", preview.container()))[0]
        bindings = container["HostConfig"]["PortBindings"]
        require(set(bindings) == {"7070/tcp"} and all(
            address["HostIp"] == "127.0.0.1" for address in bindings["7070/tcp"]
        ), "Preview exposes a port beyond localhost")
        require(container["Config"]["User"] == "10001:10001", "Runtime must remain non-root")
        config = preview.volume_json("/data/finesample.json")
        tenant = config["tenants"][0]
        require(config["profile"] == "development" and tenant["provider"]["kind"] == "scorecard",
                "Preview must use Development and the native scorecard")
        require(all(tenant.get(key) is None for key in (
            "writeBack", "warehouseFeed", "narration", "oidc", "replication", "component"
        )), "Preview unexpectedly configures an external runtime dependency")
        passed("source-free startup, local binding, native model, no write-back")

        for path, marker in (("/", b"Sign in to the workbench"),
                             ("/v1/openapi.yaml", b"openapi:"),
                             ("/assets/instrument-sans.woff2", b"wOF2")):
            with urllib.request.urlopen(preview.url + path, timeout=15) as response:
                asset = response.read()
                require(marker in asset, f"Missing bundled UI/API asset: {path}")
                if path == "/":
                    require(b"data-finalize-review" in asset, "Workbench is missing explicit review finalization")
        try:
            preview.request("GET", "/v1/me")
        except kit.ApiError as error:
            require(error.status == 401, "Unauthenticated API request did not return 401")
        else:
            raise RuntimeError("Protected API accepted an unauthenticated request")
        summary = preview.request("GET", "/internal/workbench/summary", "analyst")
        require(summary["me"]["id"] == "analyst", "Workbench did not authenticate the local analyst")
        passed("Workbench, bundled font, OpenAPI, and authenticated live API")

        alert_path = "/v1/alerts/" + sample["alertId"]
        alert = poll(lambda: preview.request("GET", alert_path + "?include=evidence", "evidenceReader"),
                     lambda value: value["processing"]["status"] == "complete", "alert decision")
        blind = alert["decisionVisibility"] == "withheldUntilReview"
        if blind:
            require(alert["decision"] is None, "Blind sample exposed its decision before review")
            repeated_blind = preview.sample()
            require(repeated_blind["alertId"] == sample["alertId"], "Sample retry duplicated a blind alert")
            require(repeated_blind["factsVisibility"] == "withheldUntilReview"
                    and repeated_blind["receiptId"] is None, "Sample retry bypassed blind fact withholding")
            cards = preview.request("GET", "/internal/workbench/audit", "analyst")
            card = next(item for item in cards["items"] if item["id"] == alert["source"]["sourceAlertId"])
            verdict = preview.request("POST", "/internal/workbench/audit/" + urllib.parse.quote(card["key"], safe=""),
                                      "analyst", {"verdict": "legitimate"})
            cards = preview.request("GET", "/internal/workbench/audit", "analyst")
            pending = next(item for item in cards["items"] if item["key"] == card["key"])
            require(pending["reviewId"] == verdict["reviewId"], "Workbench has no finalization target for its owner")
            review = preview.request("POST", "/v1/reviews/" + verdict["reviewId"] + "/finalizations", "analyst",
                                     {"confirmation": True})
        else:
            review = preview.request("POST", alert_path + "/reviews", "analyst", {
                "type": "operational", "action": "keepHeld",
                "reasonCode": "syntheticPreviewCheck", "finalize": True,
            })
        require(review["status"] == "finalized", "Synthetic review was not finalized")
        alert = preview.request("GET", alert_path + "?include=evidence", "evidenceReader")
        require(alert["decisionVisibility"] == "available", "Review did not open decision evidence")
        decision_id = alert["decision"]["id"]
        decision = preview.request("GET", "/v1/decisions/" + decision_id, "evidenceReader")
        require(decision["id"] == decision_id, "Decision identity changed")
        require(alert["writeback"]["status"] == "notApplicable", "Preview attempted downstream write-back")
        report["resources"] = {key: value for key, value in sample.items()
                               if key.endswith("Id") or key == "eventIds"}
        report["resources"].update(decisionId=decision_id, reviewId=review["id"])
        report["reviewType"] = "blind" if blind else "operational"
        passed("synthetic review respects visibility, then exposes decision evidence")

        # This pack also defines narration facts. Its fact reads remain hidden
        # during a blind review, including computations made before the alert.
        # Inspect them only once the ordinary review boundary opens them.
        computation = preview.request("GET", "/v1/feature-computations/" + sample["computationId"], "factReader")
        require(computation["receiptId"] == sample["receiptId"], "Computation has no retained receipt")
        amount = computation["features"]["sent24h"]
        require(amount["type"] == "money" and amount["value"] == {"amount": "150.00", "currency": "USD"},
                "Typed payment history did not include both payments at the recorded boundary")
        require(computation["features"]["sentCount24h"]["value"] == 1,
                "The prior-payment count unexpectedly included the current event")
        receipt = preview.request("GET", "/v1/receipts/" + sample["receiptId"], "factReader")
        require(receipt["id"] == sample["receiptId"], "Receipt identity changed")
        passed("fresh pack discovery, typed facts, and retained receipt")

        started = preview.request("POST", "/v1/evidence-packs", "evidenceReader", {
            "target": {"type": "decision", "decisionId": decision_id},
        })
        bundle_id = started["resource"]["id"]

        def content():
            try:
                return preview.request("GET", f"/v1/evidence-packs/{bundle_id}/content", "evidenceReader")
            except kit.ApiError as error:
                if error.status == 409:
                    return None
                raise

        bundle = poll(content, lambda value: value is not None, "portable evidence bundle")
        (output / "evidence.json").write_text(json.dumps(bundle, indent=2) + "\n")
        # Trust roots come separately from the local operator's runtime, never
        # from the bundle being verified. No tenant database leaves its volume.
        roots = docker("exec", preview.container(), "/usr/local/bin/wald", "roots",
                       "--config", "/data/finesample.json", "--tenant", "preview")
        (output / "roots.json").write_text(roots)
        verified = docker("run", "--rm", "--network", "none", "--mount",
                          f"type=bind,source={output.resolve()},target=/evidence,readonly", image,
                          "verify-pack", "/evidence/evidence.json", "--roots", "/evidence/roots.json")
        verification = json.loads(verified)
        require(verification["replay"]["result"] == "identical", "Evidence did not replay identically")
        (output / "verification.json").write_text(verified)
        passed("public evidence verifies and replays offline with separate trust roots")

        preview.compose("stop", "wald")
        preview.up()
        require(preview.load_credentials() == credentials, "Restart rotated the original credentials")
        repeated = preview.sample()
        require(all(repeated[key] == sample[key] for key in ("eventIds", "alertId", "receiptId", "computationId")),
                "Repeating sample changed or duplicated its resources")
        resumed = preview.request("GET", alert_path, "evidenceReader")
        require(resumed["decision"]["id"] == decision_id, "Restart lost the original Decision")
        retained_review = preview.request("GET", "/v1/reviews/" + review["id"], "analyst")
        require(retained_review["status"] == "finalized", "Restart lost the finalized review")
        passed("restart retains credentials, pack, events, decision, review, and retry-safe sample")
        report["result"] = "passed"
        return report
    finally:
        # No global prune, image removal, or access to another Compose project.
        cleanup = preview.compose("down", "--volumes", "--remove-orphans", check=False)
        report["cleanup"] = "complete" if cleanup.returncode == 0 else "failed"
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        if cleanup.returncode:
            print(f"Cleanup failed for {project}: {cleanup.stderr.strip()}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="exact candidate image reference")
    parser.add_argument("--out", type=Path, required=True, help="new directory for non-secret release evidence")
    args = parser.parse_args()
    report = run(args.image, args.out)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"runtime-preview check: {error}", file=sys.stderr)
        sys.exit(1)
