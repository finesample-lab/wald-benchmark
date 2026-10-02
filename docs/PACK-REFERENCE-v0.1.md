# Wald pack format reference, v0.1

This document owns the versioned public file contract for structured Wald decision packs. Authors use it with [`PACK-AUTHORING.md`](PACK-AUTHORING.md); Wald loads the decision files and settings into one immutable PackVersion, while package metadata, fixtures, licence, and the digest inventory make the directory understandable and reproducible outside the runtime.

This reference describes the complete format demonstrated by [`packs/minimal-v0.1/`](../packs/minimal-v0.1/) and [`packs/warranty-claim-triage-v0.1/`](../packs/warranty-claim-triage-v0.1/). Unknown properties are refused by runtime types unless a section below says the file is publication metadata.

## Directory contract

```text
my-pack/
  README.md
  LICENSE
  pack.json
  catalog.json
  facts.json
  domain.json
  release-conditions.json
  settings/
    thresholds.json
    sampling.json
    evidence.json
    triggers.json
    manifest.json
  fixtures/
    first_case.json
  scripts/
    manifest.sh
  MANIFEST.sha256
```

`scrub-rules.json`, `text-questions.json`, and `narration.json` are optional language artifacts. They are described at the end of this reference.

## `pack.json`: distribution identity

```json
{
  "schemaVersion": 1,
  "id": "my-pack",
  "version": "0.1.0",
  "status": "starter",
  "license": "MIT",
  "compatibility": {
    "wald": ">=0.1.2 <0.2.0",
    "api": "2026-09-28"
  }
}
```

| Property | Contract |
| --- | --- |
| `schemaVersion` | Metadata schema. This reference defines version `1`. |
| `id` | Stable lowercase package id. Keep it equal to the directory stem where practical. |
| `version` | Semantic version of the public package. This is separate from the numeric versions inside runtime artifacts. |
| `status` | Publication status, such as `starter` or `synthetic-example`. It does not grant runtime authority. |
| `license` | SPDX identifier for the package's own `LICENSE`. |
| `compatibility.wald` | Wald release range against which the complete directory was tested. |
| `compatibility.api` | Public API contract date required by installation. |

`pack.json` is public distribution metadata in v0.1. The runtime derives its domain name and PackVersion semantic version from `domain.json`; therefore metadata and runtime identities must be reviewed together even though they serve different boundaries.

## `catalog.json`: admitted evidence

```json
{
  "fields": {
    "fields": {
      "eventId": {"path": "eventId", "type": "text", "nullable": false},
      "entityId": {"path": "entityId", "type": "text", "nullable": false, "sensitivity": "token"},
      "entityType": {"path": "entityType", "type": "text", "nullable": false},
      "eventType": {"path": "eventType", "type": "text", "nullable": false},
      "occurredAt": {"path": "occurredAt", "type": "timestamp", "nullable": false}
    }
  },
  "entityTypes": ["subject"],
  "eventTypes": ["review.opened"],
  "projections": [],
  "projectionRules": {},
  "eventFeeds": {"review.opened": {"maxSilence": "7d"}},
  "stateSources": {},
  "referenceSets": []
}
```

Every event carries `eventId`, `entityId`, `entityType`, `eventType`, and `occurredAt`. Domain fields live below `data.*` and must be registered before use.

### Field registrations

| Property | Meaning |
| --- | --- |
| `path` | Exact event path. |
| `type` | `text`, `narration`, `integer`, `number`, `money`, `boolean`, `timestamp`, or `date`. |
| `nullable` | Defaults to true. False refuses an event without the field. |
| `sensitivity` | `public` by default; `token` for an opaque internal id; `sensitive` for a value never logged or used as a metric label; `directIdentifier` for a value refused at the gateway. |
| `description` | Plain-language explanation for authors and operators. |
| `scale` | Required for `number` and `money`; at most 18 fractional digits. |
| `rounding` | `halfEven` by default, `halfUp`, or `down`. |
| `currencyField` | Required for `money`; names the event field containing its ISO 4217 currency. |
| `match` | When true, indexes a non-decimal `data.*` field used to match historical rows to the current event. |
| `narration` | Required policy for a field of type `narration`; see Optional language artifacts. |

Numbers and money arrive as decimal text, never binary floating-point. Timestamps are RFC 3339 with an explicit offset and at most microsecond precision.

