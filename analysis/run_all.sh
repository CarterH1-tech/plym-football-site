#!/usr/bin/env bash
# Reproduce the full analysis and rebuild the PDF.
#
#   ./analysis/run_all.sh            # assumes analysis/cache/ is already populated
#   ./analysis/run_all.sh --fetch    # download source pages first
#
# PDF_ENGINE defaults to tectonic (must be on PATH).
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${1:-}" == "--fetch" ]]; then
  python3 fetch.py
fi

python3 extract_majors.py
python3 parse_stats.py
python3 parse_records.py
python3 parse_standings.py
python3 analyze.py
python3 side_note.py
python3 make_figures.py

echo "--- building PDF ---"
( cd .. && PDF_ENGINE="${PDF_ENGINE:-tectonic}" ./paper/build.sh )
