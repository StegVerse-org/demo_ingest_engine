import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_org_ingestion_step.py"
PREVIOUS = ROOT / "examples" / "previous_receipts_outbound.json"
DATASET_HASH = "sha256:0000000000000000000000000000000000000000000000000000000000000000"


def test_runner_generates_gated_outbound_receipt(tmp_path):
    output = tmp_path / "outbound.json"
    result = subprocess.run([
        sys.executable, str(RUNNER),
        "--step-id", "stegverse_org_ingestion_outbound",
        "--dataset-manifest-hash", DATASET_HASH,
        "--previous-receipts", str(PREVIOUS),
        "--output", str(output),
    ], cwd=ROOT / "scripts", text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert receipt["step_id"] == "stegverse_org_ingestion_outbound"
    assert receipt["master_records"]["action_receipt_sent"] is True
