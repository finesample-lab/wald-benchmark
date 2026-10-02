# Warranty claim triage composition benchmark

This directory owns a deterministic, synthetic history for the adjacent public warranty decision pack. The runner sends that history and the pack through Wald's existing historical evaluator, while the stdlib-only verifier checks both boundaries independently; no file in this directory participates in a live decision or grants release authority.

## What it answers

This track asks whether the released Wald image can load, execute and report on a separately published, non-fraud decision pack without changing Wald's Rust source. It exercises customer history, cross-customer serial projection, point-in-time profile state, a reviewed serial list, the pack's own outcome vocabulary, and the same chronological calibration/evaluation split as the main public benchmark.

That is a composition and reproducibility claim, not an accuracy claim. fineSample authored the decision pack, synthetic history, evaluator and separate verifier. The verifier can catch changed bytes, result drift and contract mistakes, but it is not independent validation. The synthetic outcome mix is deliberately composed and is not evidence of prevalence, discrimination, operational savings, warranty validity, claim payability, production readiness or performance on another institution's data. The historical evaluator does not exercise blind sampling, grant live release authority or change a live queue.

## Run it offline

First make the released image available locally and identify it by immutable digest. The runner checks that Docker already has the supplied image and uses `--pull never`; it does not fetch an image.

```sh
benchmark/warranty-claim-triage-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald@sha256:RELEASE_DIGEST \
  --out /tmp/wald-warranty-claim-triage-0.1
```

`--image` is the already-present Wald image reference. `--out` is a new result directory; the runner refuses to overwrite any existing path. The runner first executes all three pack conformance fixtures, including the customer-history boundaries and cross-customer serial projection, with that same image. It then runs the backtest. Each container receives only the inputs it needs as read-only mounts, the backtest receives only the output directory's existing parent as writable, both run as the host user and group, and both have networking disabled.

Maintainers can test an explicit local binary through the same generator and verifier:

```sh
WALD_BIN=/absolute/path/to/wald \
  benchmark/warranty-claim-triage-v0.1/run.sh \
  --out /tmp/wald-warranty-claim-triage-0.1
```

## Fixture design

The generator creates 400 chronological warranty-abuse alerts, each with a label from the pack's declared `claimInvestigation` source. Outcomes appear 120 days after their alerts. The 200-alert calibration period ends more than 120 days before the 200-alert evaluation period begins, and `assessment.json/asOf` is later than the final evaluation outcome.

| Period | Alerts | Deliberate composition |
| --- | ---: | --- |
| Calibration | 200 | 164 familiar later-benign claims, 3 adverse outcomes hidden in that familiar population, 33 claims with explicit abuse indicators |
| Evaluation | 200 | 150 familiar later-benign claims, 3 adverse outcomes hidden in that familiar population, 37 claims with explicit abuse indicators, 10 later-benign claims in a deliberately unfamiliar tenure band |

Every claim, customer, serial and reference key is synthetic. Reviewed-list membership is fixed by scenario before replay and is not inferred from the generated outcome. Feed sentinels keep the pack's declared inputs within their freshness bounds. The generator supplies one prior customer claim so every scorecard fact needed for a release decision is point-in-time complete; an obvious-adverse scenario separately adds a cross-customer claim on the current serial and a confirmed-abuse finding.

The published pack's evaluation settings require 500 calibration samples. This compact synthetic track deliberately overrides only `minCalibrationSamples`, lowering it to 150 in the generated `thresholds.json`; the override exists solely to keep this composition/reproducibility fixture small. It is not a recommended production setting, and the pack's published settings remain unchanged.

The resulting release fraction and adverse fraction are properties of this authored fixture. They must not be described as warranty accuracy or expected production performance. Any review-time number in Wald's report is arithmetic over release candidates later labeled `no_abuse_found`, using the explicit `--minutes-per-review 12` assumption; it is not an observed saving.

## File guide

`assessment.json` cannot contain comments, so this paragraph is its maintenance guide. It defines the seed, authored composition, maturity boundary, exact fixture hashes, exact public-pack hashes, and the result pinned for Wald 0.1.2. The evaluator copies it into the input manifest as provenance. `generate.py` is the source of truth for the JSONL history and local threshold override. `run.sh` owns the offline mount and invocation boundary. `verify.py` intentionally imports neither generator nor product code; it independently checks ordinary hashes, the pack digest inventory, the canonical runtime pack, the report, Wilson interval, illustrative arithmetic and non-live scope.

## Licensing boundary

The benchmark scripts and definition in this directory are covered by the benchmark repository's root MIT licence. The decision pack has its own [MIT licence](../../packs/warranty-claim-triage-v0.1/LICENSE). Wald's evaluator and released image remain governed by the repository's `EVALUATION-TERMS.md`; publishing this benchmark does not relicense them.
