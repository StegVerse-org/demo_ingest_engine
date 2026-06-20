import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_ingestion_receipt.py"
VALIDATOR = ROOT / "scripts" / "validate_ingestion_receipts.py"
PREVIOUS = ROOT / "examples" / "previous_receipts_outbound.json"
DATASET_HASH = "sha256:0000000000000000000000000000000000000000000000000000000000000000"


def test_generator_emits_valid_outbound_receipt(tmp_path):
    output = tmp_path / "generated_outbound.json"
    result = subprocess.run([
        sys.executable,
        str(GENERATOR),
        "--step-id", "stegverse_org_ingestion_outbound",
        "--dataset-manifest-hash", DATASET_HASH,
        "--previous-receipts", str(PREVIOUS),
        "--output", str(output),
    ], cwd=ROOT, text=True, capture_output=True, check=False)

    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["step_id"] == "stegverse_org_ingestion_outbound"
    assert receipt["master_records"]["action_receipt_sent"] is True

    checked = subprocess.run([
        sys.executable,
        str(VALIDATOR),
        str(output),
    ], cwd=ROOT, text=True, capture_output=True, check=False)

    assert checked.returncode == 0, checked.stderr
