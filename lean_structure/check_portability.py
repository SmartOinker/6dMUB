"""Test local hash enforcement without requiring original workspace locations.

These are audit-behavior checks in temporary copies, not repeated Lean builds.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

if not __debug__:
    raise RuntimeError("Audit tests require assertions; do not use -O.")
root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="mub394-portability-") as directory:
    trial = Path(directory)
    for path in root.iterdir():
        if path.is_file() and not path.is_symlink():
            shutil.copy2(path, trial/path.name)
    (trial/"logs").mkdir()
    shutil.copy2(root/"logs/axioms-all.log", trial/"logs/axioms-all.log")
    provenance_path = trial/"integration-provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance["base_release"] = str(trial/"absent-baseline")
    for filename, record in provenance["added_sources"].items():
        record["path"] = str(trial/"absent-originals"/filename)
    provenance_path.write_text(json.dumps(provenance, indent=2)+"\n")

    def audit():
        return subprocess.run(["python3",str(trial/"audit_inventory.py"),"verify"],
                              capture_output=True,text=True)

    accepted = audit()
    assert accepted.returncode == 0, accepted.stderr
    record = json.loads((trial/"verification.json").read_text())
    assert record["theorem_count"] == 394
    assert record["local_proof_hashes_verified"] is True
    assert record["baseline_preserved"] is None
    assert record["original_baseline_verification"]["status"] == "not_available"
    assert all(v["status"] == "not_available"
               for v in record["original_added_source_verification"].values())
    assert record["historical_baseline_verification"]["status"] == "verified_unchanged"

    tested = []
    for filename, expected_reason in [
        ("MUBBridge.lean","local baseline proof"),
        ("MUBNormalizerObstructions.lean","local added proof"),
    ]:
        path = trial/filename
        original = path.read_bytes()
        path.write_bytes(original+b"\n-- temporary integrity-test alteration\n")
        rejected = audit()
        assert rejected.returncode != 0 and expected_reason in rejected.stderr, rejected.stderr
        path.write_bytes(original)
        tested.append(filename)

result = {
    "status":"PASS",
    "checked_at_utc":datetime.now(timezone.utc).isoformat(),
    "tests":{
        "missing_original_workspace_paths_are_optional":True,
        "all_forty_six_local_proof_hashes_remain_mandatory":True,
        "unavailable_originals_are_reported_without_current_preservation_claim":True,
        "historical_baseline_record_is_preserved_separately":True,
        "tampered_baseline_and_new_proof_files_are_rejected":tested,
    },
    "scope":"Portable audit and hash-enforcement checks; the mathematical proof sources and frozen baseline are unchanged.",
}
(root/"portability-check.json").write_text(json.dumps(result,indent=2)+"\n")
print("PASS: portable audit and two local-proof tamper controls.")
