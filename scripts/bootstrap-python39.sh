#!/usr/bin/env bash
# Restore the official setup-python 3.9 asset if the hosted image omits it.
set -euo pipefail

. /etc/os-release
if [[ "$ID" != ubuntu || "$VERSION_ID" != 24.04 || "$(uname -m)" != x86_64 ]]; then
  exit 0
fi
for marker in "$RUNNER_TOOL_CACHE"/Python/3.9.*/x64.complete; do
  [[ -f "$marker" ]] && exit 0
done
if [[ -e "$RUNNER_TOOL_CACHE/Python/3.9.25/x64" ]]; then
  echo 'Refusing to replace an incomplete Python tool-cache directory.' >&2
  exit 1
fi
work="$(mktemp -d "$RUNNER_TEMP/python39.XXXXXXXX")"
timeout 120s gh api --header 'Accept: application/octet-stream' \
  'repos/actions/python-versions/releases/assets/311997504' > "$work/python.tar.gz"
printf '%s  %s\n' '3f3be0babc02c5c457df8546207c7bea3844c3eef21cb037485ef83c59118cbd' "$work/python.tar.gz" | sha256sum --check
mkdir "$work/extracted"
tar -xzf "$work/python.tar.gz" -C "$work/extracted"
(cd "$work/extracted" && LD_LIBRARY_PATH="$work/extracted/lib" bash setup.sh)
