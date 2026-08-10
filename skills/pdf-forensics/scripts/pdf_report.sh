#!/usr/bin/env bash

set -u

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s INPUT.pdf\n' "$0" >&2
  exit 2
fi

pdf="$1"
[ -f "$pdf" ] || { printf 'File not found: %s\n' "$pdf" >&2; exit 1; }

printf '== File ==\n'
file "$pdf"
printf '\n== Metadata ==\n'
pdfinfo "$pdf" 2>&1 || true
printf '\n== Structure ==\n'
qpdf --check "$pdf" 2>&1 || true
printf '\n== Fonts ==\n'
pdffonts "$pdf" 2>&1 || true
printf '\n== Images ==\n'
pdfimages -list "$pdf" 2>&1 || true
