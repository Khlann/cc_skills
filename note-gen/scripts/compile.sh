#!/usr/bin/env bash
# Compile a note's LaTeX into a PDF, then open it.
# Usage: bash compile.sh <work_dir> <jobname> [engine]
#   <work_dir> : directory containing <jobname>.tex (and optional refs.bib, figures/)
#   <jobname>  : tex filename without extension (e.g. "note")
#   [engine]   : "xelatex" (default, needed for Chinese/ctex) or "pdflatex"
set -e

WORK_DIR="${1:?usage: compile.sh <work_dir> <jobname> [engine]}"
JOB="${2:?usage: compile.sh <work_dir> <jobname> [engine]}"
ENGINE="${3:-xelatex}"
TEXBIN="$HOME/texlive/bin/universal-darwin"
TEX="$TEXBIN/$ENGINE"
BIBTEX="$TEXBIN/bibtex"

cd "$WORK_DIR"

"$TEX" -interaction=nonstopmode "$JOB.tex" > /dev/null 2>&1 || true
# Run bibtex only if a \bibliography or \citation appears in the aux
if grep -q "\\\\citation\|\\\\bibdata" "$JOB.aux" 2>/dev/null; then
  "$BIBTEX" "$JOB" > /dev/null 2>&1 || true
fi
"$TEX" -interaction=nonstopmode "$JOB.tex" > /dev/null 2>&1 || true
PAGES=$("$TEX" -interaction=nonstopmode "$JOB.tex" 2>&1 | grep -oE "Output written on .*\([0-9]+ page" | grep -oE "[0-9]+ page" | grep -oE "[0-9]+" || echo "?")

if [ -f "$JOB.pdf" ]; then
  echo "OK  $WORK_DIR/$JOB.pdf  (${PAGES} pages)"
  open "$JOB.pdf" 2>/dev/null || true
else
  echo "FAIL  no PDF produced. Last log tail:"
  tail -20 "$JOB.log" 2>/dev/null || true
  exit 1
fi
