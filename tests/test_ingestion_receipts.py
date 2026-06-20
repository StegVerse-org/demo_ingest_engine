import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_ingestion_receipts.py"
OUTBOUND_RECEIPT = ROOT / "examples" / "org_outbound_ingestion_receipt.json"
RETURN_RECEIPT = ROOT / "examples" / "org_return_ingestion_receipt.json"


def run_validator(path):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_org_outbound_ingestion_receipt_is_valid():
    result = run_validator(OUTBOUND_RECEIPT)
    assert result.returncode == 0, result.stderr
    assert "PASS: ingestion receipt is valid" in result.stdout


def test_org_return_ingestion_receipt_is_valid():
    result = run_validator(RETURN_RECEIPT)
    assert result.returncode == 0, result.stderr
    assert "PASS: ingestion receipt is valid" in result.stdout
