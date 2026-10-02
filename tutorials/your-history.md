---
# Maintainer guide: Owns the public evaluator workflow for a prepared real export.
# Keep file shapes aligned with the released fixture generator and backtest contract.
# It follows getting-started.md and must not borrow the fixture's synthetic outcomes.
title: Measure the release opportunity in your own history
audience: Fraud operations leads and the analysts preparing their export
time: About 10 minutes for a small prepared export, after setup and downloads
prerequisites:
  - The public repository and pinned image from the getting-started tutorial
  - A prepared historical fraud export that you are authorized to evaluate
  - A running Docker-compatible runtime with linux/amd64 support and a POSIX shell
  - A local directory for private reports, outside the public repository
status: Public Wald 0.1.3 evaluator, historical assessment only
---

# Measure the release opportunity in your own history

Find which alerts in your queue Wald would have marked for release, then check what happened to them later. You will get a report your operations team can compare with its existing review process. The evaluation changes nothing live.

Complete [the fixed-example tutorial](getting-started.md) first. This walkthrough starts after your data owner has prepared an export, which may take longer than the assessment itself. Allow more than 10 minutes for large histories or emulated execution. Read the [evaluation terms](../EVALUATION-TERMS.md): the free release covers authorized historical data and internal assessment, not running a live queue or offering a service.

## Prepare the history, not today's view of it

Keep the export outside this public checkout. Use the record shapes in the [fixture generator](../benchmark/public-assessment-v0.1/generate.py), mapping your source records to the embedded fraud pack's declared event types and fields. Preserve their actual values and meaning; arbitrary event names are not accepted. Each `.jsonl` file contains one JSON object per line. Copy the format, not the generated records.

| File | What to supply |
| --- | --- |
| `events.jsonl` | Event history with `eventId`, `eventType`, `entityType`, `entityId`, `occurredAt`, and the event's `data`. Supply `value` where the event carries an amount. Include the history the fraud facts need, not only the alert-triggering events. |
| `alerts.jsonl` | Unique alerts with `sourceSystem`, `alertId`, `entityId`, `alertClass`, and `raisedAt`. Preserve `sourceDisposition`, the link in `eventId`, and the source's actual fields such as `triggeringRules`, `sourceScore`, `reportedPattern`, and `exposure` when available. Put the rows in chronological order. |
| `labels.jsonl` | Outcomes with `alertKey`, `outcome`, `source`, and `observedAt`. The key is the alert's `sourceSystem` and `alertId` joined by a colon. Supply one outcome per alert key; add nonnegative `heldMinutes` only when measured. |
| `assessment.json` | A JSON object with `asOf` set to the actual assessment cutoff as a timestamp. It must not precede the latest alert. Do not copy the synthetic fixture's date, hashes, or expected counts. |
| `state.jsonl`, when needed | Historical customer-profile revisions with `stateRevisionId`, `source`, `entityId`, `effectiveAt`, and `data`. Preserve what the profile said at the time. |
| `references.jsonl`, when needed | The reference sets the facts read, with `setId` and `keys`. Use membership known before the assessed history; this file is not a timeline of later list changes. |

This command uses the image's embedded fraud pack. The public fixture uses `fraud` alerts, `falsePositive` and `fraud` outcomes, and the independent source `confirmedInvestigation`. Map a real investigation to that vocabulary only when it means the same thing. A queue closure on its own is not an independently confirmed legitimate outcome. Do not rename a source or outcome just to make an input pass.

Keep amounts and source scores as decimal text, as the generator does, and include the timezone in timestamps. Preserve a source disposition of `hardDecline` or `critical`; omitting `sourceDisposition` defaults it to `review`.

Use actual observation times, not the alert time copied into every label. Do not replace missing historical values with what you know today, treat unlabeled alerts as legitimate, or manufacture feed activity to make facts look current. If you cannot reconstruct a profile or a changing reference list, record the limitation and inspect its effect on the result.

The evaluator splits the chronological alerts near the midpoint, using the earlier group for calibration and the later group for evaluation. It keeps equal timestamps on one side of the split. Only calibration outcomes already observed by the evaluation boundary can help calibration. Evaluation labels count only when observed by your `asOf` cutoff. Both periods need suitable history; a file of recent alerts whose outcomes have not matured is not enough.

