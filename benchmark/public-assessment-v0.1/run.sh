#!/bin/sh
# Runs Wald Public Benchmark 0.1 from a local binary or an immutable image.
# It generates and hash-checks the synthetic inputs, then passes them to the
# existing `wald backtest` command; Wald owns every report written to --out.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
image=""
output=""

usage() {
    echo "Usage: $0 [--image IMAGE] --out DIRECTORY" >&2
    echo "       WALD_BIN=/path/to/wald $0 --out DIRECTORY" >&2
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
if [ -e "$output" ]; then
    echo "Refusing to replace existing output: $output" >&2
    exit 1
fi

fixture_dir=$(mktemp -d "${TMPDIR:-/tmp}/wald-public-assessment-v0.1.XXXXXX")
cleanup() {
    rm -rf -- "$fixture_dir"
}
trap cleanup EXIT HUP INT TERM

python3 "$script_dir/generate.py" --output "$fixture_dir"
output_parent=$(dirname -- "$output")
output_name=$(basename -- "$output")
mkdir -p "$output_parent"
output_parent=$(CDPATH= cd -- "$output_parent" && pwd)
output="$output_parent/$output_name"

if [ -n "$image" ]; then
    docker run --rm \
        --network none \
        --user "$(id -u):$(id -g)" \
        --volume "$fixture_dir:/fixture:ro" \
        --volume "$output_parent:/results" \
        "$image" backtest /fixture --out "/results/$output_name"
elif [ -n "${WALD_BIN:-}" ]; then
    "$WALD_BIN" backtest "$fixture_dir" --out "$output"
else
    echo "Choose the released image with --image, or set WALD_BIN to an explicit local binary." >&2
    exit 2
fi

test -f "$output/backtest.json"
python3 "$script_dir/verify.py" --fixture "$fixture_dir" --result "$output" --definition "$script_dir/assessment.json"
echo "Assessment report: $output"
