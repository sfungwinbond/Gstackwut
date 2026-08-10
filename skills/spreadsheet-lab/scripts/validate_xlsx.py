#!/usr/bin/env python3

import argparse
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
SHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def validate(path: Path) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts = {"sheets": 0, "charts": 0, "formulas": 0}
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"not a valid ZIP package: {exc}"], counts

    with archive:
        names = set(archive.namelist())
        for required in ("[Content_Types].xml", "xl/workbook.xml"):
            if required not in names:
                errors.append(f"missing {required}")
        for name in sorted(names):
            if name.endswith((".xml", ".rels")):
                try:
                    root = ET.fromstring(archive.read(name))
                except ET.ParseError as exc:
                    errors.append(f"invalid XML {name}: {exc}")
                    continue
                if name == "xl/workbook.xml":
                    counts["sheets"] = len(root.findall(f".//{{{SHEET_NS}}}sheet"))
                if name.startswith("xl/worksheets/") and name.endswith(".xml"):
                    counts["formulas"] += len(root.findall(f".//{{{SHEET_NS}}}f"))
                if name.endswith(".rels"):
                    if name == "_rels/.rels":
                        base_dir = ""
                    elif "/_rels/" in name:
                        owner_dir, relationship_file = name.rsplit("/_rels/", 1)
                        owner_name = relationship_file.removesuffix(".rels")
                        base_dir = posixpath.dirname(posixpath.join(owner_dir, owner_name))
                    else:
                        base_dir = posixpath.dirname(name)
                    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
                        if rel.get("TargetMode") == "External":
                            continue
                        target = rel.get("Target", "")
                        resolved = posixpath.normpath(posixpath.join(base_dir, target)).lstrip("/")
                        if target and resolved not in names:
                            errors.append(f"broken relationship {name} -> {target}")
        counts["charts"] = sum(1 for name in names if name.startswith("xl/charts/chart") and name.endswith(".xml"))
    return errors, counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an XLSX package and summarize editable content.")
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    errors, counts = validate(args.workbook)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.workbook} | sheets={counts['sheets']} charts={counts['charts']} formulas={counts['formulas']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
