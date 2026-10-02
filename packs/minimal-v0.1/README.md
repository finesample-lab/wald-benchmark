# Minimal Wald decision pack

This directory owns the smallest complete structured decision pack an author can copy. Wald uses its one event and one point-in-time fact to judge whether a synthetic review may leave a specialist queue; the files demonstrate the public v0.1 contract, not a real operating policy or production recommendation.

The example deliberately has one simple repeat-review pattern and no monetary exposure. Its settings sample every candidate, allow at most one automatic release in 24 hours, stop on any provider fault or incomplete state in the trigger window, and grant no outbound capability. Those values make the example conservative and observable; they are still demonstration values that must not be carried into another domain without evidence and review.

## Directory map

JSON cannot carry maintenance comments, so this table is the guide for every machine-readable file in the pack.

| Path | What it owns and how Wald uses it |
| --- | --- |
| `pack.json` | Public package identity, licence, and tested Wald/API compatibility. It describes the distribution; `domain.json` supplies the runtime domain identity. |
| `catalog.json` | Admits one entity and the `review.opened` event used by the fact set and fixture. |
| `facts.json` | Defines `priorReviews30d`, the count of earlier reviews available when the current review opened. |
| `domain.json` | Defines one releasing class, one repeat-review pattern, the three required question roles, point-in-time state binding, outcome words, and a one-fact starting scorecard. |
| `release-conditions.json` | Allows the domain clear condition only when the calibrated release answer meets the named threshold and no earlier review exists. Wald's other release checks still apply. |
| `settings/thresholds.json` | Supplies the named threshold and conservative evaluation/rate requirements for this synthetic example. |
| `settings/sampling.json` | Samples every candidate in this example for both release evidence and learning. |
| `settings/evidence.json` | Supplies demonstration rates and windows from which Wald derives the sequential evidence test. |
| `settings/triggers.json` | Contains the example after any provider fault or incomplete state in its recent decision window. |
| `settings/manifest.json` | Allows the governed scorecard but grants no outbox, warehouse, anchor, connector, or local-model capability. |
| `fixtures/one_prior_review.json` | Proves the current event is excluded and one earlier event inside 30 days is counted. |
| `scripts/manifest.sh` | Regenerates or verifies the sorted digest inventory of the distributed pack. |
| `MANIFEST.sha256` | Generated file inventory. Do not edit it by hand. |
| `LICENSE` | MIT grant for this starter pack. This README supplies its maintenance context because legal text is not modified with comments. |

## Validate it

Wald 0.1.2 can compile the fact and run the fixture:

```sh
wald validate facts.json --catalog catalog.json
wald test fixtures
./scripts/manifest.sh
```

The next Wald release adds the complete, offline check:

```sh
wald pack validate .
```

That command reads `./settings` automatically and makes no network call. It is not available in the public Wald 0.1.2 image.

## Adapt it

Follow the [public authoring guide](../../docs/PACK-AUTHORING.md) and [v0.1 format reference](../../docs/PACK-REFERENCE-v0.1.md). Rename the package, domain, class, event, entity, fact, questions, outcomes, and source. Replace every score point and setting with values justified for the new domain. Add a fixture for each fact and every boundary that could change the judgment.

For several fact sets, money, state, reference lists, and cross-entity history, use the [warranty claim triage pack](../warranty-claim-triage-v0.1/README.md) as the advanced example.

## Publish for evaluation

Set `FS_SERVICE_TOKEN` to an `artifactAuthor` credential, then publish the complete settings explicitly:

```sh
wald pack install . --settings settings --url https://wald.example
```

Installation publishes an immutable PackVersion and submits its Change. A different person must review and sign that exact Change. The empty outbox manifest means this starter cannot dispatch a live action even after activation.
