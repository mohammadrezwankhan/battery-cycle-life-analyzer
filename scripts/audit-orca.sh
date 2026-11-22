#!/usr/bin/env bash
set -euo pipefail
out="$PWD/reader-evidence"
mkdir -p "$out"
mark() { printf '%s %s\n' "$(date -Is)" "$*" | tee -a "$out/progress.log"; }
reader=""
recorder=""
http=""
chrome=""
finish_process() {
  local pid="${1:-}" name="${2:-process}" state=""
  [[ -n "$pid" ]] || return 0
  kill -TERM "$pid" 2>/dev/null || true
  for n in $(seq 1 50); do
    state="$(ps -o stat= -p "$pid" 2>/dev/null || true)"
    [[ -z "$state" || "$state" == Z* ]] && break
    sleep 0.1
  done
  state="$(ps -o stat= -p "$pid" 2>/dev/null || true)"
  if [[ -n "$state" && "$state" != Z* ]]; then
    mark "$name did not stop after five seconds; sending KILL"
    kill -KILL "$pid" 2>/dev/null || true
  fi
  wait "$pid" 2>/dev/null || true
  mark "$name reaped"
}
cleanup() {
  set +e
  finish_process "$reader" Orca
  finish_process "$recorder" Recorder
  finish_process "$chrome" Chrome
  finish_process "$http" HTTP
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mark "screen-reader versions"
orca --version > "$out/version.txt"
google-chrome --version >> "$out/version.txt"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-$RUNNER_TEMP/orca-runtime}"
mkdir -p "$XDG_RUNTIME_DIR"
chmod 700 "$XDG_RUNTIME_DIR"
pulseaudio --start --exit-idle-time=-1
pactl load-module module-null-sink sink_name=bcla
pactl set-default-sink bcla
pactl info > "$out/audio-sink.txt"
mkdir -p "$HOME/.config/speech-dispatcher"
printf '%s\n' 'AudioOutputMethod "pulse"' 'DefaultModule espeak-ng' > "$HOME/.config/speech-dispatcher/speechd.conf"
speech-dispatcher -d
mark "speech-dispatcher probe started"
timeout 15 spd-say -w "Screen reader audio check"
mark "speech-dispatcher probe completed"
parecord --device=bcla.monitor --file-format=wav "$out/narration.wav" &
recorder=$!
mark "audio capture started pid=$recorder"
gsettings set org.gnome.desktop.a11y.applications screen-reader-enabled true
openbox > "$out/window-manager.log" 2>&1 &
sleep 2
orca --replace --debug-file="$out/orca.log" > "$out/orca-console.log" 2>&1 &
reader=$!
mark "Orca started pid=$reader"
python3 -m http.server 4180 --bind 127.0.0.1 --directory docs > "$out/site.log" 2>&1 &
http=$!
mark "local site server started pid=$http"
sleep 4
google-chrome --user-data-dir="$RUNNER_TEMP/orca-chrome" --no-first-run --no-default-browser-check --force-renderer-accessibility --disable-gpu --window-size=1280,1000 --window-position=0,0 http://127.0.0.1:4180/ > "$out/chrome.log" 2>&1 &
chrome=$!
mark "Chrome started pid=$chrome"
for n in $(seq 1 35); do
  win=$(xdotool search --onlyvisible --name "Battery Cycle-Life Lab" 2>/dev/null | tail -1 || true)
  test -z "$win" || break
  sleep 1
done
test -n "$win"
xdotool windowactivate --sync "$win"
xdotool windowfocus --sync "$win"
xdotool getwindowname "$win" > "$out/title.txt"
mark "site title confirmed: $(cat "$out/title.txt")"
# Click inside the rendered page, then use Tab so Orca follows page controls,
# not the browser omnibox. The initial Chrome URL already points to this server.
xdotool mousemove --sync 640 400 click 1
sleep 1
xdotool key Tab
mark "page click and initial Tab sent"
for n in $(seq 1 60); do xdotool key Tab; sleep .45; done
xdotool key Control_L+Home
sleep 1
for n in 1 2 3; do xdotool key h; sleep 1; done
xdotool getwindowname "$win" > "$out/final-title.txt"
grep -i 'speech output' "$out/orca.log" > "$out/speech.txt"
expected=("Battery Cycle-Life Lab" "Reset" "Load lesson preset" "Check outcomes" "Export CSV")
missing=0
for label in "${expected[@]}"; do
  if grep -Fqi "$label" "$out/speech.txt"; then
    mark "ANNOUNCED label: $label"
  else
    mark "MISSING label: $label"
    missing=1
  fi
done
if grep -Fqi 'Run simulation' "$out/speech.txt" || grep -Fqi 'Pause simulation' "$out/speech.txt"; then
  mark "ANNOUNCED label: Run or Pause simulation"
else
  mark "MISSING label: Run or Pause simulation"
  missing=1
fi
if [[ "$missing" -ne 0 ]]; then
  exit 1
fi
mark "required page and control labels found in Orca speech output"
finish_process "$recorder" Recorder
recorder=""
finish_process "$reader" Orca
reader=""
finish_process "$chrome" Chrome
chrome=""
finish_process "$http" HTTP
http=""
