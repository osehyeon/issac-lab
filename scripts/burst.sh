#!/bin/zsh
set -e
secs=${1:-7}
app="Isaac Sim WebRTC Streaming Client"
out=${TMPDIR:-/tmp}/isaac_burst
rm -rf $out && mkdir -p $out
osascript -e 'tell application "Preview" to quit' 2>/dev/null || true
osascript -e "tell application \"$app\" to activate"
sleep 1.5
b=$(osascript -e "tell application \"System Events\" to tell process \"$app\" to get {position, size} of window 1")
IFS=', ' read -r x y w h <<< "$b"
for i in $(seq -w 1 $((secs * 4))); do
  screencapture -x -R"$x,$y,$w,$h" $out/f$i.png
  sleep 0.25
done
echo $out