### Sources and projections

- `entityTypes` and `eventTypes` list admitted names.
- `eventFeeds` maps a source event type to `{"maxSilence":"<duration>"}`. Durations use positive whole `s`, `m`, `h`, or `d` units.
- `stateSources` maps a source id to named fields, each with `path` and `type`. A `lookup` fact supplies the maximum usable age.
- `referenceSets` lists set ids read by `exists` facts.
- `projections` lists projection ids.
- `projectionRules` maps a source event type to rules shaped as `{"projection":"serial","entityField":"data.serialNumber","entityType":"serial","eventType":"serial.claim.filed"}`. A projected event is filed under the second entity but retains its relationship to the source event.

A deployed tenant's catalog is additive. A registered field keeps its type, scale, rounding, and currency; sensitivity may only become stricter; a projection keeps its rules.

## `facts.json`: point-in-time fact sets

One set may be the root object:

```json
{
  "schemaVersion": "1.0",
  "id": "subjectActivity",
  "appliesTo": ["subject"],
  "features": []
}
```

Several sets use `{"featureSets":[...]}`. The warranty example uses this form for customer and projected-serial facts.

### Common fact properties

| Property | Meaning |
| --- | --- |
| `name` | Stable camel-case name, unique in the set. |
| `label` | Plain-language label people see. |
| `type` | `integer`, `number`, `money`, `boolean`, `text`, `timestamp`, or `date`. |
| `op` | Operation listed below. |
| `field` | Event field read by an aggregate. |
| `window` | Positive whole number plus `s`, `m`, `h`, or `d`. |
| `current` | Required on history operations: `include` or `exclude`. |
| `where` | Historical-row predicate. |
| `projection` | Projection whose entity history is read. |
| `latest` | Positive cap on matching historical rows, newest first. |
| `currency` | Fixed ISO code or `{"current":"data.currency"}` for money facts and money predicates. |
| `method` | `continuous` or `discrete` for percentile; `sample` or `population` for variance and standard deviation. |
| `percentile` | Exact decimal text, such as `"0.95"`. |
| `scale`, `rounding` | Exact result behavior for decimal calculations. |
| `onZero` | Declared divide-by-zero result. Omission produces an empty result with `divisionByZero`. |
| `args` | Ordered operands for calculations, comparisons, and composition. |
| `branches`, `default` | Ordered cases and required fallback for `case`. |
| `caseSensitive` | Pattern matching behavior; true by default. |
| `source`, `maxAge` | State source and maximum age for `lookup`; reference set for `exists`. |

### Operations

| Group | Operations | Additional properties |
| --- | --- | --- |
| History | `count`, `lastSeen` | `window`, `current`, optional `projection`, `where`, `latest`, and `currency` when the predicate compares money. |
| History | `unique`, `min`, `max`, `mode`, `sum` | Same, plus `field`; `currency` where required. |
| History | `avg` | Same, plus `field`, `scale`, and `rounding`. |
| History | `stdev`, `variance`, `percentile` | Same, plus `method`, `scale`, `rounding`, and `percentile` where applicable. |
| Calculate | `add`, `subtract`, `remainder`, `coalesce` | `args`. |
| Calculate | `multiply` | `args`, `scale`, `rounding`. |
| Calculate | `divide` | `args`, `onZero`, `scale`, `rounding`. |
| Compare | `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in` | `args`. |
| Compare | `match` | `args`, optional `caseSensitive`; patterns support `*` and `?`. |
| Compose | `all`, `any`, `not` | `args`. |
| Compose | `case` | `branches`, `default`. |
| State | `lookup` | `source`, `field`, `maxAge`. |
| Reference | `exists` | `source`, `where` containing one `key` operand. |

### Operands and history predicates

An operand is an object with one key:

- `{"feature":"priorReviews30d"}` reads a preceding fact in the same set.
- `{"current":"data.serialNumber"}` reads the event being computed.
- `{"state":"customerProfile.tier"}` reads point-in-time state.
- `{"value":1}` or `{"value":"0.95"}` supplies a fixed value.
- `{"field":"data.serialNumber"}` reads each historical row and is valid only inside `where`.

`where` accepts compact equality such as `{"eventType":"review.opened"}`, boolean `all`/`any`/`not`, comparisons over two operands, `in`, and `match`. Money comparisons require the fact's `currency` declaration and do not compare two unrelated money fields.

