"""Compiled code headers and code staleness (architecture.md § 6)."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from lib import ROOT
from lib.specs import Spec, sha256

PIPELINE = ROOT / "pipeline"


def code_path(spec: Spec) -> Path | None:
    """Where a spec's compiled code lives, or None if its type has none."""
    if spec.type == "Indicator":
        return PIPELINE / "indicators" / f"{spec.id}.py"
    return None


@dataclass
class Header:
    spec: str | None
    spec_hash: str | None
    generated: dict | None
    verified: dict | None


def read_header(path: Path) -> Header:
    fields: dict = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^# (spec|spec_hash|generated|verified): (.+)$", line)
        if m:
            value = m.group(2).strip()
            fields[m.group(1)] = yaml.safe_load(value) if value.startswith("{") else value
        elif line and not line.startswith("#"):
            break
    return Header(fields.get("spec"), fields.get("spec_hash"), fields.get("generated"), fields.get("verified"))


def code_hash(path: Path) -> str:
    """Hash of the code without its `verified` line, so a review doesn't make results stale."""
    lines = [l for l in path.read_text().splitlines(keepends=True) if not l.startswith("# verified:")]
    return sha256("".join(lines).encode())


def code_status(spec: Spec) -> str:
    """'none' (type has no compiled code), 'missing', 'stale', 'unverified', or 'ok'."""
    path = code_path(spec)
    if path is None:
        return "none"
    if not path.exists():
        return "missing"
    header = read_header(path)
    if header.spec_hash != spec.hash:
        return "stale"
    if not header.verified:
        return "unverified"
    return "ok"
