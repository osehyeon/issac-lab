#!/bin/bash
set -e
isaaclab=${ISAACLAB:-$HOME/IsaacLab}
out=${1:-$HOME/issac-lab-work/patched}
cd "$(dirname "$0")/.."
mkdir -p "$out"
for p in patches/*.patch; do
  src=$(sed -n '1s#^--- a/##p' "$p")
  dst="$out/$(basename "$p" .patch).py"
  cp "$isaaclab/$src" "$dst"
  patch -s "$dst" "$p"
  echo "$dst"
done
