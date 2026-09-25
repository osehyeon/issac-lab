#!/bin/zsh
set -e
name=${1:?usage: capture.sh <example> <command> [note]}
cmd=${2:--}
note=${3:-}
app="Isaac Sim WebRTC Streaming Client"
cd "${0:A:h}/.."
mkdir -p captures
n=1
while [[ -e captures/${name}_$n.png ]]; do n=$((n+1)); done
f=captures/${name}_$n.png
osascript -e 'tell application "Preview" to quit' 2>/dev/null || true
osascript -e "tell application \"$app\" to activate"
sleep 1.5
b=$(osascript -e "tell application \"System Events\" to tell process \"$app\" to get {position, size} of window 1")
IFS=', ' read -r x y w h <<< "$b"
screencapture -x -R"$x,$y,$w,$h" "$f"
log=captures/README.md
if [[ ! -e $log ]]; then
  printf '# Captures\n\n| File | Example | Time | Command | Note |\n|---|---|---|---|---|\n' > $log
fi
[[ $cmd != - ]] && cmd="\`$cmd\`"
printf '| [%s](%s) | %s | %s | %s | %s |\n' "${f:t}" "${f:t}" "$name" "$(date '+%Y-%m-%d %H:%M')" "$cmd" "$note" >> $log
echo "$f"
