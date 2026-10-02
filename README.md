<!--
This README is the public front door for Wald's reproducible benchmark.
It leads readers from the declared result to an offline run, while the fixture
README and release workflow hold the detailed design and publication contract.
-->

# See Wald run on a history you can inspect

Most alerts end in release. Wald measures which customers could have stopped
waiting, what happened to those alerts later, and which cases still needed a
person.

This is the public benchmark for Wald 0.1: one generated alert history, one
published evaluator, one expected answer, and a separate check of every output.

**Free to run. No account. No live changes. No network access during the
assessment.**

[Try Wald on your history](#try-wald-on-your-history) ·
[Run the public fixture](#run-it) ·
[Read the fixture design](benchmark/public-assessment-v0.1/README.md) ·
[Download a release](https://github.com/finesample-lab/wald-benchmark/releases)

## The expected result

The fixed evaluation period contains 600 synthetic fraud alerts with mature,
independently observed outcomes.

| On the public fixture | Wald 0.1 |
| --- | ---: |
| Alerts evaluated | 600 |
| Customers Wald would mark for release | 526 |
| Later adverse outcomes among them | 6 of 526: 1.1% (95% Wilson interval: 0.5–2.5%) |
| Illustrative review time on later-legitimate release candidates | 104 hours (520 × an assumed 12 minutes) |
| Alerts kept with a person | 74 |

The headline counts and review-time total are declared in
[`assessment.json`](benchmark/public-assessment-v0.1/assessment.json). The rate
and interval are derived from those counts, and a verifier separate from the
evaluator checks the released report.

The 104 hours are arithmetic under the stated review-time assumption, not an
observed saving. The Wilson interval is a binomial-model calculation over this
fixed, deliberately composed fixture; it does not make the fixture
representative of another queue.

**What this does not tell us.** The history is synthetic and deliberately
contains familiar, adverse, and unfamiliar cases. This benchmark tests the
historical evaluator, its release-opportunity scorecard, and the reproducible
release conditions around it. It does not exercise Wald's live CRI loop or
show that blind outcome sampling has earned authority in a deployment. It does
not predict what Wald will find in another institution's queue, rank Wald
against another product, or certify a live deployment.

fineSample wrote the fixture, evaluator, and verifier. Keeping the verifier
separate catches reproducibility and contract failures, but it is not
independent validation. **Running the same evaluator on your own history and
independently observed outcomes is the benchmark that matters.**

## Run it

You need Python 3 and a Docker-compatible OCI container runtime.

```sh
git clone https://github.com/finesample-lab/wald-benchmark.git
cd wald-benchmark
benchmark/public-assessment-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald:v0.1.2 \
  --out /tmp/wald-assessment-0.1
```

The runner generates the fixture, checks every input hash, runs Wald with
networking disabled, and verifies the reports against the expected result. It
refuses to replace an existing output directory.

For the immutable release image, download `image-reference.txt` from the
matching [release](https://github.com/finesample-lab/wald-benchmark/releases)
and run:

```sh
benchmark/public-assessment-v0.1/run.sh \
  --image "$(cat image-reference.txt)" \
  --out /tmp/wald-assessment-0.1-by-digest
```

## What you get

- `backtest.md` — the result in the language of customers, outcomes,
  assumption-derived review time, and hold time;
- `backtest.json` — the complete result, including label coverage,
  uncertainty calculations, calibration, bands, and limits; and
- `assessment-manifest.json` — the exact identities of the inputs, pack,
  method, evaluator, and output files.

Two runs against the same image and inputs produce the same assessment result.

## Try Wald on your history

The public fixture shows the shape of the answer. To measure your own queue,
prepare one directory with:

- `events.jsonl`, the history available at each alert time;
- `alerts.jsonl`, the alerts in chronological order; and
- `labels.jsonl`, outcomes from an independent source.

Then run the same image locally:

```sh
mkdir -p wald-results
docker run --rm \
  --network none \
  --user "$(id -u):$(id -g)" \
  -v "$PWD/export:/input:ro" \
  -v "$PWD/wald-results:/results" \
  ghcr.io/finesample-lab/wald:v0.1.2 \
  backtest /input --out /results/assessment
```

The evaluator changes nothing live and needs no service or account. Optional
inputs add point-in-time state, references, recorded model answers, reviewed
thresholds, or another complete decision pack. Read the
[fixture guide](benchmark/public-assessment-v0.1/README.md) and
[evaluation terms](EVALUATION-TERMS.md) before using a result commercially.

## How a release is checked

Each Wald release is bound to the matching version of this repository. The
release jobs:

1. compare the benchmark bundled in the image with this tagged source;
2. pull the image without credentials and resolve its immutable digest;
3. verify the image signature and embedded benchmark revision;
4. run the assessment twice with networking disabled; and
5. publish the source, reports, image reference, and `SHA256SUMS` together.

The image carries the same benchmark at
`/usr/share/doc/wald/public-assessment-v0.1/`. The complete fixture composition,
time split, outcome lag, and interpretation guide are in the
[fixture README](benchmark/public-assessment-v0.1/README.md).

## Repository map

This repository owns the public benchmark, not Wald's product source. The
boundary is intentionally small:

- `assessment.json` declares the fixed fixture and expected result;
- `generate.py` produces and hash-checks the synthetic inputs;
- `run.sh` runs a selected Wald image without network access;
- `verify.py` checks the reports without sharing evaluator code; and
- `.github/workflows/release.yml` binds each public release to an exact image
  digest and publishes durable evidence.

## Licence

The benchmark source and synthetic fixture definition are available under the
[MIT License](LICENSE). That licence does not apply to Wald, its image, its
binary, its decision packs, or fineSample trademarks. The evaluator is
distributed under [Wald's evaluation terms](EVALUATION-TERMS.md).

`LICENSE` is standard legal text and intentionally has no maintenance header.
Generated JSONL inputs and reports are untracked; the versioned generator and
release workflow are their sources of truth.
