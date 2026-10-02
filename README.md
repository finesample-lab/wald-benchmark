<!--
This is the public entry point for evaluating Wald and authoring decision packs.
Keep the first run simple, the result's limits visible, and product previews
distinct from the supported historical evaluator. Detailed contracts live in docs.
-->

<p align="center">
  <img src="docs/assets/wald-banner.svg" alt="Wald by fineSample. Most alerts end in release. Start there." width="100%">
</p>

<p align="center">
  <a href="tutorials/getting-started.md">Try Wald free</a> ·
  <a href="tutorials/your-history.md">Assess your history</a> ·
  <a href="tutorials/warranty-pack.md">Try the warranty pack</a>
</p>

Wald helps teams get legitimate customers out of alert queues sooner. Start
with your history: see which alerts Wald would have released, what happened
to them later, and which still needed a person.

This repository gives you a free evaluator to run, public examples to inspect,
and a separate verifier to check the result. You do not need an account or
Wald's private source. The assessment runs locally with networking disabled
and changes no live queue.

## Meet the workbench

![Wald workbench showing a synthetic alert, its model answers, and supporting facts](docs/assets/workbench-queue.jpg)

*Product preview: the full development runtime with synthetic data. The free
0.1 offering supports historical assessment, not deployment of this workbench.*

The full product brings the case, model answers, and facts together. People
handle unfamiliar alerts and review blind samples of decisions automation
would otherwise hide. Wald learns from independently observed outcomes.

<details>
<summary>See how facts are computed</summary>

<p><img src="docs/assets/workbench-facts.jpg" alt="The workbench explains each fact and shows where history is missing"></p>

<p><em>Synthetic development data. These are product screens, not benchmark results.</em></p>

</details>

## Your first result

| You want to | Start here |
| --- | --- |
| Run a published example and verify its answer | [Your first assessment](tutorials/getting-started.md) |
| Measure the opportunity in a prepared export | [Your own history](tutorials/your-history.md) |
| Use Wald for a decision beyond fraud | [The warranty pack](tutorials/warranty-pack.md) |

Allow about 10 minutes after the prerequisites and downloads. Preparing your
own export takes separate work. The tutorials identify the exact image for
each experiment, show the expected output, and explain what the result means.

## A result you can check

On the [published fraud fixture](https://github.com/finesample-lab/wald-benchmark/releases/tag/v0.1.3),
Wald assesses 600 held-out alerts:

| Would release | Later adverse outcomes among them | Kept with a person |
| ---: | ---: | ---: |
| 526 | 6 of 526: 1.1% (95% Wilson interval: 0.5% to 2.5%) | 74 |

**What we don't know yet.** fineSample wrote the synthetic history, evaluator,
and verifier. This is a reproducible historical result, not independent
validation, a competitive ranking, or a prediction for your queue. It does
not test the live learning loop. The interval describes this constructed
fixture, not another population. The report's illustrative 104 review hours
are 520 later-legitimate candidates multiplied by an assumed 12 minutes,
not measured savings.

[Read the fixture design](benchmark/public-assessment-v0.1/README.md) or
[run it on your own history](tutorials/your-history.md).

## Bring another decision

Fraud is the first application. The public
[warranty pack](packs/warranty-claim-triage-v0.1/README.md) asks whether a claim
can leave enhanced abuse review and enter ordinary warranty adjudication.
It does not decide warranty coverage or authorize payment.

Run its [400-claim composition benchmark](tutorials/warranty-pack.md) to see
Wald use customer history, product state, and facts across customers on the
same serial number. It proves composition and reproducibility, not production
warranty accuracy. The tutorial retains the proof's pinned 0.1.2 image.

To define your own decision, start with the
[pack-authoring guide](docs/PACK-AUTHORING.md),
[minimal complete pack](packs/minimal-v0.1/README.md), and
[format reference](docs/PACK-REFERENCE-v0.1.md).
The [authoring skill](skills/author-a-wald-pack/SKILL.md) follows those same
public contracts when you work with an agent.

## What's public

The benchmark source, synthetic fixture definitions, example packs, and
authoring kit are public. Wald's product source remains private.

The 0.1 image supports historical assessment and, from 0.1.3, offline validation
of complete packs. Although the binary contains server commands, API and
workbench deployment are outside this release's supported and licensed scope.
[Read the release boundary](docs/RELEASE-BOUNDARY.md).

The benchmark source is [MIT-licensed](LICENSE). The
[minimal starter](packs/minimal-v0.1/LICENSE) and
[warranty pack](packs/warranty-claim-triage-v0.1/LICENSE) carry their own MIT
grants. Those licences do not apply to Wald's image, binary, unpublished packs,
or fineSample trademarks. Use of the evaluator is governed by the
[evaluation terms](EVALUATION-TERMS.md).

[Published releases](https://github.com/finesample-lab/wald-benchmark/releases) · [Tutorials](tutorials/README.md) · [How releases are checked](docs/RELEASE-BOUNDARY.md#how-releases-are-checked)