### Empty results

Facts do not invent values. Supported issue reasons include `insufficientData`, `nullInput`, `missingState`, `staleState`, `sourceUnavailable`, `divisionByZero`, `overflow`, `currencyUnavailable`, `timeout`, `historyGap`, `feedNotConnected`, `feedStale`, and `computeFailed`. A count over a connected, fresh feed with no matching history is zero; missing or stale feed evidence is not.

## `domain.json`: questions and starting judgment

The complete structure is:

```json
{
  "domain": "reviewTriage",
  "version": 1,
  "label": "Review triage",
  "classes": {"review": {"label": "Review", "releases": true}},
  "outcomes": {
    "adverse": {"key": "concern_confirmed", "label": "Concern confirmed"},
    "benign": {"key": "no_concern_found", "label": "No concern found"},
    "inconclusive": {"key": "inconclusive", "label": "Inconclusive"}
  },
  "independentSources": ["independentReview"],
  "patterns": ["repeat_review"],
  "patternLabels": {"repeat_review": "Repeat review"},
  "questionSchema": {},
  "roles": {},
  "stateContract": {},
  "scorecard": {}
}
```

Ids are artifact vocabulary; `label` values are human copy. Labels are required for domains, classes, outcomes, questions, and patterns. Outcome keys must be distinct. `independentSources` contains distinct external source names; `analyst` and the built-in `blindAudit` are not declared there.

### Roles and question schema

Required roles:

```json
{
  "release": {"key": "p_clear"},
  "priority": {"key": "priority"},
  "pattern": {"key": "pattern", "none": "none_apparent", "other": "other"}
}
```

The optional `corroboration` role is `{"key":"corroboration","contradicts":"contradicts"}`.

`questionSchema` has `id`, positive numeric `version`, and `questions`. Each question has `key`, `label`, `instructions`, and one primitive:

- `{"type":"noul","proposition":"this review shows no concern requiring specialist review"}` for the release probability;
- `{"type":"score","levels":["very_low","low","medium","high","critical"]}` for priority; or
- `{"type":"choice","options":["named_pattern","none_apparent","other"]}` for pattern.

There are exactly three role questions, or four when corroboration is enabled. Choice options for the pattern role equal declared `patterns`, in their declared order, followed by `none` and `other`. The v0.1 PackVersion vocabulary requires at least one named pattern. Priority has exactly five ordered levels because v0.1 scorecards have four risk edges. Every instruction carries the standing evidence clause shown in the authoring guide.

### State contract

```json
{
  "id": "reviewTriage",
  "version": 1,
  "byteBudget": 8192,
  "featureSets": [
    {"featureSet": "subjectActivity", "as": "subject"}
  ]
}
```

A projected binding also carries `"projection":"serial"`. The alias makes a fact available as `subject.priorReviews30d`. Every scorecard and release-condition state path must resolve through one binding.

### Scorecard

| Part | Shape |
| --- | --- |
| `base` | Exactly one exact-decimal starting score per declared class. |
| `facts` | At least one aliased fact path mapped to bands. |
| `patterns` | Exactly one reachable pattern card per declared pattern. |
| `priority` | Four strictly increasing `riskEdges` between zero and one; `tierSteps` maps exposure tiers to shifts `0`, `1`, or `2`. |
| `familiarity` | `carryingFacts` from 1 through the number of scorecard facts, `floor` from 1 through 10,000, and exact-decimal `marginFloor` from zero through one. |

Band shapes:

- number: `{"kind":"number","edges":["0","2"],"points":["0","-1","-3"],"empty":"0"}`;
- age: `{"kind":"age","hours":["24","168"],"points":["-1","0","0.5"],"empty":"-1"}`;
- boolean: `{"kind":"boolean","true":"1","false":"-1","empty":"0"}`; and
- category: `{"kind":"category","values":{"known":"1"},"other":"0","empty":"-1"}`.

Number and age bands have one more point than edge. Scorecard fact kinds must match the fact result: integer/number to `number`, timestamp to `age`, boolean to `boolean`, and text to `category`. Pattern cards have `floor` and their own fact bands; their maximum attainable points must reach the floor.

## `release-conditions.json`: the domain release test

One releasing class uses one object; several use an array of objects.

