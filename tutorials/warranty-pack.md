---
# Maintainer guide: This tutorial owns the public warranty pack learning path.
# It runs the released composition benchmark and explains its existing fixtures.
# Keep its image pin and expected results aligned with the warranty workflow and assessment.json.
title: Try a warranty decision pack and check its answer
audience: Domain experts and pack authors
time: 10 minutes after prerequisites
prerequisites:
  - This public repository checkout
  - Python 3, a POSIX shell, and a Docker-compatible container runtime with linux/amd64 support
  - The pinned Wald 0.1.2 image already available locally
  - shasum for the pack file check
status: Public historical composition tutorial, not a live deployment
---

# Try a warranty decision pack and check its answer

Run a warranty example through the released Wald image, verify the result,
and inspect a fact that connects claims from different customers. You will
see how a pack gives Wald a different question without changing product code.

The question is specific: can a claim leave enhanced abuse review and enter
ordinary warranty adjudication? A release here does not approve coverage,
authorize a repair, or pay the claim.

## Prepare once, before the clock starts

Run commands from this repository's root. If you do not have a checkout yet:

```sh
git clone https://github.com/finesample-lab/wald-benchmark.git
cd wald-benchmark
```

This tutorial reproduces the warranty benchmark's **Wald 0.1.2** result, not
the latest evaluator's result. Use the same immutable image as the
[warranty verification workflow](../.github/workflows/verify-warranty.yml):

```sh
export WALD_WARRANTY_IMAGE="ghcr.io/finesample-lab/wald@sha256:cb7202c48d1e502a42d0c5435a9daadcbb3336e5b0955f8c9aa4a7289ee2d95d"
docker image inspect "$WALD_WARRANTY_IMAGE" >/dev/null
```

If the image is missing, fetch it before starting the exercise:

```sh
docker pull "$WALD_WARRANTY_IMAGE"
```

Downloading the image and preparing the container runtime are outside the
10-minute target. Allow extra time if your runtime emulates linux/amd64.
Check your available disk space first. No model download,
account, API credential, or running Wald service is needed. Read the
[evaluation terms](../EVALUATION-TERMS.md) before using results commercially.

Do not substitute `v0.1.3` for this run. The
[assessment definition](../benchmark/warranty-claim-triage-v0.1/assessment.json)
pins both the evaluator version and the result hash; a different version is
not the same reproduction.

## Run and verify the warranty history

Give the runner a new output path inside a private temporary directory:

```sh
export WALD_WARRANTY_RUN="$(mktemp -d "${TMPDIR:-/tmp}/wald-warranty-tutorial.XXXXXX")"

benchmark/warranty-claim-triage-v0.1/run.sh \
  --image "$WALD_WARRANTY_IMAGE" \
  --out "$WALD_WARRANTY_RUN/results"
```

The existing runner generates 400 synthetic claims, runs all three pack
fixtures, evaluates the history, and invokes the separate verifier. Containers
have networking disabled and use `--pull never`. Inputs are mounted read-only;
the evaluator writes reports into the output directory.

Expect the three fixtures to pass and the verifier to print:

```text
Verified warranty-claim composition benchmark: sha256:5f31e404d3ef83ad2e2041edb9ca1cadbb070b605c4470743c91f64a7fba7d83
```

That line means the verifier matched the pack, fixture, report, and declared
result. It does not mean the scorecard has been independently validated on
real warranty claims. fineSample authored the pack, synthetic history,
evaluator, and verifier; the verifier is separate code, not a separate party.

## Read the result in claim terms

```sh
cat "$WALD_WARRANTY_RUN/results/backtest.md"
```

The first 200 claims form the calibration period. In the later 200-claim
evaluation period, expect:

| On this synthetic history | Expected result |
| --- | ---: |
| Claims that would leave enhanced abuse review | 153 |
| Later confirmed abuse among those claims | 3 of 153 |
| Claims kept in enhanced review | 47 |
| Release candidates later labeled no abuse found | 150 |

