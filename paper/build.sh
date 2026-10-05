#!/usr/bin/env bash
# Build the academic PDF from the Markdown source.
# Requires: pandoc and a LaTeX engine (tectonic recommended).
# TECTONIC=/path/to/tectonic ./paper/build.sh
set -euo pipefail
cd "$(dirname "$0")"
ENGINE="${PDF_ENGINE:-tectonic}"
pandoc majors-and-football.md \
  -o majors-and-football.pdf \
  --pdf-engine="$ENGINE" \
  -V documentclass=article \
  -V geometry:margin=0.85in \
  -V fontsize=10pt \
  -V linestretch=0.96 \
  -V colorlinks=true \
  -V linkcolor=black -V urlcolor=NavyBlue -V citecolor=black \
  -V pagestyle=plain
echo "wrote $(pwd)/majors-and-football.pdf"
