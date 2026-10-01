# Wald Benchmark

This repository owns the public, reproducible benchmark for Wald releases. It contains the synthetic fixture design, generator, independent verifier, and image runner; it never contains Wald's source code. Each version is run against the corresponding public image, and its durable release assets bind the exact image digest to the observed result.

## Run 0.1

The benchmark needs Python 3 and a Docker-compatible container runtime. On macOS, the Docker CLI supplied by OrbStack works without any benchmark-specific setup.

```sh
git clone https://github.com/finesample-lab/wald-benchmark.git
cd wald-benchmark
benchmark/public-assessment-v0.1/run.sh \
  --image ghcr.io/finesample-lab/wald:v0.1.0 \
  --out /tmp/wald-assessment-0.1
```

The runner generates the fixture from its checked-in definition, verifies every generated input hash, runs the image without network access, and independently checks the reports and expected result. It refuses to replace an existing output directory.

For the exact release image, download `image-reference.txt` from the matching [GitHub release](https://github.com/finesample-lab/wald-benchmark/releases) and pass its contents to `--image`:

```sh
benchmark/public-assessment-v0.1/run.sh \
  --image "$(cat image-reference.txt)" \
  --out /tmp/wald-assessment-0.1-by-digest
```

## What the result means

The 0.1 benchmark is a fixed, synthetic fraud alert history. It demonstrates the evaluator's report shape, point-in-time behavior, refusal boundaries, and reproducibility. Its expected result is declared in [`assessment.json`](benchmark/public-assessment-v0.1/assessment.json), then checked independently by [`verify.py`](benchmark/public-assessment-v0.1/verify.py).

It is not evidence of performance on an institution's alerts, a competitive leaderboard, a safety certification, or a claim about underwriting or another decision pack. A buyer's own historical export is the evidence for that buyer's opportunity.

## Releases and trust

The matching Wald release workflow compares its bundled benchmark with this repository's version tag before publishing. This repository then pulls the public image anonymously by tag, resolves it to an immutable digest, runs the benchmark against that digest, and publishes checksummed source and result archives.

Wald's image also carries the same files at `/usr/share/doc/wald/public-assessment-v0.1/`. `SHA256SUMS` in each benchmark release covers every durable asset.

## Licensing boundary

The benchmark source and synthetic fixture definition in this repository are licensed under the [MIT License](LICENSE). That license does not apply to Wald, its image, its binary, its decision packs, or fineSample trademarks. The separately distributed evaluator is governed by [Wald's evaluation terms](EVALUATION-TERMS.md).

`LICENSE` is the standard legal text for the benchmark materials, so it intentionally contains no maintenance header. Generated JSONL inputs and report files are intentionally untracked; the versioned generator and release workflow are their maintainable sources.
