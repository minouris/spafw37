#!/usr/bin/env bash
set -euo pipefail

REQUIRE_SDIST=${1:-true}

set +e
OUT=$(python3 .github/scripts/find_artifacts.py dist ${REQUIRE_SDIST} 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then
  echo "$OUT" >&2
  exit $rc
fi

WHEEL=$(echo "$OUT" | sed -n '1p')
SDIST=$(echo "$OUT" | sed -n '2p')
REQ=$(echo "$OUT" | sed -n '3p')

# Write to GITHUB_OUTPUT if it exists (CI environment), otherwise just print
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "wheel_path=$WHEEL" >> $GITHUB_OUTPUT
  echo "sdist_path=$SDIST" >> $GITHUB_OUTPUT
  echo "requires_python=$REQ" >> $GITHUB_OUTPUT
else
  echo "wheel_path=$WHEEL"
  echo "sdist_path=$SDIST"
  echo "requires_python=$REQ"
fi
