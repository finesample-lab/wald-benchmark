---
# Maintainer guide: This tutorial owns the application and agent integration path.
# Keep requests aligned with the public OpenAPI contract, api_facts, and api_intake.
# It uses the source-free runtime preview prepared by deployment.md.
title: Give your application facts it can explain
audience: Application and agent developers
time: 10 minutes after prerequisites
prerequisites:
  - The running runtime preview and extracted kit from deployment.md
  - A POSIX shell, curl 7.76 or later, and jq
status: v0.2.0-beta.1 candidate; not yet published
---

# Give your application facts it can explain

Send two payments and ask what was known at the second one. Your application
will receive typed facts, including the amount sent and the number of earlier
payments, with a saved receipt. Then submit an alert and follow its links to
the State and, when visible, the Decision.

This is a synthetic integration exercise. It does not require a language model
or enable automatic release.

## Before you start

Complete [Review your first alert](deployment.md), leaving its container
running. Run the commands below from the extracted `runtime-preview` kit
directory. The ten-minute clock starts with that runtime, `curl`, and `jq`
available. No source checkout or native binary is needed.

Finish the deployment sample's blind review and finalization before these
fact requests. An open blind review can withhold a computation that includes
protected narration facts, even though this tutorial sends no narration.
The event IDs below are separate from the kit sample's reserved IDs.

This tutorial targets the `v0.2.0-beta.1` candidate, which is not yet published.
The earlier public `v0.1.3` remains a historical evaluator under its original
release contract.

Prepare a private directory for the request and response files, then load
only the credentials needed for these requests:

```sh
umask 077
export WALD_DIR="$PWD/integration-results"
mkdir -p "$WALD_DIR"
export WALD_URL="http://127.0.0.1:7070"

export WALD_EVENT_TOKEN="$(python3 wald-preview.py credentials --purpose eventWriter)"
export WALD_ALERT_TOKEN="$(python3 wald-preview.py credentials --purpose alertWriter)"
export WALD_FACT_TOKEN="$(python3 wald-preview.py credentials --purpose factReader)"
export WALD_EVIDENCE_TOKEN="$(python3 wald-preview.py credentials --purpose evidenceReader)"
export WALD_OUTCOME_TOKEN="$(python3 wald-preview.py credentials --purpose outcomeWriter)"
```

These credentials have different jobs. The application sends events and
alerts. A fact-reading agent gets only the fact-reader credential. Pack
installation and approval belong to operators. The startup kit already used
its separate local author and approver credentials to install the fraud pack.

Define two small shell helpers so every request uses the same contract:

```sh
wald_get() {
  curl --fail-with-body --silent --show-error \
    -H "Authorization: Bearer $1" \
    -H "Wald-Version: 2026-09-28" \
    "$WALD_URL$2"
}

wald_post() {
  curl --fail-with-body --silent --show-error \
    -H "Authorization: Bearer $1" \
    -H "Wald-Version: 2026-09-28" \
    -H "Idempotency-Key: $3" \
    -H "Content-Type: application/json" \
    --data-binary "@$4" "$WALD_URL$2"
}
```

The credential selects the tenant. Do not add `tenantId` to these bodies.
Each POST uses a key for that logical operation. To retry it, keep both the
key and the saved request file unchanged.

## Find the installed facts

The image includes the fraud pack at `/usr/share/wald/packs/fraud`. Bootstrap
uses `wald pack install` and the public Change signature route to activate it;
you do not need to copy a pack out of the private repository. This activates
definitions, not automatic release. The example sends structured data only.

Find the pack's payer facts by their public resource ID:

```sh
wald_get "$WALD_FACT_TOKEN" "/v1/feature-sets?limit=100" \
  > "$WALD_DIR/feature-sets.json"
WALD_FACT_SET_ID="$(jq -er \
  '.data[] | select(.name == "payerActivity") | .id' \
  "$WALD_DIR/feature-sets.json")"
```

## Send two payments

Create two events for one synthetic account, one minute apart. All identifiers
below are test identifiers, not customer data. Real integrations must tokenize
declared identifiers before sending them.