The adverse fraction is about 2.0%, with a two-sided 95% Wilson interval of
about 0.7% to 5.6% under a binomial model. The fixture's authored mix is not
an estimate of your queue's abuse rate or expected performance.

Any 30-hour review-time figure is arithmetic: 150 later-benign release
candidates multiplied by an assumed 12 minutes each. It is not a measured
saving. This compact benchmark also lowers the calibration minimum from the
pack's 500 samples to 150; it does not recommend that setting for production.

Keep the three output files together:

- `backtest.md` explains the result and its limitations.
- `backtest.json` contains the detailed counts and calculations.
- `assessment-manifest.json` binds the input, pack, evaluator, and output
  identities.

The runner verifies them before it exits. This historical test does not
exercise blind sampling, earn live release authority, or change a live queue.

## Inspect a fact that crosses customer histories

Open the
[serial fixture](../packs/warranty-claim-triage-v0.1/fixtures/serial_cross_customer.json).
It files claims from different customers under the same synthetic serial.
The current claim is excluded, as is a claim exactly on the 365-day edge.
Two earlier claims remain. Product registration and reviewed-list membership
arrive as separate evidence.

Print the fixture's target and exact expected answer:

```sh
python3 - <<'PY'
import json
from pathlib import Path

path = Path("packs/warranty-claim-triage-v0.1/fixtures/serial_cross_customer.json")
fixture = json.loads(path.read_text())
print(json.dumps({"compute": fixture["compute"], "expect": fixture["expect"]}, indent=2))
PY
```

Expect `priorClaims365d: 2`, `registeredAt:
"2026-01-10T09:00:00.000Z"`, `onAbuseList: true`, and no issues. The earlier
runner already executed this fixture through Wald. Printing its expectation
alone is not another execution or verification.

Follow the definition across four files:

| File | What to inspect |
| --- | --- |
| [catalog.json](../packs/warranty-claim-triage-v0.1/catalog.json) | The `serial` projection that groups events by serial rather than customer. |
| [facts.json](../packs/warranty-claim-triage-v0.1/facts.json) | `serialClaimActivity`, including the window and current-event exclusion. |
| [domain.json](../packs/warranty-claim-triage-v0.1/domain.json) | The questions, fact aliases, outcome words, and starting scorecard. |
| [release-conditions.json](../packs/warranty-claim-triage-v0.1/release-conditions.json) | The conditions for leaving enhanced review, not for paying a claim. |

## Check the pack before adapting it

Verify the published file inventory without modifying it:

```sh
packs/warranty-claim-triage-v0.1/scripts/manifest.sh
```

Every listed file should report `OK`. This checks the distributed bytes.
Together with the three executed fixtures and the verified assessment, it
gives you a reproducible starting example, not a production-ready warranty
policy.

For your own domain, start with the
[minimal complete pack](../packs/minimal-v0.1/README.md), then follow the
[authoring guide](../docs/PACK-AUTHORING.md) and
[v0.1 format reference](../docs/PACK-REFERENCE-v0.1.md). Define the release
destination and independent outcome source before changing score points.
Keep the published warranty directory unchanged so this benchmark remains
reproducible.

Whole-directory `wald pack validate` is available in Wald 0.1.3 and later,
not the 0.1.2 image used here. The
[complete-pack validation instructions](../docs/PACK-AUTHORING.md#8-validate-the-complete-pack)
cover that separate authoring step. You do not need a second image to finish
this tutorial.

## If a step fails

- Image missing: pull the exact digest above before rerunning. The runner
  deliberately cannot fetch it during the assessment.
- Container runtime unavailable: start your Docker-compatible runtime and
  repeat `docker image inspect`.
- Output path already exists: retain the previous result and choose another
  new directory. The runner will not overwrite it.
- File or result hash differs: check the image digest and restore an
  untouched public checkout. Do not edit expected hashes to make a changed
  result pass.
- A fixture fails: inspect its named facts and boundaries before changing
  the scorecard. A correct score cannot repair an incorrect input fact.

The [benchmark design](../benchmark/warranty-claim-triage-v0.1/README.md)
explains the authored scenarios, time split, maturity, and limits in detail.
