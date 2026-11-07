"""Offline evidence collection. Recorded attestations do not verify identities."""
from __future__ import annotations

from contextlib import closing
import hashlib
import json
import math
import platform
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def keys(value: object, required: set[str], optional: set[str] = frozenset()) -> dict:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(f"Expected fields {sorted(required)}; optional {sorted(optional)}")
    return value


def number(value: object, label: str) -> float:
    try:
        finite = math.isfinite(value) if type(value) in (int, float) else False
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{label} must be a finite number")
    return value


def parse_json(data: str) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Invalid number: {value}")))


def load_json(path: Path) -> dict:
    return parse_json(path.read_text(encoding="utf-8"))


def evaluate(manifest_path: Path) -> dict:
    """Evaluate a manifest against declared tolerances and hash local artifacts.

    Paths are relative to the manifest and must remain within its directory.
    Checks express acceptance criteria, not independent physics validation.
    """
    manifest_path = Path(manifest_path).resolve()
    manifest = keys(load_json(manifest_path),
                    {"schema_version", "run_id", "claim", "scope", "operator", "artifacts", "checks", "reviews"})
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported manifest schema_version")
    for field in ("run_id", "claim", "scope", "operator"):
        text(manifest[field], field)
    for field in ("artifacts", "checks", "reviews"):
        if not isinstance(manifest[field], list):
            raise ValueError(f"{field} must be an array")
    if not manifest["artifacts"] or not manifest["checks"]:
        raise ValueError("At least one artifact and acceptance check are required")
    artifacts = []
    artifact_bytes = {}
    artifact_ids = set()
    for raw in manifest["artifacts"]:
        item = keys(raw, {"id", "path", "source", "license", "provenance_group", "sha256"})
        for field, value in item.items():
            text(value, field)
        if item["id"] in artifact_ids:
            raise ValueError("Duplicate artifact id")
        artifact_ids.add(item["id"])
        path = (manifest_path.parent / item["path"]).resolve()
        if not path.is_relative_to(manifest_path.parent) or not path.is_file():
            raise ValueError("Artifact must be a file within the manifest directory")
        data = path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if item["sha256"] != actual:
            raise ValueError(f"Artifact hash mismatch: {item['id']}")
        artifacts.append(dict(item))
        artifact_bytes[item["id"]] = data
    checks = []
    check_ids = set()
    for raw in manifest["checks"]:
        item = keys(raw, {"id", "artifact_id", "quantity", "unit", "observed_key", "expected", "absolute_tolerance"})
        for field in ("id", "artifact_id", "quantity", "unit", "observed_key"):
            text(item[field], field)
        if item["id"] in check_ids or item["artifact_id"] not in artifact_ids:
            raise ValueError("Duplicate check id or unknown artifact_id")
        check_ids.add(item["id"])
        measurements = parse_json(artifact_bytes[item["artifact_id"]].decode("utf-8"))
        if not isinstance(measurements, dict) or item["observed_key"] not in measurements:
            raise ValueError("observed_key must name a top-level JSON measurement")
        observed = number(measurements[item["observed_key"]], "observed")
        expected = number(item["expected"], "expected")
        tolerance = number(item["absolute_tolerance"], "absolute_tolerance")
        if tolerance < 0:
            raise ValueError("absolute_tolerance must be nonnegative")
        error = abs(observed - expected)
        if not math.isfinite(error):
            raise ValueError("Check error overflow")
        checks.append({**item, "observed": observed, "absolute_error": error, "passed": error <= tolerance})
    reviews = []
    reviewers = set()
    for raw in manifest["reviews"]:
        item = keys(raw, {"reviewer", "decision", "rationale"})
        for field in item:
            text(item[field], field)
        if item["decision"] not in ("approve", "reject"):
            raise ValueError("Review decision must be approve or reject")
        if item["reviewer"] == manifest["operator"] or item["reviewer"] in reviewers:
            raise ValueError("Reviewers must be distinct from operator and one another")
        reviewers.add(item["reviewer"])
        reviews.append(dict(item))
    passed = all(check["passed"] for check in checks)
    reviewed = bool(reviews) and all(item["decision"] == "approve" for item in reviews)
    return {"schema_version": SCHEMA_VERSION, "run_id": manifest["run_id"],
            "manifest_sha256": digest(manifest), "claim": manifest["claim"],
            "scope": manifest["scope"], "operator": manifest["operator"],
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "runtime": {"python": platform.python_version(), "package": "researchos-fusion", "version": "0.2.0"},
            "artifacts": artifacts, "checks": checks, "reviews": reviews,
            "acceptance_passed": passed, "review_recorded": reviewed,
            "status": "reviewed" if passed and reviewed else "pending_review" if passed else "failed",
            "limitations": ["Offline evaluation only; no equipment control or scientific certification.",
                            "Reference values and review identities are declared, not independently verified.",
                            "Artifact hashes bind bytes; they do not establish source independence."]}


class Ledger:
    """SQLite transactional append API with a hash chain.

    Detects modified records and internal deletions, not privileged rewrites or
    tail truncation without a separately retained head hash. Not a WORM store.
    """
    def __init__(self, path: Path):
        self.path = Path(path)

    def _connect(self):
        connection = sqlite3.connect(self.path, timeout=30)
        connection.execute("CREATE TABLE IF NOT EXISTS runs (sequence INTEGER PRIMARY KEY, run_id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL, previous_hash TEXT NOT NULL, record_hash TEXT NOT NULL)")
        return connection

    @staticmethod
    def _verify(connection) -> list[dict]:
        previous = "0" * 64
        records = []
        for expected, (sequence, run_id, payload, prior, recorded) in enumerate(connection.execute(
                "SELECT sequence, run_id, payload, previous_hash, record_hash FROM runs ORDER BY sequence"), 1):
            decoded = parse_json(payload)
            if not isinstance(decoded, dict):
                raise ValueError("Ledger payload must be an object")
            if (sequence != expected or prior != previous or decoded.get("run_id") != run_id
                    or digest({"sequence": sequence, "payload": decoded, "previous_hash": prior}) != recorded):
                raise ValueError("Ledger integrity check failed")
            records.append({"sequence": sequence, "payload": decoded, "previous_hash": prior, "record_hash": recorded})
            previous = recorded
        return records

    def append(self, report: dict) -> dict:
        with closing(self._connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            records = self._verify(connection)
            sequence = len(records) + 1
            previous = records[-1]["record_hash"] if records else "0" * 64
            record = {"sequence": sequence, "payload": report, "previous_hash": previous}
            record["record_hash"] = digest(record)
            if connection.execute("SELECT 1 FROM runs WHERE run_id = ?", (report["run_id"],)).fetchone():
                raise ValueError("Run id already recorded; use a new run id")
            connection.execute("INSERT INTO runs VALUES (?, ?, ?, ?, ?)",
                               (sequence, report["run_id"], canonical(report), previous, record["record_hash"]))
            return record

    def verify(self, expected_head: str | None = None) -> dict:
        if not self.path.is_file():
            raise ValueError("Ledger does not exist")
        with closing(self._connect()) as connection, connection:
            records = self._verify(connection)
        head = records[-1]["record_hash"] if records else "0" * 64
        if expected_head is not None and head != expected_head:
            raise ValueError("Ledger head does not match retained checkpoint")
        return {"records": len(records), "head_sha256": head, "integrity_passed": True}