```sh
WALD_TIME_1="$(jq -nr 'now - 60 | strftime("%Y-%m-%dT%H:%M:%SZ")')"
WALD_TIME_2="$(jq -nr 'now | strftime("%Y-%m-%dT%H:%M:%SZ")')"

jq -n --arg at "$WALD_TIME_1" '{
  eventId: "evt_01KABCDGH0123456789ABCDEFG",
  entityId: "tutorial-payer", entityType: "account",
  eventType: "payment.sent", occurredAt: $at, value: "100.00",
  data: {currency: "USD", beneficiaryId: "tutorial-beneficiary",
         deviceId: "tutorial-device"}
}' > "$WALD_DIR/payment-1.json"

jq -n --arg at "$WALD_TIME_2" '{
  eventId: "evt_01KABCDGH0123456789ABCDEH0",
  entityId: "tutorial-payer", entityType: "account",
  eventType: "payment.sent", occurredAt: $at, value: "50.00",
  data: {currency: "USD", beneficiaryId: "tutorial-beneficiary",
         deviceId: "tutorial-device"}
}' > "$WALD_DIR/payment-2.json"

wald_post "$WALD_EVENT_TOKEN" "/v1/events" \
  "tutorial-payment-1" "$WALD_DIR/payment-1.json" \
  > "$WALD_DIR/event-1.json"
wald_post "$WALD_EVENT_TOKEN" "/v1/events" \
  "tutorial-payment-2" "$WALD_DIR/payment-2.json" \
  > "$WALD_DIR/event-2.json"
jq '{id, object, value, sequence}' "$WALD_DIR/event-2.json"
```

Each first submission returns HTTP 201 and an `event`. Keep the returned
`id`; use it to refer to that stored event. Money travels as decimal strings,
not floating-point numbers. Event IDs use Wald's `evt_` opaque-ID format;
these valid examples are for one run in this tutorial tenant.

## Ask what was known at the second payment

```sh
WALD_EVENT_ID="$(jq -r '.id' "$WALD_DIR/event-2.json")"
jq -n --arg event "$WALD_EVENT_ID" --arg fs "$WALD_FACT_SET_ID" '{
  input: {type: "storedEvent", eventId: $event},
  featureSet: {id: $fs, version: "active"}
}' > "$WALD_DIR/facts-request.json"

wald_post "$WALD_FACT_TOKEN" "/v1/feature-computations" \
  "tutorial-payment-2-facts" "$WALD_DIR/facts-request.json" \
  > "$WALD_DIR/facts.json"
jq '{retention, featureSetVersionId, receiptId,
     facts: (.features | {sent24h, sentCount24h, aboveUsualAmount})}' \
  "$WALD_DIR/facts.json"
```

Expect a durable computation with these values:

```json
{
  "sent24h": {"type": "money", "value": {"amount": "150.00", "currency": "USD"}, "issues": []},
  "sentCount24h": {"type": "integer", "value": 1, "issues": []},
  "aboveUsualAmount": {"type": "boolean", "value": false, "issues": []}
}
```

The definitions include the current payment in the amount, exclude it from
the earlier-payment count, and compare it with prior amounts. Your application
does not need to reproduce those queries. Check each fact's `issues` before
using its value. Other facts will report missing sources or quiet feeds in
this small example; a missing fact is not zero.

Retrieve the computation's saved receipt:

```sh
WALD_RECEIPT_ID="$(jq -r '.receiptId' "$WALD_DIR/facts.json")"
wald_get "$WALD_FACT_TOKEN" "/v1/receipts/$WALD_RECEIPT_ID" \
  > "$WALD_DIR/receipt.json"
jq '{id, eventId, definitionOwner, inputView, planHash,
     outputSha256, status, signatureAlgorithm: .signature.algorithm}' \
  "$WALD_DIR/receipt.json"
```

The receipt identifies the definition, input boundary, output hash, and
signature. This step retrieves the evidence; it does not independently verify
the signature. Keep the receipt ID with the application result. For a later
computation that must use the same definition, select the returned
`featureSetVersionId` with `featureSet: {id: ..., versionId: ...}` instead of
`version: "active"`.

## Submit an alert and inspect its evidence

An event records what happened. An alert asks Wald to assess a case. Discover
the alert-writer credential's connector, then refer to the stored payment:

```sh
WALD_CONNECTOR_ID="$(wald_get "$WALD_ALERT_TOKEN" "/v1/me" | jq -r '.pins.connectorId')"
jq -n --arg connector "$WALD_CONNECTOR_ID" \
  --arg event "$WALD_EVENT_ID" --arg at "$WALD_TIME_2" '{
  connectorId: $connector, sourceAlertId: "tutorial-case-2",
  class: "fraud", entityId: "tutorial-payer", eventId: $event,
  occurredAt: $at, sourceScore: "0.20",
  exposure: {amount: "50.00", currency: "USD"}
}' > "$WALD_DIR/alert-request.json"

wald_post "$WALD_ALERT_TOKEN" "/v1/alerts" \
  "tutorial-alert-2" "$WALD_DIR/alert-request.json" \
  > "$WALD_DIR/alert.json"
WALD_ALERT_ID="$(jq -r '.id' "$WALD_DIR/alert.json")"

wald_get "$WALD_EVIDENCE_TOKEN" "/v1/alerts/$WALD_ALERT_ID?include=evidence" \
  > "$WALD_DIR/alert-evidence.json"
jq '{id, processing, decisionVisibility, decision, review,
     stateId: .evidence.state.id,
     limits: .evidence.decision.limits}' "$WALD_DIR/alert-evidence.json"
```

