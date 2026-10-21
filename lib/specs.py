"""Load specs and build the dependency graph (architecture.md §§ 3, 5)."""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from lib import ROOT

SPECS = ROOT / "specs"

FOLDERS = {
    "Resource": "resources",
    "Geography": "geographies",
    "Crosswalk": "crosswalks",
    "Indicator": "indicators",
    "Visualization": "visualizations",
}

# Frontmatter fields that point to other specs, and the type each must point to.
REFS = {
    "Resource": {},
    "Geography": {"within": "Geography"},
    "Crosswalk": {"from": "Geography", "to": "Geography", "weights_source": "Resource"},
    "Indicator": {"geography": "Geography", "crosswalks": "Crosswalk",
                  "data[].resource": "Resource", "builds_on": "Indicator"},
    "Visualization": {"indicator": "Indicator", "geography": "Geography", "also_show": "Indicator"},
}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


@dataclass
class Spec:
    id: str
    path: Path
    meta: dict
    body: str
    text: str

    @property
    def type(self) -> str:
        return self.meta.get("type")

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(ROOT))

    @property
    def hash(self) -> str:
        """Whole file except `status`: used for specs with compiled code.
        `status` is approval, not content, so approving a spec doesn't make its code stale."""
        return sha256(re.sub(r"^status:.*\n", "", self.text, count=1, flags=re.M).encode())

    @property
    def meta_hash(self) -> str:
        """Frontmatter except `status`: used for specs without compiled code."""
        meta = {k: v for k, v in self.meta.items() if k != "status"}
        return sha256(json.dumps(meta, sort_keys=True, default=str).encode())

    def sections(self) -> set[str]:
        return {m.strip() for m in re.findall(r"^# (.+)$", self.body, re.M)}

    def refs(self) -> list[tuple[str, str, str]]:
        """(field, referenced id, expected type) for every reference field."""
        out = []
        for field, want in REFS.get(self.type, {}).items():
            if field == "data[].resource":
                for entry in self.meta.get("data") or []:
                    if isinstance(entry, dict) and entry.get("resource"):
                        out.append((field, entry["resource"], want))
                continue
            val = self.meta.get(field)
            for v in (val if isinstance(val, list) else [val] if val else []):
                out.append((field, v, want))
        return out


def load_all() -> dict[str, Spec]:
    """Every spec in specs/, keyed by ID. Duplicate IDs are kept under a list for the validator."""
    specs: dict[str, Spec] = {}
    for path in sorted(SPECS.rglob("*.md")):
        if path.name == "index.md":
            continue
        text = path.read_text()
        meta, body = split_frontmatter(text)
        spec = Spec(path.stem, path, meta if isinstance(meta, dict) else {}, body, text)
        if spec.id in specs:
            spec.id = f"{spec.id}#dup:{spec.rel}"
        specs[spec.id] = spec
    return specs


def dependencies(spec: Spec, specs: dict[str, Spec]) -> list[Spec]:
    """All specs below `spec` in the graph, bottom first (build order), excluding `spec`."""
    order: list[Spec] = []
    seen: set[str] = set()

    def visit(s: Spec, stack: tuple[str, ...]):
        for _, ref, _ in s.refs():
            if ref in stack:
                raise ValueError(f"loop in spec graph: {' → '.join(stack + (ref,))}")
            if ref in specs and ref not in seen:
                visit(specs[ref], stack + (ref,))
                seen.add(ref)
                order.append(specs[ref])

    visit(spec, (spec.id,))
    return order


def dependents(spec_id: str, specs: dict[str, Spec]) -> list[str]:
    """IDs of all specs above `spec_id` in the graph."""
    out = []
    for s in specs.values():
        try:
            if any(d.id == spec_id for d in dependencies(s, specs)):
                out.append(s.id)
        except ValueError:
            pass
    return out
