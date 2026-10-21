"""Fetch data into snapshots, and hash local files (architecture.md § 10).

All computation reads snapshots, never a live source. A snapshot is saved once per
request in data/raw/<source>/<request-hash>/ with a snapshot.yaml; refreshing means
deleting that folder on purpose so the next run fetches it again.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import requests
import yaml

from lib import ROOT
from lib.specs import file_hash, sha256

RAW = ROOT / "data" / "raw"


@dataclass
class Snapshot:
    source: str          # Resource or Geography ID
    request: str         # human-readable description of the request
    path: Path           # the data file
    hash: str
    retrieved: str | None
    url: str | None      # key removed

    def record(self) -> dict:
        out = {"source": self.source, "request": self.request,
               "path": str(self.path.relative_to(ROOT)), "hash": self.hash}
        if self.retrieved:
            out["retrieved"] = self.retrieved
        return out


def request_hash(request: dict) -> str:
    return sha256(json.dumps(request, sort_keys=True).encode()).split(":")[1][:16]


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _read(folder: Path, source: str) -> Snapshot | None:
    meta_path = folder / "snapshot.yaml"
    if not meta_path.exists():
        return None
    meta = yaml.safe_load(meta_path.read_text())
    path = folder / meta["file"]
    if file_hash(path) != meta["hash"]:
        raise RuntimeError(f"snapshot {folder} does not match its recorded hash; delete it and fetch again")
    return Snapshot(source, meta["request"], path, meta["hash"], meta["retrieved"], meta["url"])


def _write(folder: Path, source: str, request: str, url: str, filename: str, content: bytes) -> Snapshot:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(content)
    meta = {"source": source, "request": request, "url": url, "retrieved": _now(),
            "file": filename, "hash": file_hash(path)}
    (folder / "snapshot.yaml").write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True))
    return Snapshot(source, request, path, meta["hash"], meta["retrieved"], url)


def url_file(source: str, url: str) -> Snapshot:
    """A whole file at a fixed URL (e.g. a boundary file), fetched once."""
    folder = RAW / source / request_hash({"url": url})
    snap = _read(folder, source)
    if snap:
        return snap
    print(f"fetching {url}")
    r = requests.get(url, timeout=300)
    r.raise_for_status()
    return _write(folder, source, f"file {url}", url, Path(urlsplit(url).path).name, r.content)


def local_file(source: str, path: str) -> Snapshot:
    """A local file, hashed in place (not copied)."""
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"{source}: local file {path} not found")
    return Snapshot(source, f"local file {path}", p, file_hash(p), None, None)


def census_api(resource: dict, dataset: str, vintage: int, fields: list[str],
               for_: str, in_: list[str]) -> Snapshot:
    """One Census Data API request. The key comes from .env by the variable name in `auth`."""
    request = {"dataset": dataset, "vintage": vintage, "fields": fields, "for": for_, "in": in_}
    folder = RAW / "census_api" / request_hash(request)
    desc = f"{dataset} {vintage} · {', '.join(fields)} · for {for_} in {' '.join(in_)}"
    snap = _read(folder, "census_api")
    if snap:
        return snap
    if len(fields) > 50:
        raise ValueError("Census API allows at most 50 fields per request")
    base = f"{resource['resource']}/{vintage}/{dataset}"
    params = [("get", ",".join(fields)), ("for", for_)] + [("in", i) for i in in_]
    public_url = requests.Request("GET", base, params=params).prepare().url
    key = _env(resource.get("auth"))
    print(f"fetching {public_url}")
    r = requests.get(base, params=params + ([("key", key)] if key else []), timeout=120)
    if r.status_code != 200:
        # Never echo the request URL here: it contains the key.
        raise RuntimeError(f"Census API returned HTTP {r.status_code} for {public_url}: {r.text[:300]}")
    return _write(folder, "census_api", desc, public_url, "data.json", r.content)


def _env(name: str | None) -> str | None:
    if not name:
        return None
    if name in os.environ:
        return os.environ[name]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            k, _, v = line.partition("=")
            if k.strip() == name:
                return v.strip()
    raise RuntimeError(f".env has no {name}")
