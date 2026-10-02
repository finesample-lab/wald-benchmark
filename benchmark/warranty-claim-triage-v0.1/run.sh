#!/bin/sh
# Runs the warranty-claim composition benchmark from a supplied Wald image.
# It mounts the published pack and generated fixture read-only, disables
# container networking, then asks the independent verifier to bind the result.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$script_dir/../.." && pwd)
pack_dir="$repo_dir/packs/warranty-claim-triage-v0.1"
image=""
output=""

usage() {
    echo "Usage: $0 --image ALREADY-PRESENT-IMAGE --out DIRECTORY" >&2
    echo "       WALD_BIN=/absolute/path/to/wald $0 --out DIRECTORY" >&2
    exit 2
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --image)
            [ "$#" -ge 2 ] || usage
            image=$2
            shift 2
            ;;
        --out)
            [ "$#" -ge 2 ] || usage
            output=$2
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            usage
            ;;
    esac
done

[ -n "$output" ] || usage
[ -d "$pack_dir" ] || {
    echo "Published warranty pack is missing: $pack_dir" >&2
    exit 1
}
if [ -e "$output" ]; then
    echo "Refusing to replace existing output: $output" >&2
    exit 1
fi

fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/wald-warranty-claim-triage-v0.1.XXXXXX")
cleanup() {
    rm -rf -- "$fixture_dir"
}
trap cleanup EXIT HUP INT TERM

python3 "$script_dir/generate.py" \
    --definition "$script_dir/assessment.json" \
    --pack "$pack_dir" \
    --output "$fixture_dir"
output_parent=$(dirname -- "$output")
output_name=$(basename -- "$output")
mkdir -p "$output_parent"
output_parent=$(CDPATH= cd -- "$output_parent" && pwd)
output="$output_parent/$output_name"

if [ -n "$image" ]; then
    docker image inspect "$image" >/dev/null
    docker run --rm \
        --pull never \
        --network none \
        --user "$(id -u):$(id -g)" \
        --volume "$pack_dir:/pack:ro" \
        "$image" test /pack/fixtures
    docker run --rm \
        --pull never \
        --network none \
        --user "$(id -u):$(id -g)" \
        --volume "$fixture_dir:/fixture:ro" \
        --volume "$pack_dir:/pack:ro" \
        --volume "$output_parent:/results" \
        "$image" backtest /fixture \
            --pack /pack \
            --minutes-per-review 12 \
            --out "/results/$output_name"
elif [ -n "${WALD_BIN:-}" ]; then
    "$WALD_BIN" test "$pack_dir/fixtures"
    "$WALD_BIN" backtest "$fixture_dir" \
        --pack "$pack_dir" \
        --minutes-per-review 12 \
        --out "$output"
else
    echo "Choose an already-present released image with --image, or set WALD_BIN explicitly." >&2
    exit 2
fi

test -f "$output/backtest.json"
test -f "$output/backtest.md"
test -f "$output/assessment-manifest.json"
python3 "$script_dir/verify.py" \
    --definition "$script_dir/assessment.json" \
    --fixture "$fixture_dir" \
    --pack "$pack_dir" \
    --result "$output"
echo "Warranty composition assessment: $output"
