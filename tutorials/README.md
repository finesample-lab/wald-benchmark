---
# Owns the public tutorial index and the boundary between evaluation and live use.
# Keep every linked walkthrough runnable with public artifacts, without product source.
title: Start with a result
audience: Evaluators, data teams, and decision-pack authors
status: Published 0.1 evaluator tutorials and unpublished 0.2 runtime preview candidate
---

# Start with a result

These tutorials use public image releases and the source-free kit in this
repository. `v0.2.0-beta.1` is a candidate, not yet published; the 0.1 historical
walkthroughs remain available. You need no private source or model download.
Each path names its prerequisites, expected output, and limits.

| You want to | Start here | Allow |
| --- | --- | --- |
| Run a queue and keep your work after restart | [Runtime preview](deployment.md) | About 10 minutes after the candidate image is available and downloaded |
| Give an application facts, decisions, and outcomes | [API integration](developer-integration.md) | About 10 minutes with the preview already running |
| See and verify a result before bringing data | [Run your first assessment](getting-started.md) | About 10 minutes after setup and downloads |
| Find the opportunity in your own queue | [Assess your own history](your-history.md) | About 10 minutes to run a prepared export; preparation depends on your data |
| Try a decision beyond fraud | [Run the warranty pack](warranty-pack.md) | About 10 minutes after setup and downloads |

The fraud walkthrough uses the 0.1.3 release. The warranty composition proof
retains its published 0.1.2 image and result. Follow the image reference in each
tutorial; a different image is a different experiment, not an interchangeable
dependency.

## What each release supports

The public 0.1 offering supports historical assessments and, from 0.1.3,
offline validation of complete decision packs. It changes no live queue.
It retains the [terms distributed with 0.1.3](https://github.com/finesample-lab/wald-benchmark/blob/v0.1.3/EVALUATION-TERMS.md).

The 0.2 preview adds one localhost Development tenant: Workbench, durable data,
pack installation, facts, independent outcomes, and existing learning API/CLI.
Its [evaluation terms](../EVALUATION-TERMS.md) permit authorized customer data
and observational live feeds for internal local evaluation. There is no
external write-back. WorkOS, the complete Merit Loop browser workflow,
narration, hosted operation, and production qualification remain outside the
[release boundary](../docs/RELEASE-BOUNDARY.md).

## Build on the examples

Use the [pack-authoring guide](../docs/PACK-AUTHORING.md) and
[format reference](../docs/PACK-REFERENCE-v0.1.md) when you are ready to define
your own decision. The [minimal starter](../packs/minimal-v0.1/README.md)
is the smallest complete example. The public
[authoring skill](../skills/author-a-wald-pack/SKILL.md) follows the same
contracts for people who prefer to work with an agent.
