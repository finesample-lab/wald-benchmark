# Wald Runtime Preview

This startup kit runs the Wald image without the private source tree.
It owns local Docker setup and an optional synthetic example. The image contains
the runtime, Workbench, live API, and fraud pack. All records, configuration,
keys, and purpose-specific credentials remain in one Docker volume.

`v0.2.0-beta.1` is the release candidate defined by this kit. The commands below
use that tag once published; maintainers can test an already built image with
`--image`. A source commit or a passing local check is not a published release.

## Start Wald

You need Docker with Compose and Python 3.10 or later. The first release image
targets `linux/amd64`; an ARM computer needs Docker's amd64 emulation. The kit
does not download a model, start a database service, or require an identity
provider. Download and extract the runtime-preview release asset, then run:

```sh
python3 wald-preview.py up --sample
python3 wald-preview.py credentials
```

Open the analyst sign-in link to use the queue. Use the artifact-author link to
inspect or edit definitions, and the approver link to inspect Changes. These
are separate purpose-bound identities for **one person's local evaluation**,
not a substitute for organizational sign-in in a shared installation.

The API is at `http://127.0.0.1:7070/v1` and its reference is at
`http://127.0.0.1:7070/v1/openapi.yaml`. The host port accepts local connections
only. Do not expose this quickstart on a public or shared network.

Omit `--sample` for an empty tenant. Bring authorized structured data through
the public API. Canonical input fields must match the pack; this setup does not
infer arbitrary source schemas or process free-text narration. The local
scorecard needs no external model. It reports missing facts rather than
inventing history.

## Inspect the example

`--sample` sends two payments and one alert through the public API. It prints
their identifiers, a typed fact computation, and its receipt identifier. No
review or independent outcome is invented. On a new tenant, the decision can
remain hidden until a blind review is complete; this is expected behavior.

To repeat the example or recover an interrupted submission:

```sh
python3 wald-preview.py sample
```

The example reuses its stored event time, fixed identifiers, and identical
request bodies. It does not add duplicate cases or advance the learning clock.
If its blind review is still open, a repeated run can report
`factsVisibility: "withheldUntilReview"` with null computation and receipt IDs.
The pack's complete fact set includes a narration-derived fact, so the API
correctly conceals it during blind review, even when this example has no text.
Complete the actual blind review in the Workbench before fetching that result.
The fixed identifiers are reserved for this example; use new IDs for your own
activity. All JSON comes from the script or runtime, so no private fixture
directory is needed.

Get one API credential without parsing sign-in links:

```sh
WALD_FACT_TOKEN="$(python3 wald-preview.py credentials --purpose factReader)"
curl -fsS -H "Authorization: Bearer $WALD_FACT_TOKEN" \
  -H 'Wald-Version: 2026-09-28' \
  http://127.0.0.1:7070/v1/feature-sets
```

Use the appropriate purpose for each write. For example, `eventWriter` sends
events, `alertWriter` sends alerts, and `outcomeWriter` reports the installed
fraud pack's first independent source, `chargeback`. A sample case cannot
establish model accuracy or earn permission to release live work.

## Stop and resume

```sh
python3 wald-preview.py stop
python3 wald-preview.py up
```

Stopping does not remove the volume. Starting again reuses the existing
configuration, keys, credentials, and active pack. It does not reset settings,
reseed data, or automatically upgrade an active pack. A partly completed first
pack install resumes through the same API. If initialization itself failed,
the kit refuses to overwrite surviving credentials or keys; inspect and retain
the original volume before taking manual recovery action.

There is deliberately no reset command. Do not run Compose with `down --volumes`
unless you intend to delete this tenant and its evidence. Back up the complete
volume, including keys, before maintenance. Access to the Docker daemon also
grants access to these local credentials.

Inside that volume, `/data/finesample.json` is the runtime configuration.
`/data/preview-credentials.json` maps each API purpose to its original bearer
token. `wald init` creates this file with owner-only permissions; the kit reads
it to resume and to show the sign-in links. Neither file belongs in a repository
or a shared support log.

## Select an image or another local port

```sh
python3 wald-preview.py up --image ghcr.io/finesample-lab/wald:v0.2.0-beta.1
python3 wald-preview.py up --image wald:preview-test --project wald-test --port 17070
```

An available local image is used without a pull. Otherwise Compose pulls the
selected reference. Use the release's signed digest when you need an immutable
image identity. `WALD_IMAGE`, `WALD_PREVIEW_PROJECT`, and `WALD_PREVIEW_PORT` are
equivalent defaults. Keep the project and port consistent for subsequent
commands. Each project owns a separate volume; nothing is removed implicitly.

## Operating boundary

The generated Development configuration uses local SQLite and local keys. It
has no write-back destination, warehouse feed, narration model, or external
identity provider. Development cannot acquire an automatic enforcement lease.
The initial pack activation uses the normal author and approver API; the kit
does not modify the database directly or bypass the runtime's validation.

This preview supports local observation and evaluation, not production
automatic write-back or hosted service. Existing training and Merit Loop
operations remain available through the documented API/CLI where the browser
workflow is incomplete. They do not gain authority from this bootstrap.

For maintainers, `compose.yaml` owns only the image, localhost port and volume.
`wald-preview.py` owns initialization and API orchestration. The release image
check imports its `Preview` class, so the check exercises the same startup kit
users receive instead of maintaining a second bootstrap implementation.
