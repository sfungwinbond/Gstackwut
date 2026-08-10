#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 2 ]; then
  printf 'Usage: %s SOURCE OUTPUT\n' "$0" >&2
  exit 2
fi

source_file="$1"
output_file="$2"
extension="${source_file##*.}"
mkdir -p "$(dirname "$output_file")"

case "$extension" in
  mmd|mermaid) mmdc -i "$source_file" -o "$output_file" ;;
  dot|gv) dot -T"${output_file##*.}" "$source_file" -o "$output_file" ;;
  puml|plantuml)
    output_dir="$(dirname "$output_file")"
    source_stem="$(basename "$source_file")"
    source_stem="${source_stem%.*}"
    generated_file="$output_dir/$source_stem.${output_file##*.}"
    plantuml -t"${output_file##*.}" -o "$output_dir" "$source_file"
    if [ "$generated_file" != "$output_file" ]; then
      mv "$generated_file" "$output_file"
    fi
    ;;
  *) printf 'Unsupported source extension: %s\n' "$extension" >&2; exit 2 ;;
esac
