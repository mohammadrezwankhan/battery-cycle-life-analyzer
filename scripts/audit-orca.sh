#!/usr/bin/env bash
set -euo pipefail
out="$PWD/reader-evidence"
orca --version > "$out/version.txt"
google-chrome --version >> "$out/version.txt"
gsettings set org.gnome.desktop.a11y.applications screen-reader-enabled true
orca --replace --debug-file="$out/orca.log" > "$out/orca-console.log" 2>&1 &
reader=$!
python3 -m http.server 4180 --bind 127.0.0.1 --directory docs > "$out/site.log" 2>&1 &
http=$!
trap 'kill "$reader" "$http" 2>/dev/null || true' EXIT
sleep 4
google-chrome --user-data-dir="$RUNNER_TEMP/orca-chrome" --no-first-run --no-default-browser-check --force-renderer-accessibility --disable-gpu http://127.0.0.1:4180/ > "$out/chrome.log" 2>&1 &
for n in $(seq 1 35); do
  win=$(xdotool search --onlyvisible --class google-chrome 2>/dev/null | tail -1 || true)
  test -z "$win" || break
  sleep 1
done
xdotool windowfocus --sync "$win"
xdotool getwindowname "$win" > "$out/title.txt"
for n in $(seq 1 45); do xdotool key Tab; sleep .45; done
xdotool key Escape Control_L+Home
sleep 1
for n in 1 2 3; do xdotool key h; sleep 1; done
grep -i 'speech output' "$out/orca.log" > "$out/speech.txt"
grep -Ei 'simulation|lesson|configuration|reset|export' "$out/speech.txt"
