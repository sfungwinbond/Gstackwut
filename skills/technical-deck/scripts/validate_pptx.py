#!/usr/bin/env python3
"""Validate the basic integrity and relationships of a PPTX package."""

from __future__ import annotations

import argparse
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def source_part_for_rels(name: str) -> str:
    if name == "_rels/.rels":
        return ""
    directory, filename = posixpath.split(name)
    if not directory.endswith("/_rels") or not filename.endswith(".rels"):
        raise ValueError(f"Unexpected relationships path: {name}")
    source_dir = directory[: -len("/_rels")]
    return posixpath.join(source_dir, filename[: -len(".rels")])


def resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def validate(path: Path) -> int:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "ppt/presentation.xml",
            "ppt/_rels/presentation.xml.rels",
        }
        errors.extend(f"Missing required part: {name}" for name in required - names)

        xml_parts = [n for n in names if n.endswith((".xml", ".rels"))]
        for name in xml_parts:
            try:
                ET.fromstring(archive.read(name))
            except ET.ParseError as exc:
                errors.append(f"Malformed XML in {name}: {exc}")

        for rels_name in (n for n in names if n.endswith(".rels")):
            try:
                root = ET.fromstring(archive.read(rels_name))
                source_part = source_part_for_rels(rels_name)
            except (ET.ParseError, ValueError):
                continue
            for rel in root.findall(f"{{{REL_NS}}}Relationship"):
                if rel.get("TargetMode") == "External":
                    continue
                target = rel.get("Target")
                if not target:
                    errors.append(f"Empty relationship target in {rels_name}")
                    continue
                resolved = resolve_target(source_part, target)
                if resolved not in names:
                    errors.append(f"Broken relationship: {rels_name} -> {resolved}")

        slides = sorted(
            n
            for n in names
            if n.startswith("ppt/slides/slide") and n.endswith(".xml")
        )
        shape_count = 0
        for slide_name in slides:
            root = ET.fromstring(archive.read(slide_name))
            shape_count += len(root.findall(f".//{{{P_NS}}}sp"))
            shape_count += len(root.findall(f".//{{{P_NS}}}cxnSp"))

    if errors:
        print(f"FAIL: {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"OK: {path} | slides={len(slides)} | editable_shapes={shape_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    if not args.pptx.is_file():
        print(f"File not found: {args.pptx}", file=sys.stderr)
        return 2
    if not zipfile.is_zipfile(args.pptx):
        print(f"Not a valid ZIP/PPTX package: {args.pptx}", file=sys.stderr)
        return 2
    return validate(args.pptx)


if __name__ == "__main__":
    raise SystemExit(main())
