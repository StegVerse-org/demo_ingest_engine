import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "gate_ingestion_handoff.py"
OUTBOUND_RECEIPT = ROOT / "examples" / "org_outbound_ingestion_receipt.json"
RETURN_RECEIPT = ROOT / "examples" / "org_return_ingestion_receipt.json"


def run_gate(receipt, next_step):
    return subprocess.run(
        [sys.executable, str(GATE), str(receipt), "--next-step", next_step],
        cwd=ROOT / "scripts",
        text=True,
        capture_output=True,
        check=False,
    )


def test_outbound_handoff_allows_stegghost_admission():
    result = run_gate(OUTBOUND_RECEIPT, "stegghost_ingestion_cge_admission")
    assert result.returncode == 0, result.stderr
    assert "ALLOW:" in result.stdout


def test_return_handoff_allows_human_delivery():
    result = run_gate(RETURN_RECEIPT, "human_delivery")
    assert result.returncode == 0, result.stderr
    assert "ALLOW:" in result.stdout


def test_outbound_handoff_denies_wrong_next_step():
    result = run_gate(OUTBOUND_RECEIPT, "human_delivery")
    assert result.returncode == 1
    assert "DENY:" in result.stderr