The first alert submission returns HTTP 201. The evidence expansion links
the source alert, its assembled State, and its Decision when visible. The
State carries the decision-time fact receipts. Do not assume it reuses the
standalone computation's receipt: it is assembled for the alert's own input
boundary and pack version.

On a fresh tenant this example can return `decisionVisibility:
"withheldUntilReview"`, `decision: null`, and a required blind review. That
is a successful request, not missing processing. The API also masks protected
parts of the State while review is open. Keep the case in review; do not
resubmit it under another ID to get a visible answer.

When visibility is `available`, inspect the Decision's disposition, reasons,
and limits. Do not treat a probability as permission to release. This
development setup cannot release alerts automatically, and the example has
no independent outcome history or connected writeback destination.

## Record an independent outcome

For this synthetic case, simulate a later observation that the payment was
legitimate. The preview's outcome-writer credential is bound to the fraud
pack's `chargeback` source; source identity comes from the credential, not
from a caller-supplied field. In a real feed, record only truth established
by that independent source.

```sh
WALD_OBSERVED_AT="$(jq -nr 'now | strftime("%Y-%m-%dT%H:%M:%SZ")')"
jq -n --arg alert "$WALD_ALERT_ID" --arg at "$WALD_OBSERVED_AT" '{
  externalId: "tutorial-outcome-2", alertId: $alert,
  value: "falsePositive", observedAt: $at
}' > "$WALD_DIR/outcome-request.json"

wald_post "$WALD_OUTCOME_TOKEN" "/v1/outcomes" \
  "tutorial-outcome-2" "$WALD_DIR/outcome-request.json" \
  > "$WALD_DIR/outcome.json"
jq '{id, alertId, value, observedAt}' "$WALD_DIR/outcome.json"
```

This stores an Outcome and its label. It does not make a model prediction
true, complete a blind review, or immediately qualify the case for learning.
Blind-review and maturity rules still apply. Reuse this saved body and key
when retrying, including the original observation time.

## Follow learning through the API

An artifact author can list scorecard runs with the same source-free setup:

```sh
WALD_AUTHOR_TOKEN="$(python3 wald-preview.py credentials --purpose artifactAuthor)"
wald_get "$WALD_AUTHOR_TOKEN" "/v1/scorecard-runs?limit=10" | jq .
```

The existing `POST /v1/scorecard-runs` route accepts `{}` and returns an
Operation to poll at `/v1/operations/{id}`. A run needs enough eligible,
independently observed outcomes; this tiny example does not establish
learning quality or promise a promotable result.

Structural Merit Loop candidates use a Pack's `/earning-candidates/input`
export and `/earning-candidates` submission routes. The image's
`wald pack propose` command can call a separately configured proposal adapter
to produce an inert draft. Current candidates move one existing band edge or
add an already-measured Boolean fact. They must pass measurement and two
human signatures before activation, and still earn fresh release evidence.
Use the running OpenAPI reference for request schemas. The complete browser
workflow is outside this preview; no external proposer is needed here.

## Carry this into your application

You now have a stored event, useful payment facts, a receipt, and an alert with
linked evidence. Keep the application path small:

- Use an event-writer credential for ingestion and a fact-reader credential
  for application or agent context. Do not give an agent installation keys.
- Preserve the exact POST body and idempotency key across retries. Use new
  identifiers only for genuinely new events and cases.
- Read typed values and their issues together. Save receipt IDs instead of
  presenting unsupported explanations as facts.
- Use `decisionVisibility`, `processing`, and `review` explicitly. An absent
  Decision is not an instruction to act.

The same fact-reader boundary is available through `wald mcp`, configured
with `FS_RUNTIME_URL` and a fact-reader `FS_RUNTIME_TOKEN`. The CLI is in the
image; an agent needs no unrestricted credential.

## If a step fails

- `401` or `403`: check the credential's purpose. Alert writers cannot request
  `include=evidence`; use the evidence-reader credential.
- Empty feature-set list: confirm the pack Change is `applied` and the
  fact-reader credential belongs to the tenant where the pack was installed.
- `409` on a retry: reuse the original request file and idempotency key. Do
  not regenerate the timestamps in an already submitted event.
- Null facts with issues: inspect the issue codes. This tutorial does not
  populate customer profiles, trusted-device lists, or every event feed.
- Connection refused: run `python3 wald-preview.py up` from the same kit with
  the same project and port.

The API returns a `Request-Id` header and structured error details. Add `-i`
to a failing curl call to inspect the headers. Keep that request ID for
diagnosis without sharing bearer tokens. The runtime's exact contract is
available at `GET /v1/openapi.yaml`.
