# Warranty claim triage for Wald

This directory owns a runnable, synthetic decision pack that shows how Wald composes the same evidence-learning loop for warranty abuse screening. Wald loads these files together as one PackVersion; the catalog and facts assemble point-in-time claim evidence, the domain interprets that evidence, and the release conditions decide whether a claim may leave enhanced abuse review for ordinary warranty adjudication.

It is deliberately **not** a warranty-coverage or auto-payment system. A released claim still goes through the operator's normal coverage, contract, exclusion, repair and payout checks. The included facts, scorecard points and settings are reproducible demonstration inputs for the public benchmark, not production recommendations or evidence of real-world accuracy.

## What the pack demonstrates

- A claim filed by one customer is also projected into the product serial's history.
- Reuse of the same serial by another customer is visible without a graph engine or application-code change.
- Product registration is a real input: it establishes the serial's first known registration time.
- A closed investigation contributes only when it explicitly records `abuse_confirmed`; an ordinary denial is not treated as abuse.
- Wald's calibration, blind sampling, evidence and lease rules still determine whether any release authority has been earned.

## Directory map

JSON cannot carry maintenance comments, so this table is the guide for each machine-readable file.

| Path | Responsibility and runtime relationship |
| --- | --- |
| `pack.json` | Public package identity, licence and Wald/API compatibility metadata. It documents the bundle but is not a runtime decision artifact. |
| `catalog.json` | Registers accepted fields, events and sources. Its `serial` projection files claims and registrations under the tokenized serial so `serialClaimActivity` can read cross-customer history. |
| `facts.json` | Defines the customer and projected-serial point-in-time facts consumed by the State contract in `domain.json`. |
| `domain.json` | Defines the abuse-screening class, outcome words, questions, State contract and draft scorecard. Its release answer means “leave enhanced abuse review,” never “pay this claim.” |
| `release-conditions.json` | Requires a calibrated no-abuse answer, no prior confirmed abuse and no reviewed-list match before the core release gates are considered. |
| `settings/*.json` | Complete executable demonstration settings for `wald pack install`. The capability manifest deliberately grants no outbound write, so an operator must publish a separately reviewed PackVersion before live action. |
| `fixtures/first_claim.json` | Proves empty history is represented explicitly and customer state remains point-in-time. |
| `fixtures/customer_history_boundaries.json` | Proves 30/90-day edges, a confirmed-abuse finding, state lookups and same-currency aggregation. |
| `fixtures/serial_cross_customer.json` | Proves a serial's projected history crosses customer boundaries, excludes the exact 365-day edge and reads registration/list evidence. |
| `MANIFEST.sha256` | Generated digest inventory for the unpacked publication. `scripts/manifest.sh` owns and verifies it. |
| `LICENSE` | MIT grant for this decision pack; the benchmark repository's root licence intentionally does not cover packs. |

## Verify locally

Wald 0.1.2 or a compatible 0.1 release is required.

```bash
wald test fixtures
./scripts/manifest.sh
```

All three fixtures should pass. Each fixture compiles and executes the relevant
fact set through both the reference evaluator and the production feature
engine. This proves the fact definitions are structurally executable; it does
not validate the draft scorecard against real warranty outcomes.

## Install for evaluation

Set `FS_SERVICE_TOKEN` to an `artifactAuthor` credential, then run:

```bash
wald pack install . --settings settings --url https://wald.example
```

The command publishes one immutable PackVersion and returns a Change for a different person to sign. The included settings make publication complete but keep outbound capabilities empty. Before any live rollout, replace the scorecard and settings with values reviewed against the operator's policy, history and independent outcomes, then enable only the intended destination in a newly approved capability manifest.

## Benchmark claim

This pack supports a narrow, checkable claim: the released Wald image can validate and execute a non-fraud domain expressed in pack files, including a cross-customer serial projection, without a Rust change. The accompanying [synthetic assessment](../../benchmark/warranty-claim-triage-v0.1/README.md) adds a deterministic history, matured outcomes and an independent verifier. Both the pack and assessment remain vendor-authored composition evidence, not production warranty evidence.
