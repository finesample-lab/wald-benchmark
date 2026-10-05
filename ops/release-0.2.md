# Wald 0.2 runtime preview

This document owns the build and publication contract for `v0.2.0-beta.1`.
It defines the supported local runtime and the evidence needed to release it;
the preview kit and tutorials implement this contract. The earlier
[0.1 release boundary](../docs/RELEASE-BOUNDARY.md#published-01-evaluator) remains a historical record.

**Status (2026-10-05): published beta.**
The signed image, source-free startup kit, historical results, and checksums
are available in the [public release](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.2.0-beta.1).
The supported scope remains local evaluation, not production deployment.

## The job

In the first ten minutes after pulling the image, an evaluator can send a real
API Event and Alert, review the case in the Workbench, inspect its facts and
evidence, restart Wald, and retrieve the same saved work. Synthetic starter
data makes this possible before connecting an observational customer feed.

The preview is one local tenant, structured data only, in the Development
profile. It binds to localhost and has no external write-back. Local review
and outcome records let a team evaluate the workflow without changing its
payment or case-management systems.

## What ships

- One signed `linux/amd64` image: `ghcr.io/finesample-lab/wald:v0.2.0-beta.1`.
  Its `wald` entrypoint runs the requested command; the default remains
  `backtest --help`. The kit starts `serve` explicitly.
- One source-free bootstrap kit, `wald-runtime-preview-v0.2.0-beta.1.tar.gz`,
  containing a `runtime-preview/` directory. It uses Docker with Compose and
  Python 3.10 or later, one runtime service, and a retained local volume.
- The same kit in the public `finesample-lab/wald-benchmark` repository at
  `deploy/preview`, and in the image at `/usr/share/doc/wald/runtime-preview/`.
  The release archive and its `SHA256SUMS` must be obtainable without access
  to the private product repository.
- The installable fraud pack at `/usr/share/wald/packs/fraud`. Installation
  and approval use the existing public Pack and Change APIs.
- The Workbench connected to the running API, durable Events and Alerts,
  review and evidence reads, fact computations with receipts, independent
  Outcomes, and the existing learning API/CLI paths.
- Historical backtests and offline pack validation from the same image.
- The [evaluation grant](../EVALUATION-TERMS.md) for internal local evaluation,
  including authorized customer data and observational live feeds. Product
  source remains private; hosted service provision and resale are not granted.

## First session and retention

The kit's `python3 wald-preview.py up --sample` initializes a new private
store, installs and approves the fraud pack, and sends the sample through the
public API. `credentials` prints Workbench links for the local human purposes.
Separate credentials remain available for event, alert, fact, outcome,
authoring, approval, and evidence operations.

`stop` stops the service without deleting its volume. A later `up` uses the
same store, keys, credentials, and installed pack. Repeating sample setup uses
its saved identities rather than creating a new queue. Missing credentials
or partial initialization must fail visibly, never silently replace a store.
The kit has no implicit reset.

Readiness proves that this tenant can serve requests. It does not confer
release authority. Human reviews only affect the local store because no
write-back destination is configured; Development cannot obtain an automatic
enforcement lease.

## Deliberate cuts

WorkOS or other identity-provider onboarding, hosted or multi-tenant operation,
production admission, operational write-back, automatic release, narration
model installation and qualification, and the complete Merit Loop browser
workflow are outside this preview. The backend learning and candidate paths
remain available through their documented API/CLI interfaces. No new workflow,
model vendor, benchmark leaderboard, or general candidate language is required.

The published synthetic benchmark remains historical evidence. Its 526
release candidates among 600 held-out alerts included six later adverse
outcomes: 1.1%, with a 95% Wilson interval of 0.5% to 2.5%. Its 104 review
hours are 520 later-legitimate candidates times an assumed 12 minutes, not
measured savings. Neither the benchmark nor this runtime walkthrough proves
learning quality, performance on a customer's queue, or production capacity.

## Ready means

Normal repository CI passes once for the exact candidate commit. The release
workflow retains its existing signing, SBOM, provenance, historical assessment,
and anonymous digest-pull checks. It does not repeat normal CI or introduce a
new family of release gates.

One end-to-end run of the actual candidate image and kit must prove:

1. Fresh startup without a private checkout, source build, model download,
   identity provider, or external write-back, with only localhost exposed.
2. Fraud-pack installation through the shipped path, real Event and Alert
   intake, a Workbench review, and retrievable facts and decision evidence.
3. Stop and restart with the same tenant, credentials, pack, events, alert,
   and completed review retained.
4. Working published kit instructions and a checksummed archive matching the
   image's bundled kit. Record the image digest and the run's result.

Publish only after those results exist. Update the README and the status here
with the actual public digest and release links at publication; a source
version change by itself is not a release.

## Local candidate verification

The final local `linux/amd64` image has image ID
`sha256:65e4e5a0b0d16fa785263cc6de91e0fa739e63fcea6cc0e6481ecf91a558ac48`.
This is a local test identity, not a published or signed registry digest.

- The existing workspace tests, formatting, strict Clippy, typed-client
  contract check, and optional Wasm compilation pass. No new test suite or
  CI job was introduced.
- `deploy/preview/check.py` passes against the final image: fresh startup,
  purpose-bound authentication, bundled Workbench and OpenAPI, pack discovery,
  Event and Alert intake, a finalized synthetic review, typed facts, evidence
  verification, and retention through stop/restart. Its temporary tenant is
  removed after the run.
- A browser check on the final image completes Hold, returns to the queue
  after the last case, and opens that review in Done. This caught and fixed
  the narrow-screen empty-detail navigation trap. No browser errors were
  recorded. Browser automation is not a new release gate.
- Offline verification reproduces two fact receipts, one scorecard answer,
  and one Decision without differences. The current epoch's sampling key is
  still withheld: its draw is reported as awaiting reveal, not falsely
  claimed as replayed. A Decision bundle is not a complete ledger audit.
- The image's extracted kit matches `deploy/preview` and the prepared public
  mirror byte-for-byte. The beta historical assessment retains result hash
  `sha256:c596e676c251823709a890f456b07f067631e80234b669b8776b1da23b2d9e52`.

These checks establish local functional readiness, not production capacity,
multi-day recovery, independent learning quality, or hosted readiness. The
publication checks below establish the public artifact identity; the local
test identity above is not a release digest.

## Published release

The `v0.2.0-beta.1` release uses the signed image
`ghcr.io/finesample-lab/wald@sha256:5047149a9ad0c870fa0d5c63d4d68da19afc161e3f110b7b414c19a4e6d96be7`.
Its source identities are:

- Private product commit: `910b12398e5d6356665f8ff71c9f4c5f26cb989f`.
  Product source remains private.
- Public benchmark and kit commit:
  [`abd32ff1374468835275288ab8e2dce1dfa4adc4`](https://github.com/finesample-lab/wald-benchmark/commit/abd32ff1374468835275288ab8e2dce1dfa4adc4).
  Both release tags retain these exact source identities.

Normal product CI passed in run `37351287264`. The private image release
passed in run `37353021417`, including its shipped-dependency audit,
historical assessment, source-free runtime journey, kit packaging, signing,
SBOM, and provenance. These runs are in the private product repository.

The [public evidence workflow](https://github.com/finesample-lab/wald-benchmark/actions/runs/37357435064)
pulled the image without registry credentials, verified its signature and
attestations, matched the bundled benchmark and kit to the tagged public
source, and reran the historical benchmark against that digest. It published
the kit, source and result archives, reports, `image-reference.txt`, and
`SHA256SUMS` on the [beta release](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.2.0-beta.1).
The historical result hash remains
`sha256:c596e676c251823709a890f456b07f067631e80234b669b8776b1da23b2d9e52`.

This publication did not add a new CI job or test suite. It does not establish
production capacity, shared-user admission, live learning quality, narration
qualification, or operational write-back readiness.
