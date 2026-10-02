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
[See another decision](#one-wald-image-another-decision) ·
[Author a pack](docs/PACK-AUTHORING.md) ·
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

## One Wald image, another decision

Fraud is Wald's first public application, not a boundary in the product. The
[warranty claim triage pack](packs/warranty-claim-triage-v0.1/README.md) gives
the same released Wald image a different history, vocabulary and question—no
new product source required.

For each claim, the pack composes the customer history, product registration,
prior investigations and cross-customer serial history that existed when the
claim arrived. It then asks one useful question: **can this claim leave
enhanced abuse review and enter ordinary warranty adjudication?** It never
answers whether a warranty is valid or a claim should be paid.

[Run the warranty composition benchmark](benchmark/warranty-claim-triage-v0.1/README.md)
to inspect the pack, its three conformance cases, a deterministic 400-claim
history and the separate result verifier. This track proves composition and
reproducibility. Because fineSample authored the synthetic data and pack, it is
not production warranty evidence or an accuracy comparison.

## Bring your own decision

Wald's domain boundary is a pack, not a product fork. A pack names the events
and point-in-time facts Wald can use, the judgment it makes, the later outcomes
that test it, and the exact boundary an alert may cross. The runtime keeps the
same evidence, sampling, replay and authority machinery underneath it.

The public authoring kit now includes:

- a [step-by-step authoring guide](docs/PACK-AUTHORING.md);
- the [versioned v0.1 format reference](docs/PACK-REFERENCE-v0.1.md);
- a [minimal complete starter](packs/minimal-v0.1/README.md) with one event,
  one fact and no outbound capability;
- the [warranty pack](packs/warranty-claim-triage-v0.1/README.md) as the
  advanced, cross-entity example; and
- an [authoring skill](skills/author-a-wald-pack/SKILL.md) that helps a coding
  agent interview the domain expert and work from those same public contracts.

Start with the decision boundary in plain words, copy the smallest honest
example, and prove the facts with synthetic fixtures before tuning a score or
threshold. The kit documents accepted inputs and released commands; Wald's
product source remains outside this repository.

## Run it

You need Python 3 and a Docker-compatible OCI container runtime.

```sh
git clone https://github.com/finesample-lab/wald-benchmark.git
cd wald-benchmark
benchmark/public-assessment-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald:v0.1.3 \
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
  ghcr.io/finesample-lab/wald:v0.1.3 \
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

- `benchmark/public-assessment-v0.1/` holds the first alert-history assessment;
- `docs/` holds the human authoring workflow and versioned pack contract;
- `packs/minimal-v0.1/` is the smallest complete decision-pack starter;
- `packs/warranty-claim-triage-v0.1/` holds the executable, MIT-licensed
  warranty composition pack;
- `benchmark/warranty-claim-triage-v0.1/` holds its synthetic history, runner
  and independent verifier;
- `skills/author-a-wald-pack/` holds the agent workflow that follows the same
  public guide and reference; and
- `.github/workflows/release.yml` binds each public release to an exact image
  digest and publishes durable evidence, while `verify-warranty.yml` checks
  the mounted warranty pack against that immutable image.

## Licence

The benchmark source and synthetic fixture definition are available under the
[MIT License](LICENSE). The [minimal starter](packs/minimal-v0.1/LICENSE) and
[warranty decision pack](packs/warranty-claim-triage-v0.1/LICENSE) each carry
their own MIT grant. These licences do not apply to Wald's image, binary,
unpublished decision packs, or fineSample trademarks. The evaluator is
distributed under [Wald's evaluation terms](EVALUATION-TERMS.md).

`LICENSE` is standard legal text and intentionally has no maintenance header.
Generated JSONL inputs and reports are untracked; the versioned generator and
release workflow are their sources of truth.
