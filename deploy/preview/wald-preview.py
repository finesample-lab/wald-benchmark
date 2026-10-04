#!/usr/bin/env python3
"""Start a source-free, single-person Wald runtime preview from its public image.

This kit owns Docker Compose setup and an optional synthetic API example. The
image owns the runtime and fraud pack; its normal init, pack install, and public
API own all tenant changes. Credentials and data remain in one Docker volume.
Import Preview to drive the same journey from the release image check.
"""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


CONTRACT_VERSION = "2026-09-28"
DEFAULT_IMAGE = "ghcr.io/finesample-lab/wald:v0.2.0-beta.1"
PACK = "/usr/share/wald/packs/fraud"
PURPOSES = (
    "eventWriter", "alertWriter", "outcomeWriter", "connectorSource", "analyst",
    "artifactAuthor", "approver", "factReader", "evidenceReader",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class ApiError(RuntimeError):
    def __init__(self, method, path, status, detail):
        self.status = status
        super().__init__(f"{method} {path}: HTTP {status}: {detail}")


class Preview:
    def __init__(self, image=None, project=None, port=None):
        self.image = image or os.environ.get("WALD_IMAGE", DEFAULT_IMAGE)
        self.project = project or os.environ.get("WALD_PREVIEW_PROJECT", "wald-preview")
        self.port = int(port if port is not None else os.environ.get("WALD_PREVIEW_PORT", "7070"))
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", self.project):
            raise ValueError("project must contain lowercase letters, digits, underscores, or hyphens")
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be between 1 and 65535")
        self.url = f"http://127.0.0.1:{self.port}"
        self.env = dict(os.environ, WALD_IMAGE=self.image, WALD_PREVIEW_PORT=str(self.port))
        self.compose_file = Path(__file__).resolve().with_name("compose.yaml")
        self.tokens = None

    def compose(self, *args, extra_env=None, check=True):
        result = subprocess.run(
            ["docker", "compose", "--project-name", self.project, "--file", str(self.compose_file), *args],
            env=dict(self.env, **(extra_env or {})), capture_output=True, text=True,
        )
        if check and result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Docker Compose failed")
        return result

    def container(self):
        ids = self.compose("ps", "--all", "--quiet", "wald").stdout.split()
        if len(ids) != 1:
            raise RuntimeError("No preview container is available. Run the up command first.")
        return ids[0]

    def volume_json(self, path, missing_ok=False):
        # Docker cp also reads stopped containers. A private temporary directory
        # keeps keys off stdout and removes the host copy when the read finishes.
        with tempfile.TemporaryDirectory(prefix="wald-preview-") as directory:
            target = Path(directory) / "value.json"
            result = subprocess.run(
                ["docker", "cp", f"{self.container()}:{path}", str(target)],
                capture_output=True, text=True,
            )
            if result.returncode:
                if missing_ok and "Could not find the file" in result.stderr:
                    return None
                raise RuntimeError(result.stderr.strip() or f"Cannot read {path} from the retained volume")
            return json.loads(target.read_text())

    def load_credentials(self):
        tokens = self.volume_json("/data/preview-credentials.json")
        if not isinstance(tokens, dict) or any(not isinstance(tokens.get(p), str) or not tokens[p] for p in PURPOSES):
            raise RuntimeError("The retained credentials are incomplete. Restore the original volume; nothing was reset.")
        self.tokens = tokens
        return tokens

    def request(self, method, path, purpose=None, body=None, key=None):
        headers = {"Wald-Version": CONTRACT_VERSION}
        if purpose:
            if self.tokens is None:
                self.load_credentials()
            headers["Authorization"] = "Bearer " + self.tokens[purpose]
        data = None
        if body is not None:
            data = canonical(body).encode()
            headers["Content-Type"] = "application/json"
            headers["Idempotency-Key"] = key or (
                "preview-" + hashlib.sha256((method + path + canonical(body)).encode()).hexdigest()
            )
        req = urllib.request.Request(self.url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            raise ApiError(method, path, error.code, error.read().decode(errors="replace")) from error

    def wait_ready(self):
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try:
                if self.request("GET", "/health")["status"] == "ok":
                    return
            except (OSError, RuntimeError):
                pass
            time.sleep(0.5)
        raise RuntimeError("Wald did not start within 60 seconds. Inspect Docker Compose logs; all data was retained.")

    def up(self, sample=False):
        self.compose("create", "wald")
        config = self.volume_json("/data/finesample.json", missing_ok=True)
        if config is None:
            self.compose(
                "run", "--rm", "--no-deps", "wald", "init", "--dir", "/data", "--tenant", "preview",
                "--pack", PACK, "--listen", "0.0.0.0:7070",
                "--credentials-file", "/data/preview-credentials.json",
            )
            config = self.volume_json("/data/finesample.json")
        tenants = config.get("tenants", [])
        if (config.get("profile") != "development" or config.get("listen") != "0.0.0.0:7070"
                or len(tenants) != 1 or tenants[0].get("id") != "preview"
                or any(tenants[0].get(k) is not None for k in ("writeBack", "warehouseFeed", "narration", "oidc", "replication", "component"))
                or tenants[0].get("provider", {}).get("kind") != "scorecard"):
            raise RuntimeError("The retained configuration differs from the local preview boundary. Nothing was reset.")
        self.load_credentials()
        self.compose("up", "--detach", "--no-deps", "wald")
        self.wait_ready()
        packs = self.request("GET", "/v1/packs?limit=100", "artifactAuthor")
        if packs["hasMore"]:
            raise RuntimeError("This tenant has more packs than the bootstrap can inspect; use the public API.")
        active = [p for p in packs["data"] if p.get("activeVersion")]
        if not active:
            publication = self.compose(
                "run", "--rm", "--no-deps", "-e", "FS_SERVICE_TOKEN", "wald", "pack", "install", PACK,
                "--url", "http://wald:7070", extra_env={"FS_SERVICE_TOKEN": self.tokens["artifactAuthor"]},
            )
            change = json.loads(publication.stdout)["change"]
            if change:
                self.request("POST", f"/v1/changes/{change['id']}/signatures", "approver", {})
        elif len(active) != 1 or active[0]["name"] != "fraud":
            raise RuntimeError("An alternative pack is active. This kit does not replace your active pack.")
        return self.sample() if sample else None

    def sample(self):
        # Fixed public IDs make retries reuse the original records. Recover the
        # first event's occurrence time before constructing any later request;
        # even an interrupted sample run therefore submits identical bodies.
        ids = ["evt_01KABCDEF0123456789ABCDEFG", "evt_01KABCDEF0123456789ABCDEH0"]
        try:
            first = self.request("GET", f"/v1/events/{ids[0]}", "eventWriter")
            start = datetime.datetime.fromisoformat(first["occurredAt"].replace("Z", "+00:00"))
        except ApiError as error:
            if error.status != 404:
                raise
            start = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) - datetime.timedelta(seconds=60)
        events = []
        for index, amount in enumerate(("100.00", "50.00")):
            occurred = (start + datetime.timedelta(seconds=30 * index)).isoformat().replace("+00:00", "Z")
            events.append(self.request("POST", "/v1/events", "eventWriter", {
                "eventId": ids[index], "entityId": "preview-payer", "entityType": "account",
                "eventType": "payment.sent", "occurredAt": occurred, "value": amount,
                "data": {"currency": "USD", "beneficiaryId": "preview-beneficiary", "deviceId": "preview-device"},
            }))
        sets = self.request("GET", "/v1/feature-sets?limit=100", "factReader")
        feature_set = next((s for s in sets["data"] if s["name"] == "payerActivity"), None)
        if feature_set is None:
            raise RuntimeError("The fraud pack's payerActivity fact set is not active; run up first.")
        facts = None
        withheld = None
        try:
            facts = self.request("POST", "/v1/feature-computations", "factReader", {
                "input": {"type": "storedEvent", "eventId": events[1]["id"]},
                "featureSet": {"id": feature_set["id"], "version": "active"},
            })
        except ApiError as error:
            if error.status != 404:
                raise
            # The full fact set includes a narration-derived aggregate. After
            # the first run creates a blind task, its whole computation can
            # correctly become concealed, even on an idempotent retry.
            withheld = error
        principal = self.request("GET", "/v1/me", "alertWriter")
        alert = self.request("POST", "/v1/alerts", "alertWriter", {
            "connectorId": principal["pins"]["connectorId"], "sourceAlertId": "preview-case-2",
            "class": "fraud", "entityId": "preview-payer", "eventId": events[1]["id"],
            "occurredAt": events[1]["occurredAt"], "sourceScore": "0.20",
            "exposure": {"amount": "50.00", "currency": "USD"},
        })
        if withheld:
            current = self.request("GET", f"/v1/alerts/{alert['id']}", "evidenceReader")
            if current["decisionVisibility"] != "withheldUntilReview":
                raise withheld
        return {
            "eventIds": [event["id"] for event in events], "alertId": alert["id"],
            "featureSetId": feature_set["id"],
            "computationId": facts["id"] if facts else None,
            "receiptId": facts["receiptId"] if facts else None,
            "factsVisibility": "withheldUntilReview" if withheld else "available",
            "evidenceUrl": f"{self.url}/v1/alerts/{alert['id']}?include=evidence",
            "note": "Synthetic data only. Missing feeds remain visible. No review or outcome was fabricated.",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("up", "sample", "credentials", "stop"))
    parser.add_argument("--image", help="released image tag/digest, or an already built local image")
    parser.add_argument("--project", help="Docker Compose project (default: wald-preview)")
    parser.add_argument("--port", type=int, help="localhost port (default: 7070)")
    parser.add_argument("--sample", action="store_true", help="up: add the optional, retry-safe synthetic case")
    parser.add_argument("--purpose", choices=PURPOSES, help="credentials: print only this purpose's token")
    args = parser.parse_args()
    if args.sample and args.command != "up":
        parser.error("--sample belongs to up")
    if args.purpose and args.command != "credentials":
        parser.error("--purpose belongs to credentials")
    preview = Preview(args.image, args.project, args.port)
    if args.command == "up":
        result = preview.up(sample=args.sample)
        print(f"Wald is running at {preview.url}. API reference: {preview.url}/v1/openapi.yaml")
        print("Run credentials to display local sign-in links and purpose-specific API tokens.")
        print("Development profile: no automatic downstream release. Stop retains the data and keys.")
        if result:
            print(json.dumps(result, indent=2))
    elif args.command == "sample":
        print(json.dumps(preview.sample(), indent=2))
    elif args.command == "credentials":
        tokens = preview.load_credentials()
        if args.purpose:
            print(tokens[args.purpose])
        else:
            print("Local-only credentials. Do not paste these into shared logs or tickets.")
            for purpose in ("analyst", "artifactAuthor", "approver"):
                print(f"{purpose}: {preview.url}/#token={tokens[purpose]}")
            print(json.dumps(tokens, indent=2))
    else:
        preview.compose("stop", "wald")
        print("Wald stopped. Its volume, credentials, and records were retained. Run up to resume.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"wald-preview: {error}", file=sys.stderr)
        sys.exit(1)
