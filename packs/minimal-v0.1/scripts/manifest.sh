#!/bin/sh
# Owns the minimal pack's generated digest inventory. `--write` replaces the
# inventory with hashes of every distributed file except the inventory itself;
# the default mode verifies those bytes before the pack is copied or published.

set -eu
export LC_ALL=C

pack_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
manifest="$pack_dir/MANIFEST.sha256"

if [ "${1:-check}" = "--write" ]; then
  temporary="$manifest.tmp"
  (
    cd "$pack_dir"
    find . -type f ! -name MANIFEST.sha256 ! -name MANIFEST.sha256.tmp -print \
      | LC_ALL=C sort \
      | sed 's#^\./##' \
      | xargs shasum -a 256
  ) >"$temporary"
  mv "$temporary" "$manifest"
  exit 0
fi

cd "$pack_dir"
shasum -a 256 -c MANIFEST.sha256