```json
{
  "id": "reviewRelease",
  "version": 1,
  "alertClass": "review",
  "exposureCeiling": "none",
  "clear": {
    "all": [
      {"answer": "p_clear", "gte": {"threshold": "pClearMin"}},
      {"state": "subject.priorReviews30d", "lte": 0}
    ]
  },
  "escalate": {"answerTop": "pattern", "in": ["repeat_review", "other"]},
  "expedite": {"state": "subject.priorReviews30d", "gte": 3}
}
```

Conditions compose with `all`, `any`, and `not`. Leaves are:

- `answer` plus `gte`, `lte`, or `eq`, normally against `{"threshold":"name"}`;
- `answerTop` plus `in` for a choice answer; and
- `state` plus `gte`, `lte`, or `eq`, against a literal or named threshold.

`exposureCeiling` is `none` only when alerts of the class never carry money. `byRiskTier`, also the behavior when omitted, requires alert exposure plus `baseCurrency`, `exposureCeilings`, and `riskTierField` settings.

The optional `requiredControlChecks` can list the complete runtime check set for an explicitly pinned contract; omission selects Wald's full current set. `allowContextContradicts` defaults false.

## `settings/thresholds.json`

```json
{
  "version": 1,
  "values": {"pClearMin": "<reviewed-decimal>"},
  "baseCurrency": "USD",
  "exposureCeilings": {},
  "riskTierField": "",
  "rateLimitCount": 1,
  "rateLimitWindowHours": 24,
  "minCalibrationSamples": 500,
  "maxCalibrationError": "<reviewed-decimal-between-zero-and-one>",
  "minHeldOut": 200
}
```

- `values` supplies every named threshold referenced by release conditions as exact decimal text.
- `baseCurrency`, `exposureCeilings`, and `riskTierField` define exposure conversion and ceilings. Empty ceilings and field are valid only when all releasing classes declare `exposureCeiling: none`.
- `rateLimitCount` and `rateLimitWindowHours` cap automatic releases.
- `minCalibrationSamples` and `maxCalibrationError` define the minimum calibration support and accepted error.
- `minHeldOut` is from 1 through 100,000 and controls challenger evaluation.
- Optional `familiarityFloor` and `patternMarginFloor` override the domain's reviewed values.

These are tenant decisions. Wald has no honest generic production value for a new domain.

## `settings/sampling.json`

```json
{
  "version": 1,
  "rates": {},
  "defaultRate": "<reviewed-decimal-above-zero-through-one>",
  "exposureTiers": {},
  "learningRate": "<reviewed-decimal-above-zero-through-one>"
}
```

`rates` maps a stratum or stratum prefix to its blind-sample rate. The longest configured prefix wins; `defaultRate` covers everything else. No rate may be zero. `exposureTiers` maps tier names to ascending monetary bounds; amounts above every bound use `above`. `learningRate` independently samples scorecard answers from the whole population.

## `settings/evidence.json`

```json
{
  "acceptableRate": "<reviewed-rate>",
  "unacceptableRate": "<larger-reviewed-rate>",
  "alpha": "<reviewed-error-bound>",
  "beta": "<reviewed-error-bound>",
  "maxEvidenceAgeHours": 1,
  "labelLatencyHours": 1,
  "recentFalseStopsPerYear": "<reviewed-budget>"
}
```

This is the author input, not the stored sequential-test artifact. On validation or installation Wald derives the log weights, accept/reject bounds, and recent-stop table. Required relationships are `0 < acceptableRate < unacceptableRate < 1`, `0 < alpha,beta < 0.5`, and `maxEvidenceAgeHours > labelLatencyHours`; both time values are at most ten years. Replace all placeholders with reviewed values before validation.

## `settings/triggers.json`

```json
{
  "windowDecisions": 200,
  "maxProviderFaultPerMille": 0,
  "maxIncompletePerMille": 0,
  "controlSources": {}
}
```

`windowDecisions` must be positive. The two per-mille limits range from zero through 1,000; zero is strict and valid. `controlSources`, when present, maps a required source to the positive number of minutes it may stay silent before containment.

## `settings/manifest.json`

```json
{
  "version": 1,
  "model": {"provider": "scorecard", "artifact": "governed-active"},
  "outbox": {"capabilities": []},
  "warehouseFeed": false,
  "anchor": false,
  "evidenceConnectors": [],
  "localModels": []
}
```

