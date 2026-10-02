# Wald Public Benchmark 0.1

This directory owns the reproducible public benchmark for Wald's free historical evaluator. It generates synthetic alerts and independently observed outcomes, checks their hashes, and sends them through the same `wald backtest` path used for an institution's export; it never changes a live queue or replaces evaluation on an institution's own outcomes.

## What it answers

The assessment asks one deliberately narrow question:

> On this fixed history, which alerts would Wald have sent back to the existing review process, which would it have identified as release opportunities, and what later outcomes were observed?

It is useful for inspecting Wald's result shape, replaying the same inputs, and checking that a release image produces the declared assessment. It is not customer evidence, a safety certification, a live drift exercise, or competitive proof. A public fixture can be recognized and optimized for; it cannot establish what will happen on a new institution's alerts.

## Run it

The supported public path uses the released image:

```sh
benchmark/public-assessment-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald:v0.1.1 \
  --out /tmp/wald-assessment-0.1
```

Maintainers can exercise an explicit local build without giving the public runner any knowledge of Wald's private source tree:

```sh
WALD_BIN=/absolute/path/to/wald \
  benchmark/public-assessment-v0.1/run.sh \
  --out /tmp/wald-assessment-0.1
```

The output directory must not already exist. The runner never overwrites an earlier result.
For an image run it mounts only the generated fixture and the output directory's existing parent, creates the named result as a fresh child under the host user's UID and GID, and disables container networking.
The released image also carries this public benchmark at `/usr/share/doc/wald/public-assessment-v0.1/`; the release evidence includes the same directory as an extractable archive.

## Fixture design

The generator creates 1,200 chronological fraud alerts with 1,200 labels from `confirmedInvestigation`:

| Period | Alerts | Composition |
| --- | ---: | --- |
| Calibration | 600 | 540 familiar legitimate alerts, 6 adverse outcomes hidden among familiar alerts, 54 visibly suspicious adverse alerts |
| Evaluation | 600 | 520 familiar legitimate alerts, 6 adverse outcomes hidden among familiar alerts, 54 visibly suspicious adverse alerts, 20 unfamiliar legitimate alerts |

The periods are separated by more than the fixture's 120-day outcome-observation lag, so the calibration period's outcomes are available before evaluation begins. The declared `asOf` is later than the final evaluation label's `observedAt`, so all 1,200 outcomes have matured for this assessment. The input also includes point-in-time customer-profile state, payment history, and synthetic feed traffic that stays inside every freshness bound read by the fraud pack. Trusted devices and monitored beneficiaries come from small, predeclared pools: membership is fixed before the timeline and is never derived from an individual outcome. Unfamiliar cases use devices absent from those pools. The pack does not read the catalog's `graphSnapshot` source, so the fixture does not invent graph state. All identifiers are synthetic tokens.

`assessment.json` defines the fixture, pins the SHA-256 of each generated file, and records the expected 0.1 result. It cannot carry a comment, so this paragraph is its file guide: the generator reads it, the runner copies it beside the JSONL inputs, and the evaluator records it as input provenance. The generated JSONL files likewise contain no comments because each line must remain a valid input record; `generate.py` is their source of truth. `verify.py` independently checks the inputs, report outputs, canonical assessment statement, result hash, and headline baseline before the runner succeeds.

## Reading the result

Start with labeled evaluation coverage, observed adverse outcomes among would-release alerts, the uncertainty around that rate, analyst time, and hold time. Read the per-band table and the stated limitations with the headline number. Do not interpret the fixture as evidence that Wald can release the same share for another institution.

The evaluator's content-hashed assessment manifest—not this fixture definition—binds the input hashes, effective pack identity, runtime version, result hashes, method, and limitations. The manifest is not internally signed. For an official release, the release workflow attaches it as a Sigstore attestation to the signed image; that external release identity is what authenticates the published result.
