---
name: author-a-wald-pack
description: Create or revise a Wald v0.1 facts or decision pack from a domain expert's requirements, validate its complete public bundle, and prepare fixtures or a historical backtest. Use when bringing a domain to Wald or changing pack facts, catalog fields, decision roles, outcomes, release conditions, or settings.
---

# Author a Wald pack

This skill owns the path from a domain expert's intent to a reviewable Wald pack. It produces pack files and local evidence; Wald's public authoring guide and versioned reference remain the authority for accepted structure and semantics.

## Start with the contract

1. Read the [pack authoring guide](../../docs/PACK-AUTHORING.md).
2. Read the sections needed for the change in the [v0.1 pack reference](../../docs/PACK-REFERENCE-v0.1.md). Do not infer fields or behavior that the reference does not define.
3. Choose the closest honest starting point:
   - use [`packs/minimal-v0.1/`](../../packs/minimal-v0.1/) for a small new pack;
   - study [`packs/warranty-claim-triage-v0.1/`](../../packs/warranty-claim-triage-v0.1/) when the pack needs a complete decision profile, settings, cross-entity history, and conformance fixtures;
   - revise the tenant's existing pack when extending an installed domain, so its catalog and identifiers remain compatible.

Treat examples as demonstrations, not schemas. Do not copy domain words, outcome meanings, thresholds, or release semantics merely because they already exist.

## Author from domain meaning

Establish the domain contract in plain language before editing JSON. Resolve the entity and events, the point-in-time facts experts use, the meaning of release, the independently observed outcomes, and which feeds are actually available. For decision packs, separate release from the later business action: leaving enhanced review need not mean approval, payment, or account access.

Use the expert's terms in labels and README prose. Make missing or stale evidence explicit rather than translating absence into a reassuring value. Use invented opaque identifiers in fixtures and never put customer data or direct identifiers in the repository.

Keep each change coherent across the catalog, facts, domain, release conditions, settings, fixtures, manifest, and pack README. If a new format cannot carry a guide comment, explain the file and its relationship to the pack in that README.

## Prove the bundle

Prefer the complete offline check when the installed Wald CLI exposes it:

```sh
wald pack validate <pack-directory>
```

If that subcommand is unavailable, use the compatibility sequence in the authoring guide for that released CLI. Do not claim complete validation from a feature-set-only check.

Run conformance fixtures whenever the pack includes or changes facts:

```sh
wald test <pack-directory>/fixtures
```

For a decision pack, run a historical backtest when a suitable export was supplied and the user authorized its use:

```sh
wald backtest <export-directory> --pack <pack-directory> --out <report-directory>
```

Treat a backtest as historical evidence, not live authority or proof of future performance. Show the exact commands and results, fix validation failures at their source, and report any check that could not be run.

## Preserve the approval boundary

Authoring and local validation do not authorize publication or tenant changes. Do not install a pack, submit an activation change, push commits, create a release, or otherwise publish unless the user explicitly requests that action. Never approve or sign a change authored in the same workflow; approval belongs to another accountable person.

Hand back the pack's intended decision, material assumptions, changed files, validation evidence, and remaining uncertainties. Keep the response clear about what the evidence proves and what it does not.
