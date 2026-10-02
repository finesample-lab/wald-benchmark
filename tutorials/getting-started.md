---
# Maintainer guide: Owns the first assessment using the public Wald 0.1 evaluator.
# Keep commands and results tied to the v0.1.3 release and unchanged fixture files.
# The separate your-history tutorial covers institution exports, not this baseline.
title: Find the release opportunity in an alert history
audience: Fraud operations leads and business evaluators
time: About 10 minutes after prerequisites and downloads
prerequisites:
  - Git, curl, Python 3, and a POSIX shell
  - A running Docker-compatible container runtime with linux/amd64 support
  - Network access to download the public benchmark and evaluator image
status: Public evaluator tutorial, pinned to Wald 0.1.3
---

# Find the release opportunity in an alert history

Find which alerts Wald would have released, how many later had an adverse outcome, and which still needed a person. Start with a published synthetic history, then [measure your own history](your-history.md).

You will produce a readable report in about 10 minutes after setup and downloads. This is a historical assessment. It changes no live queue, starts no server, and requires no account or model download. Wald's product source stays private; the benchmark source is public.

## Get the fixed example

Use a terminal with Git, curl, Python 3, and a running Docker-compatible container runtime. The image needs linux/amd64 execution support. Allow extra time for downloads or emulated execution. Read the [evaluation terms](../EVALUATION-TERMS.md) before using the evaluator.

Clone the public repository's default branch into a new directory, read the release's immutable image reference, and download that image:

```sh
git clone --depth 1 https://github.com/finesample-lab/wald-benchmark.git
cd wald-benchmark
curl --fail --location \
  --output image-reference.txt \
  https://github.com/finesample-lab/wald-benchmark/releases/download/v0.1.3/image-reference.txt
wald_image=$(cat image-reference.txt)
docker pull "$wald_image"
```

The default branch contains these tutorials. The versioned fixture in `benchmark/public-assessment-v0.1/` remains the unchanged 0.1.3 baseline: its generator checks each input against the hashes in [`assessment.json`](../benchmark/public-assessment-v0.1/assessment.json). The evaluator image stays pinned to 0.1.3 even as the documentation grows.

The image reference starts with `ghcr.io/finesample-lab/wald@sha256:`. It identifies the exact published image, rather than a tag that could move. The [0.1.3 release](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.1.3) also carries the published reports and checksums if you want to read the result before running it. Keep `image-reference.txt` for your next assessment; do not commit local run files to this public repository.

## Run the assessment

From the `wald-benchmark` directory, run:

```sh
benchmark/public-assessment-v0.1/run.sh \
  --image "$wald_image" \
  --out "$PWD/wald-results/public-assessment"
```

The runner generates the history, checks its input hashes, runs the evaluator with container networking disabled, and verifies the result. Only the generated inputs and the result parent directory are mounted into the container. Leave `public-assessment` absent before the run; the runner creates it and refuses to replace an earlier result.

A successful run ends with these lines. The report path will contain your checkout's absolute location:

```text
Verified Wald Public Benchmark 0.1: sha256:231e1217b5a57240294c61f9d30d768b8a20dad3cc26e8a3a24ac73c0245789c
Assessment report: /your/path/wald-benchmark/wald-results/public-assessment
```

Open `wald-results/public-assessment/backtest.md` in a Markdown viewer, or read it in the terminal:

```sh
less wald-results/public-assessment/backtest.md
```

Press `q` to leave the terminal viewer. The same directory contains `backtest.json` for detailed analysis and `assessment-manifest.json` for the exact inputs, evaluator, and output identities. If `domain-fitted.json` is present, it is an optional draft; it did not change the decisions measured in this report.

## Read the answer before the headline

The fixture has 1,200 alerts. The earlier 600 provide calibration history; the report evaluates the later 600, starting at `2024-07-01T00:30:00Z`. Its assessment date is `2024-12-19T00:00:00Z`, by which all of its outcomes have matured.

| Read this | Expected result | What it means |
| --- | --- | --- |
| Alerts evaluated | 600 | The held-out period, not all 1,200 alerts |
| Would release | 526 | Historical release candidates, not live releases |
| Labeled release candidates | 526 of 526 | All release candidates have a mature outcome in this fixture |
| Later adverse outcomes | 6 of 526, or 1.1% | Read with the two-sided 95% Wilson interval: 0.5% to 2.5% |
| Kept with a person | 74 | Cases that did not meet the release conditions |
| Illustrative review time | 104 hours | 520 later-legitimate release candidates multiplied by an assumed 12 minutes per review |

Source: fineSample's [fixed fixture definition](../benchmark/public-assessment-v0.1/assessment.json) and [published report](https://github.com/finesample-lab/wald-benchmark/releases/download/v0.1.3/backtest.md). The fixture represents no institution. The counts describe its evaluation period only.

Read the per-band results and the limits that held alerts back. A large release count is not useful without its label coverage and later adverse outcomes. Limits can overlap, so their counts need not add up to the 74 alerts kept with a person.

## What we don't know yet

fineSample wrote the synthetic history, evaluator, and separate verifier. The run demonstrates a reproducible historical result, not independent validation or likely performance on your queue. The uncertainty interval is a binomial-model calculation over this deliberately constructed fixture; it does not make the fixture representative.

The 104 hours are arithmetic, not measured analyst savings. Hold times in this example are synthetic too, not a demonstrated reduction in customer waiting. The public assessment does not exercise live release, blind sampling, or the CRI learning loop. A historical result is a reason to investigate your queue, not a reason to switch on automatic release.

## Recover from a stopped run

| What you see | What to do |
| --- | --- |
| Cannot connect to the Docker daemon | Start your container runtime, then repeat the command. |
| Image cannot run on this machine | Check linux/amd64 support in your runtime. The tutorial does not require a source build. |
| `Refusing to replace existing output` | Keep the earlier report and use a new path, such as `--out "$PWD/wald-results/public-assessment-2"`. |
| Generated fixture does not match `assessment.json` | Restore the unmodified fixture files from the public repository. Do not change its pinned hashes. |
| `Assessment verification failed` | Check that the image reference came from the 0.1.3 release and the fixture files still match that release. Keep the failure and report; do not edit the expected result to make it pass. |

The container exits when the run finishes. Keep the report and image reference together so someone else can check what you ran. No service needs stopping.

## Measure your own history next

The [own-history tutorial](your-history.md) explains the required export, the assessment cutoff, and the same offline command using your records. Export preparation is a separate task. Start that tutorial when your data owner has prepared the history and independently observed outcomes.
