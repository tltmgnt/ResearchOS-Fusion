import hashlib
import json
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest

from researchos_fusion.lab import Ledger, evaluate


@pytest.fixture
def manifest(tmp_path):
    artifact = tmp_path / "measurements.json"
    artifact.write_text('{"energy_mev": 17.6}')
    document = {
        "schema_version": 1, "run_id": "synthetic-001", "claim": "Reference fixture matches",
        "scope": "Synthetic software test only", "operator": "operator-a",
        "artifacts": [{"id": "a1", "path": artifact.name, "source": "synthetic fixture",
                       "license": "Apache-2.0", "provenance_group": "internal",
                       "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}],
        "checks": [{"id": "check1", "artifact_id": "a1", "quantity": "reaction energy",
                    "unit": "MeV", "observed_key": "energy_mev", "expected": 17.6,
                    "absolute_tolerance": 0.01}],
        "reviews": [{"reviewer": "reviewer-b", "decision": "approve", "rationale": "Synthetic test"}],
    }
    path = tmp_path / "run.json"
    path.write_text(json.dumps(document))
    return path, document


def write_manifest(manifest):
    path, document = manifest
    path.write_text(json.dumps(document))
    return path


def test_round_trip_and_checkpoint(manifest, tmp_path):
    report = evaluate(manifest[0])
    assert report["status"] == "reviewed"
    assert report["checks"][0]["observed"] == 17.6
    ledger = Ledger(tmp_path / "runs.sqlite")
    record = ledger.append(report)
    assert ledger.verify(record["record_hash"])["records"] == 1
    with pytest.raises(ValueError, match="already recorded"):
        ledger.append(report)
    assert ledger.verify()["records"] == 1
    with pytest.raises(ValueError, match="checkpoint"):
        ledger.verify("0" * 64)


def test_artifact_tampering(manifest):
    (manifest[0].parent / "measurements.json").write_text('{"energy_mev": 20}')
    with pytest.raises(ValueError, match="hash mismatch"):
        evaluate(manifest[0])


@pytest.mark.parametrize("field,value", [
    ("expected", float("nan")), ("expected", float("inf")),
    ("absolute_tolerance", -1), ("expected", True),
    ("artifact_id", "missing"), ("observed_key", "missing"),
])
def test_invalid_checks(manifest, field, value):
    manifest[1]["checks"][0][field] = value
    with pytest.raises(ValueError):
        evaluate(write_manifest(manifest))


@pytest.mark.parametrize("reviews,status", [([], "pending_review"),
    ([{"reviewer": "b", "decision": "reject", "rationale": "needs work"}], "pending_review")])
def test_missing_or_negative_review(manifest, reviews, status):
    manifest[1]["reviews"] = reviews
    assert evaluate(write_manifest(manifest))["status"] == status


def test_failed_acceptance_cannot_be_reviewed(manifest):
    manifest[1]["checks"][0]["expected"] = 20
    assert evaluate(write_manifest(manifest))["status"] == "failed"


def test_operator_cannot_self_review(manifest):
    manifest[1]["reviews"][0]["reviewer"] = "operator-a"
    with pytest.raises(ValueError, match="distinct"):
        evaluate(write_manifest(manifest))


@pytest.mark.parametrize("path", ["../outside.json", "/etc/passwd"])
def test_path_escape(manifest, path):
    manifest[1]["artifacts"][0]["path"] = path
    with pytest.raises(ValueError, match="within"):
        evaluate(write_manifest(manifest))


def test_symlink_escape(manifest, tmp_path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.json"
    outside.write_text('{}')
    (tmp_path / "linked.json").symlink_to(outside)
    manifest[1]["artifacts"][0]["path"] = "linked.json"
    with pytest.raises(ValueError, match="within"):
        evaluate(write_manifest(manifest))


def test_duplicate_keys_rejected(manifest):
    manifest[0].write_text('{"run_id": "a", "run_id": "b"}')
    with pytest.raises(ValueError, match="Duplicate JSON"):
        evaluate(manifest[0])


@pytest.mark.parametrize("mutation", ["UPDATE runs SET payload = '{}' WHERE sequence = 1",
    "DELETE FROM runs WHERE sequence = 1", "UPDATE runs SET previous_hash = 'bad' WHERE sequence = 2"])
def test_ledger_corruption(manifest, tmp_path, mutation):
    ledger = Ledger(tmp_path / "runs.sqlite")
    report = evaluate(manifest[0])
    ledger.append(report)
    ledger.append({**report, "run_id": "second"})
    with sqlite3.connect(ledger.path) as connection:
        connection.execute(mutation)
    with pytest.raises(ValueError):
        ledger.verify()
    with pytest.raises(ValueError):
        ledger.append({**report, "run_id": "third"})


def test_concurrent_append(manifest, tmp_path):
    ledger = Ledger(tmp_path / "runs.sqlite")
    report = evaluate(manifest[0])
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda i: ledger.append({**report, "run_id": str(i)}), range(8)))
    assert len({r["record_hash"] for r in records}) == 8
    assert ledger.verify()["records"] == 8


def test_cli_exit_codes(manifest, tmp_path):
    command = [sys.executable, "-m", "researchos_fusion.cli", "lab-run", str(manifest[0]),
               "--ledger", str(tmp_path / "runs.sqlite")]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["payload"]["status"] == "reviewed"
    assert subprocess.run(command, capture_output=True).returncode == 2
    manifest[1]["run_id"] = "second"
    manifest[1]["checks"][0]["expected"] = 99
    write_manifest(manifest)
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)["payload"]["status"] == "failed"


@pytest.mark.parametrize("mutation", [
    lambda m: m.update(schema_version=True),
    lambda m: m.update(unexpected="typo"),
    lambda m: m.update(checks=[]),
    lambda m: m["checks"].append(m["checks"][0].copy()),
    lambda m: m["artifacts"].append(m["artifacts"][0].copy()),
    lambda m: m["reviews"].append(m["reviews"][0].copy()),
])
def test_manifest_contract(manifest, mutation):
    mutation(manifest[1])
    with pytest.raises(ValueError):
        evaluate(write_manifest(manifest))


def test_transaction_rolls_back(manifest, tmp_path):
    ledger = Ledger(tmp_path / "runs.sqlite")
    report = evaluate(manifest[0])
    first = ledger.append(report)
    with sqlite3.connect(ledger.path) as connection:
        connection.execute("CREATE TRIGGER reject_insert BEFORE INSERT ON runs BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
    with pytest.raises(sqlite3.IntegrityError):
        ledger.append({**report, "run_id": "second"})
    assert ledger.verify(first["record_hash"])["records"] == 1


def test_tail_truncation_detected_by_checkpoint(manifest, tmp_path):
    ledger = Ledger(tmp_path / "runs.sqlite")
    report = evaluate(manifest[0])
    ledger.append(report)
    second = ledger.append({**report, "run_id": "second"})
    with sqlite3.connect(ledger.path) as connection:
        connection.execute("DELETE FROM runs WHERE sequence = 2")
    with pytest.raises(ValueError, match="checkpoint"):
        ledger.verify(second["record_hash"])


@pytest.mark.parametrize("observed", [True, "17.6", None, float("nan")])
def test_non_numeric_measurement_rejected(manifest, observed):
    artifact = manifest[0].parent / "measurements.json"
    artifact.write_text(json.dumps({"energy_mev": observed}))
    manifest[1]["artifacts"][0]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        evaluate(write_manifest(manifest))
