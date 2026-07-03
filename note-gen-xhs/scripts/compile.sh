#!/usr/bin/env bash
# Compile a note's LaTeX into a PDF, copy it to a title-prefixed PDF, then open it.
# Usage: bash compile.sh <work_dir> <jobname> [engine]
set -e

WORK_DIR="${1:?usage: compile.sh <work_dir> <jobname> [engine]}"
JOB="${2:?usage: compile.sh <work_dir> <jobname> [engine]}"
ENGINE="${3:-xelatex}"
TEXBIN="$HOME/texlive/bin/universal-darwin"
TEX="$TEXBIN/$ENGINE"
BIBTEX="$TEXBIN/bibtex"
SLUG="$(basename "$WORK_DIR")"
FINAL_PDF="${SLUG}-${JOB}.pdf"

if [ ! -x "$TEX" ] && [ -x "/Library/TeX/texbin/$ENGINE" ]; then
  TEX="/Library/TeX/texbin/$ENGINE"
fi
if [ ! -x "$BIBTEX" ] && [ -x "/Library/TeX/texbin/bibtex" ]; then
  BIBTEX="/Library/TeX/texbin/bibtex"
fi

cd "$WORK_DIR"

"$TEX" -interaction=nonstopmode "$JOB.tex" > /dev/null 2>&1 || true
if grep -q "\\\\citation\|\\\\bibdata" "$JOB.aux" 2>/dev/null; then
  "$BIBTEX" "$JOB" > /dev/null 2>&1 || true
fi
"$TEX" -interaction=nonstopmode "$JOB.tex" > /dev/null 2>&1 || true
PAGES=$("$TEX" -interaction=nonstopmode "$JOB.tex" 2>&1 | grep -oE "Output written on .*\([0-9]+ page" | grep -oE "[0-9]+ page" | grep -oE "[0-9]+" || echo "?")

if [ -f "$JOB.pdf" ]; then
  cp "$JOB.pdf" "$FINAL_PDF"
  echo "OK  $WORK_DIR/$FINAL_PDF  (${PAGES} pages)"
  echo "ARTIFACT  $WORK_DIR/$JOB.pdf"
  open "$FINAL_PDF" 2>/dev/null || true
else
  echo "FAIL  no PDF produced. Last log tail:"
  tail -20 "$JOB.log" 2>/dev/null || true
  exit 1
fi

