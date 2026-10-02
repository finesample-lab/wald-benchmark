# What the public image supports

This page owns the public explanation of Wald 0.1's supported commands and
product boundary. It connects the tutorials to the evaluation terms; the
benchmark definitions and release workflow remain the sources for exact
inputs, image identities, and expected results.

## The supported job

Wald 0.1 evaluates a historical export and reports which alerts it would have
released, what later happened to them, and which still needed a person. The
0.1.3 release also validates a complete decision pack offline. It does not
publish or activate that pack.

The assessment produces `backtest.md`, `backtest.json`, and
`assessment-manifest.json`. The public runners use the released binary with
container networking disabled, then check the result with a separate verifier.
Supporting fact-validation commands also let the warranty runner prove the
pack's synthetic examples. The [evaluation terms](../EVALUATION-TERMS.md)
define permitted uses of the binary; the benchmark's MIT licence does not
relicense it.

## Why the first release starts offline

A historical assessment lets a team measure the opportunity in its own queue
before connecting customer feeds, identities, or a destination for live
actions. It gives the team a report to inspect without changing a live case.
That is the deliberate scope of the first public release.

The public result is a reproducibility demonstration on synthetic data. It
does not prove the live learning loop, grant permission to automate a queue,
or predict performance on another institution's history.

## Does the image contain an API?

The 0.1.3 image carries the normal Wald binary, including server commands. Its
default command is `backtest --help`; this is not a technical removal of the
API. Those server commands are outside the public 0.1 offering's supported
and licensed deployment scope.

The workbench pictures in the README show the full development runtime with
synthetic records. They are product previews, not screens produced by the
historical evaluator. The public tutorials therefore do not tell readers to
start an API service or connect live systems using this release.

Keeping source private does not prevent distributing a supported server image.
A future API offering would need its own declared setup, permitted usage, and
deployment checks. This page makes no release-date or version promise for it.

## How releases are checked

Each release binds the evaluator image to a matching version of this repository.
The release workflow checks that the image's bundled fraud benchmark matches
the tagged source, resolves the image's immutable digest, checks its signature
and benchmark revision, and runs the assessment with networking disabled.
The separate verifier checks the pinned result hash before the workflow
publishes the source, reports, image reference, and `SHA256SUMS` together.

The image carries the fraud benchmark at
`/usr/share/doc/wald/public-assessment-v0.1/`. The warranty track has its own
pack fixtures, generated history, and separately pinned result. Neither
workflow makes the synthetic data representative of a customer population.

## Find the detailed contracts

- [Fraud fixture design and interpretation](../benchmark/public-assessment-v0.1/README.md)
- [Warranty composition proof](../benchmark/warranty-claim-triage-v0.1/README.md)
- [Pack-authoring workflow](PACK-AUTHORING.md)
- [Versioned pack format](PACK-REFERENCE-v0.1.md)
- [Published images and result archives](https://github.com/finesample-lab/wald-benchmark/releases)
