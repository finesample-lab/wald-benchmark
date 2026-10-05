---
# Maintainer guide: This tutorial owns the source-free runtime preview's first session.
# Keep commands aligned with deploy/preview and the public release assets.
# It proves a real local API/Workbench path and restart retention, not production admission.
title: Review your first alert in Wald
audience: Evaluators and platform engineers
time: 10 minutes after prerequisites and image download
prerequisites:
  - Docker with Compose and linux/amd64 support
  - Python 3.10 or later, a web browser, and an unused localhost port 7070
  - The Wald runtime preview kit
status: Published v0.2.0-beta.1 local runtime preview
---

# Review your first alert in Wald

Start a local queue, review a case in the Workbench, inspect its evidence, and
find the same work after a restart. The starter sample uses synthetic payments
sent through the real API. You need no private source checkout, Rust build,
model download, or identity-provider account.

These instructions use the published
[`v0.2.0-beta.1` beta](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.2.0-beta.1).
The published `v0.1.3` remains a historical evaluator;
it is not a substitute for this preview.

## Get the kit and image

Download
`wald-runtime-preview-v0.2.0-beta.1.tar.gz` and `SHA256SUMS` from the public
[beta release](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.2.0-beta.1).
Check the archive against its checksum, then extract it:

```sh
tar -xzf wald-runtime-preview-v0.2.0-beta.1.tar.gz
cd runtime-preview
docker pull --platform linux/amd64 ghcr.io/finesample-lab/wald:v0.2.0-beta.1
```

The same kit is distributed at `deploy/preview` in the public
[benchmark repository](https://github.com/finesample-lab/wald-benchmark).
Run the remaining commands from the kit directory. The image download is
outside the ten-minute walkthrough; amd64 emulation can be slower on an Arm
machine. The release's signed image identity is
`ghcr.io/finesample-lab/wald@sha256:5047149a9ad0c870fa0d5c63d4d68da19afc161e3f110b7b414c19a4e6d96be7`.
Use this reference with `--image` when you need an immutable image identity.

## Start your queue

```sh
python3 wald-preview.py up --sample
```

The kit starts one runtime container, prepares a private persistent volume,
installs the image's fraud pack, and approves it with the separate local
approver credential. It then sends the sample through the public Event and
Alert APIs. Repeating this command keeps the same sample identities.

Retrieve your purpose-specific sign-in links and credentials:

```sh
python3 wald-preview.py credentials
```

Open the analyst link. It leads to the Workbench at `http://127.0.0.1:7070`.
The link contains a local credential; keep it private. Run the same command
when you need the links again.

This is one Development tenant, named `preview`. It cannot obtain permission
to release alerts automatically, and the kit configures no external write-back.
A review changes Wald's local records, not a payment or your case manager.

## Review a case and inspect its evidence

1. Open the sample alert in **Queue**, or **Audit sample** when it was drawn
   for blind review. Read the facts and their missing-data indicators. An
   event records what happened; the alert asks Wald to assess it.
2. Complete the available review. If it is a blind review, Wald withholds its
   answer until you finish. Use the case evidence to give your own verdict,
   then select **Finalize review** and confirm. Finalizing ends the Undo
   window and reveals the decision.
3. Open the case's evidence after finalization. Inspect the recorded decision,
   any limit that kept it with a person, and the facts and receipts behind it.
   Pending blind review can keep the decision hidden; that is expected.
4. Open **Facts** to see the definitions used by the pack. Missing history or
   an unconnected source is reported as an issue, not presented as a zero.

The sample command also prints its `alertId`, `receiptId`, and `evidenceUrl`.
While a blind review is open, `factsVisibility` can be `withheldUntilReview`
and the computation and receipt IDs can be null. Complete the actual review,
then rerun `python3 wald-preview.py sample` to retrieve the computation.
The Workbench uses the same API your application can call; reviews, decisions,
and evidence are stored in the tenant volume. The sample is small: it proves
this workflow, not calibrated accuracy or learning quality. The
[integration tutorial](developer-integration.md) walks through raw Event,
fact, Alert, and Outcome requests.

## Restart and keep the same work

Note the reviewed alert's ID and disposition, then run:

```sh
python3 wald-preview.py stop
python3 wald-preview.py up
```

Reopen the same Workbench link and find the same alert and review. The same
tenant, keys, credentials, installed pack, and recorded evidence remain in
the volume. `up` resumes the store; it does not initialize it again or send
sample data unless you explicitly request it.

Stop with `python3 wald-preview.py stop` when finished. Keep the volume: it
contains the store and its keys. The kit provides no implicit reset. This
exercise checks normal restart retention, not recovery after losing the disk.

## Connect your data next

The [evaluation terms](../EVALUATION-TERMS.md) permit internal local use of
authorized customer data and an observational copy of a live feed. Start with
the [API integration](developer-integration.md) walkthrough, use a separate
credential for each purpose, and tokenize declared identifiers before sending
real records. Keep this service on localhost.

Facts, independent outcomes, learning runs, and candidate operations are
available through the API and CLI. WorkOS setup, the complete Merit Loop
browser flow, narration models, hosted operation, and production qualification
are outside the [preview contract](../ops/release-0.2.md).

## If a step fails

| What you see | What to check |
| --- | --- |
| The image or kit is unavailable | Check access to GitHub and `ghcr.io`, then use the linked beta release assets and exact tag. Do not substitute the historical-only 0.1 image. |
| Docker or Compose is unavailable | Start Docker and check `docker compose version`. The kit does not install a container runtime. |
| Port 7070 is occupied | Choose another loopback port with `--port`, then use it for later kit commands and API calls. |
| A partial store or missing credentials | Keep the existing volume. Inspect the reported failure instead of reinitializing it. |
| A decision is hidden | Complete the assigned blind review and its finalization before reading the answer. |
| Facts are missing | Inspect their issue codes. The sample does not fill every feed or customer history. |
| API request fails | Retain its `Request-Id` and error code for diagnosis; omit credentials and customer data. |

The running service serves its exact API reference at
`http://127.0.0.1:7070/v1/openapi.yaml`.
