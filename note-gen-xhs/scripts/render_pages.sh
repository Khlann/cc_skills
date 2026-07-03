#!/usr/bin/env bash
# Render a note PDF into <work_dir>/pages and create <work_dir>/pages.zip.
# Usage: bash render_pages.sh <work_dir> [pdf_name] [dpi]
set -e

WORK_DIR="${1:?usage: render_pages.sh <work_dir> [pdf_name] [dpi]}"
SLUG="$(basename "$WORK_DIR")"
PDF_NAME="${2:-${SLUG}-note.pdf}"
DPI="${3:-220}"

PDF="$WORK_DIR/$PDF_NAME"
PAGES_DIR="$WORK_DIR/pages"
PREFIX="$PAGES_DIR/${SLUG}-page"
PDFTOPPM="${PDFTOPPM:-$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm}"

if [ ! -f "$PDF" ]; then
  echo "Missing PDF: $PDF" >&2
  exit 1
fi
if [ ! -x "$PDFTOPPM" ]; then
  PDFTOPPM="$(command -v pdftoppm || true)"
fi
if [ -z "$PDFTOPPM" ]; then
  echo "Missing pdftoppm. Install Poppler or use the Codex bundled runtime." >&2
  exit 1
fi

rm -rf "$PAGES_DIR"
mkdir -p "$PAGES_DIR"
"$PDFTOPPM" -r "$DPI" -png "$PDF" "$PREFIX"

cd "$WORK_DIR"
rm -f pages.zip
zip -qr pages.zip pages
COUNT="$(find pages -type f -name '*.png' | wc -l | tr -d ' ')"
echo "OK  $PAGES_DIR  (${COUNT} pages)"
echo "ZIP $WORK_DIR/pages.zip"