The synthetic generator's `splitAt` records its known split; it is not a setting for choosing a different split in your export. Keep the initial assessment free of threshold overrides or recorded model answers unless you intend to evaluate those inputs too.

## Select the export and pinned image

Open a terminal in your `wald-benchmark` checkout. Load the image reference saved by the first tutorial, then enter the absolute path to your prepared export when prompted:

```sh
wald_image=$(cat image-reference.txt)
printf 'Absolute path to the prepared export directory: '
IFS= read -r wald_export
```

Check that the directory and required files exist before continuing:

```sh
test -d "$wald_export" &&
test -f "$wald_export/events.jsonl" &&
test -f "$wald_export/alerts.jsonl" &&
test -f "$wald_export/labels.jsonl" &&
test -f "$wald_export/assessment.json" &&
printf 'Required input files found.\n'
```

Continue only after `Required input files found.` appears. This check does not validate the contents; the evaluator does that when it reads them.

Create a private report parent alongside the export, outside the repository:

```sh
wald_export=$(CDPATH= cd -- "$wald_export" && pwd)
wald_results="$(dirname -- "$wald_export")/wald-results"
umask 077
mkdir -p "$wald_results"
```

Choose a location your organization permits for these records. Reports and input identities can be sensitive too. Do not commit the export or its results, attach them to a public issue, or copy them into the synthetic fixture directory.

## Run the assessment offline

The `own-history` child below must not already exist. Keep an earlier result and choose a different child name for a repeat run.

```sh
docker run --rm \
  --network none \
  --user "$(id -u):$(id -g)" \
  -v "$wald_export:/input:ro" \
  -v "$wald_results:/results" \
  "$wald_image" \
  backtest /input --out /results/own-history
```

Your export is mounted read-only. The evaluator has no container network access, and the container exits after writing the report. The container runtime and its host still have access to the mounted files; use an environment approved for your data.

A successful run creates `backtest.md`, `backtest.json`, and `assessment-manifest.json` under `$wald_results/own-history`. Your counts will differ from the public fixture. Do not run the fixture's expected-result verifier against your history.

Read the report:

```sh
less "$wald_results/own-history/backtest.md"
```

Press `q` to close the viewer. Keep the report directory and the exact image reference with your assessment notes. An optional `domain-fitted.json` is a draft for review; it did not alter the decisions measured in this run.

## Review the result with operations

Start with the number of evaluation alerts and the share with mature labels. Then read the release-candidate count, their observed adverse outcomes, and the uncertainty interval beside that rate. Missing labels are a limit on the conclusion, not evidence that a release would have been harmless.

Read the per-band results and the reasons alerts stayed with a person. Check rejected-event counts and label timing in `backtest.json` before interpreting a low release count as a product limitation. Missing or late history can prevent the facts from describing the alert.

The default review-time calculation assumes 12 minutes per review. Treat it as arithmetic unless you have measured your own review time; the `backtest` command's `--minutes-per-review` option accepts your chosen whole-minute assumption for another run. Hold times come from your supplied `heldMinutes`, and missing hold times do not mean customers waited zero minutes.

Historical labels also reflect which cases your existing process investigated. This assessment does not prove live release performance or test blind sampling and learning after deployment. Use it to decide which slice of your queue deserves a closer investigation, with the data gaps written beside the opportunity.

## If the run cannot produce a useful result

| What you see | What to check |
| --- | --- |
| A duplicate or unknown alert key | Match every label to exactly one `sourceSystem:alertId`, then resolve duplicate records at the source. |
| An outcome or source is not declared by the pack | Review its meaning with the export owner. Do not relabel evidence to bypass the error. A different decision may need a different pack. |
| No evaluation labels observed by `asOf` | Check the actual outcome observation times and cutoff. Wait for outcomes or choose an older assessment population; do not invent earlier dates. |
| The output directory already exists | Keep it and change `/results/own-history` to a new child, such as `/results/own-history-2`. |
| Few or no release candidates | Inspect mature label coverage, historical state, missing facts, and the report's limits before changing thresholds. |

If the question is not fraud-alert release, start with the [pack authoring guide](../docs/PACK-AUTHORING.md) and [warranty example](../benchmark/warranty-claim-triage-v0.1/README.md). Changing the decision requires its own facts and outcome vocabulary; a renamed fraud export is not enough.
