# Wald Public Benchmark 0.1

This directory owns the reproducible public historical benchmark bundled with Wald. It generates synthetic alerts and independently observed outcomes, checks their hashes, and sends them through the same `wald backtest` path used for an institution's export; it never changes a live queue or replaces evaluation on an institution's own outcomes. The runtime preview also includes the Workbench and live API, but this benchmark continues to measure only historical evaluation.

## What it answers

The assessment asks one deliberately narrow question:

> On this fixed history, which alerts would Wald have sent back to the existing review process, which would it have identified as release opportunities, and what later outcomes were observed?

It is useful for inspecting Wald's result shape, replaying the same inputs, and
checking that a release image produces the declared assessment. It tests the
historical evaluator and its release-opportunity scorecard, not the live CRI
loop or whether blind outcome sampling has earned authority in a deployment.
It is not customer evidence, independent validation, a safety certification,
a live drift exercise, or competitive proof. fineSample wrote the fixture,
evaluator, and separate verifier. That separation catches reproducibility and
contract failures, but a public fixture can be recognized and optimized for;
it cannot establish what will happen on a new institution's alerts.

## Run it

The supported public path uses the released image:

```sh
benchmark/public-assessment-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald:v0.1.3 \
  --baseline 0.1.3 \
  --out /tmp/wald-assessment-0.1
```

The **0.2.0-beta.1 runtime preview** retains this same historical benchmark.
Before its image is published, maintainers can exercise its definition from
an explicit local build. This does not supersede the published 0.1.3 evidence:

```sh
WALD_BIN=/absolute/path/to/wald \
  benchmark/public-assessment-v0.1/run.sh \
  --baseline 0.2.0-beta.1 \
  --out /tmp/wald-assessment-0.2.0-beta.1
```

Image runs default to baseline `0.1.3`; local `WALD_BIN` runs default to `0.2.0-beta.1`.
Use `--baseline` when testing a different pairing, including an older local
binary. A mismatched evaluator version or full result hash fails verification;
the runner never substitutes a matching baseline after a failure. Release runs
select their tag's baseline explicitly. The public runner needs no knowledge of
Wald's private source tree.

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

The JSON definitions cannot carry comments, so this paragraph is their file
guide: `assessment.json` owns the expected **0.2.0-beta.1 runtime preview**;
`assessment-0.1.3.json` preserves the published 0.1.3 definition byte for byte.
Each pins the generated input hashes, evaluator version, pack hash, full result
hash and headline counts. The generator reads the selected definition, copies
it beside the JSONL inputs under `assessment.json`, and the evaluator records
those exact bytes as provenance. The fixture data itself is unchanged between
these baselines. The generated JSONL files likewise contain no comments because
each line must remain a valid input record; `generate.py` is their source of
truth. `verify.py` independently checks the inputs, report outputs, canonical
assessment statement, full result hash and headline baseline before success.
An unchanged headline does not allow a changed report to pass an older baseline.
The runtime preview uses the corrected versioned band identities introduced
after 0.1.3 while retaining the same fixture counts and fitted starting points;
its result hash is not a claim of better predictive performance. Publication,
image signing and release attestations remain separate from local verification.

## Reading the result

Start with labeled evaluation coverage, observed adverse outcomes among
would-release alerts, the uncertainty around that rate, review-time arithmetic,
and hold time. In this fixture, 6 of 526 labeled release candidates had a later
adverse outcome: 1.1%, with a two-sided 95% Wilson interval of 0.5% to 2.5%.
That interval is a binomial-model calculation over a fixed, deliberately
composed fixture; it does not make the fixture representative of another
queue. The reported 104 analyst hours are 520 later-legitimate release
candidates multiplied by the declared assumption of 12 minutes per review;
they are not observed savings. Read the per-band table and the stated
limitations with the headline number. Do not interpret the fixture as evidence
that Wald can release the same share for another institution. The useful next
test is the same evaluator on the institution's own history and independently
observed outcomes.

The evaluator's content-hashed assessment manifest—not this fixture definition—binds the input hashes, effective pack identity, runtime version, result hashes, method, and limitations. The manifest is not internally signed. For an official release, the release workflow attaches it as a Sigstore attestation to the signed image; that external release identity is what authenticates the published result.
