# What the public images support

This page owns the public boundary between the published historical evaluator
and the local runtime preview. It connects tutorials to their applicable
evaluation terms and release evidence. Exact fixture inputs and result hashes
remain in the benchmark definitions.

## Published runtime preview

[`v0.2.0-beta.1`](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.2.0-beta.1)
is a published beta. Its one
`linux/amd64` image and source-free kit support one local Development tenant:
the Workbench on the live API, durable Event and Alert ingestion, reviews,
evidence, fact computations, independent outcomes, pack installation, and
existing learning API/CLI paths.

The kit starts on localhost and retains the store, keys, credentials, and
active pack in one Docker volume. It has no external write-back, and
Development cannot acquire an automatic enforcement lease. Local reviews
change Wald's records, not payments or an institution's case manager.

The [evaluation terms](../EVALUATION-TERMS.md) permit internal local evaluation
with authorized customer data and an observational copy of a live feed.
Wald's product source remains private. Hosted service provision and resale,
production decisioning, and operational write-back are outside the grant.

WorkOS setup, a complete Merit Loop browser workflow, narration models,
hosted operation, and production qualification are outside the preview.
Current learning and candidate operations remain available through the API
and CLI; this does not claim improved model quality on a customer's data.
See the [0.2 build contract](../ops/release-0.2.md) and
[first-session tutorial](../tutorials/deployment.md).

The signed release image is
`ghcr.io/finesample-lab/wald@sha256:5047149a9ad0c870fa0d5c63d4d68da19afc161e3f110b7b414c19a4e6d96be7`.
The release includes `image-reference.txt`, the startup kit, historical results,
and `SHA256SUMS`. Its [publication record](../ops/release-0.2.md#published-release)
identifies the source commits and checks. A public beta is not production
qualification.

## Published 0.1 evaluator

The published `v0.1.3` evaluates a historical export and validates complete
decision packs offline. It produces `backtest.md`, `backtest.json`, and
`assessment-manifest.json`, with container networking disabled. It does not
publish or activate packs. Server commands present in that binary are outside
its supported and licensed scope; use the
[terms distributed with 0.1.3](https://github.com/finesample-lab/wald-benchmark/blob/v0.1.3/EVALUATION-TERMS.md).

The [historical tutorial](../tutorials/getting-started.md) remains pinned to
that release. The [warranty proof](../tutorials/warranty-pack.md) retains its
own 0.1.2 image. A new runtime version does not replace either published
experiment or establish better accuracy or learning.

The synthetic fraud result included six adverse outcomes among 526 release
candidates from 600 held-out alerts: 1.1%, with a 95% Wilson interval of
0.5% to 2.5%. The illustrative 104 hours use an assumed 12 minutes for each
of 520 later-legitimate candidates; they are not measured savings. This is
repeatable historical evidence, not independent validation, live-learning
proof, or a prediction for another queue.

## How releases are checked

Normal product CI runs once for the exact candidate commit. The product
release checks the actual image, signs it, and retains its SBOM, provenance,
and historical assessment. The 0.2 runtime adds one actual-image end-to-end
proof of startup, real intake, review, evidence, and restart retention.
It does not introduce a second CI suite or a browser-automation release gate.

This public repository's release workflow resolves the signed image digest,
checks that its bundled benchmark matches the tagged public source, runs the
historical assessment offline, and checks the result independently. It
publishes source, reports, image reference, and checksums. For 0.2, it also
publishes the kit extracted from that verified image as
`wald-runtime-preview-v0.2.0-beta.1.tar.gz` with `SHA256SUMS`.

The image retains `backtest --help` as its default command; the kit explicitly
starts `serve`. It includes the fraud pack at `/usr/share/wald/packs/fraud`,
the kit at `/usr/share/doc/wald/runtime-preview/`, and the historical fraud
benchmark at `/usr/share/doc/wald/public-assessment-v0.1/`.

## Detailed contracts

- [Runtime preview build contract](../ops/release-0.2.md)
- [Fraud fixture design and interpretation](../benchmark/public-assessment-v0.1/README.md)
- [Warranty composition proof](../benchmark/warranty-claim-triage-v0.1/README.md)
- [Pack-authoring workflow](PACK-AUTHORING.md)
- [Versioned pack format](PACK-REFERENCE-v0.1.md)
- [Published images and result archives](https://github.com/finesample-lab/wald-benchmark/releases)
