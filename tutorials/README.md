---
# Owns the public tutorial index and the boundary between evaluation and live use.
# Keep every linked walkthrough runnable with public artifacts, without product source.
title: Start with a result
audience: Evaluators, data teams, and decision-pack authors
status: Public Wald 0.1 tutorials
---

# Start with a result

These tutorials use Wald's public evaluator image and the files in this
repository. You do not need Wald's private source, a service account, or a model
download. Each path names its prerequisites, expected output, and limits.

| You want to | Start here | Allow |
| --- | --- | --- |
| See and verify a result before bringing data | [Run your first assessment](getting-started.md) | About 10 minutes after setup and downloads |
| Find the opportunity in your own queue | [Assess your own history](your-history.md) | About 10 minutes to run a prepared export; preparation depends on your data |
| Try a decision beyond fraud | [Run the warranty pack](warranty-pack.md) | About 10 minutes after setup and downloads |

The fraud walkthrough uses the 0.1.3 release. The warranty composition proof
retains its published 0.1.2 image and result. Follow the image reference in each
tutorial; a different image is a different experiment, not an interchangeable
dependency.

## What this release supports

The public 0.1 offering supports historical assessments and, from 0.1.3,
offline validation of complete decision packs. It changes no live queue.
Read the [evaluation terms](../EVALUATION-TERMS.md) for permitted use.

Wald also has a live API and workbench. The binary contains additional runtime
commands, but their presence does not expand this release's supported or
licensed scope. These tutorials do not deploy that service or enable live
actions. See the [release boundary](../docs/RELEASE-BOUNDARY.md).

## Build on the examples

Use the [pack-authoring guide](../docs/PACK-AUTHORING.md) and
[format reference](../docs/PACK-REFERENCE-v0.1.md) when you are ready to define
your own decision. The [minimal starter](../packs/minimal-v0.1/README.md)
is the smallest complete example. The public
[authoring skill](../skills/author-a-wald-pack/SKILL.md) follows the same
contracts for people who prefer to work with an agent.