The capability manifest can only authorize names also present in deployment configuration. Omit `model` to deny all model work; the scorecard grant shown above authorizes the active governed scorecard. Empty outbox capabilities mean the pack cannot dispatch an action. Names in outbox, connector, and local-model lists must be non-empty and unique. `warehouseFeed` and `anchor` are booleans.

## Fixtures

```json
{
  "name": "one_prior_review",
  "catalog": {},
  "log": [
    {"event": {}},
    {"state": {}},
    {"reference": {}}
  ],
  "featureSet": {},
  "compute": {"eventId": "current"},
  "expect": {
    "features": {"priorReviews30d": 1},
    "issues": []
  }
}
```

Fixtures inline the catalog and one feature set. Log entries may add events, point-in-time state revisions, and reference sets. `compute.projection` selects a projected entity when needed. To prove invalid input, replace `compute` and `expect` with `expectCompileErrors`, a list of compiler error codes. `wald test` runs each executable fixture through both row and day-bucket paths.

## Manifest, guide, and licence

`MANIFEST.sha256` contains a stable, sorted SHA-256 inventory of every distributed file except itself. The pack's `scripts/manifest.sh --write` regenerates it; running the script without arguments verifies it. Because JSON cannot contain comments, the pack README's directory map is the maintenance guide for every JSON file. `LICENSE` is legal text and is also explained there rather than modified with a comment.

## Validation and installation commands

| Task | Command | Availability |
| --- | --- | --- |
| Compile one feature set | `wald validate facts.json --catalog catalog.json` | Wald 0.1.2+ |
| Inspect its execution plan | `wald inspect facts.json --catalog catalog.json` | Wald 0.1.2+ |
| Compare two feature-set files | `wald diff before.json after.json --catalog catalog.json` | Wald 0.1.2+ |
| Run conformance fixtures | `wald test fixtures` | Wald 0.1.2+ |
| Validate the complete directory and settings offline | `wald pack validate <dir>` | Wald 0.1.3+ |
| Publish one immutable PackVersion and submit its Change | `wald pack install <dir> --settings <dir>/settings --url <gateway>` | Wald 0.1.2+ |

`wald pack validate` automatically uses `<dir>/settings`. For a first publication, `wald pack install` requires the author to pass that directory explicitly. Later updates carry the tenant's active settings forward and change them only when `--settings` is supplied again, so omission cannot silently reset tuned values. Installation validates complete settings before its first network mutation. An `artifactAuthor` publishes and submits; a different approver signs the resulting Change.

## Optional language artifacts

A structured pack needs none of these files.

### Narration catalog policy

A `narration` field is nullable, sensitive, and never a match field:

```json
{
  "path": "data.narration",
  "type": "narration",
  "nullable": true,
  "sensitivity": "sensitive",
  "narration": {
    "scrubber": "basic-en-v1+domain-v1",
    "languages": ["en"],
    "maxBytes": 512,
    "model": "installed-model-id",
    "questions": "domainNarration"
  }
}
```

Only evaluated languages belong in the policy. The model is a separately installed, signed, hash-pinned artifact; its weights are not copied into the pack.

### `scrub-rules.json`

An array of versioned rule packs. Each has `guide`, `id`, positive `version`, `checksum`, and ordered `rules`. A rule declares `kind`, bounded regex `pattern`, and `validator`: `none`, `digits`, `luhn`, or `iban`. Supported placeholder kinds are `email`, `url`, `card`, `iban`, `account`, `phone`, `id`, and `number`.

### `text-questions.json`

An array of versioned artifacts. Each has `guide`, `id`, positive `version`, source `field`, and one to ten boolean or choice questions. Boolean questions declare `key`, `label`, `criteria`, and probability `threshold`. Choice questions declare two or more `options`, including `other`, and criteria for every option.

For source `data.narration` and question `pressure`, the stored answer and probability are `data.narrationPressure` and `data.narrationPressureP`. Boolean answers are boolean; choice answers are text; probability fields are sensitive numbers with scale 4. Register all derived fields in the catalog.

### `narration.json`

The deterministic inline encoder named by the state contract. It does not contain the larger scrub-and-question model. A state-contract narration binding names the field, encoder, and optional text-question artifact so the same admitted text evidence is used for judgment and replay.
