python - <<'PY'
import json
from pathlib import Path
receipt = json.loads(Path('smoke_reports/result_intake/blocked/latest_stegghost_result_intake_receipt.json').read_text())
assert receipt['verdict'] == 'FAIL_CLOSED', receipt
assert receipt['accepted'] is False, receipt
assert receipt['delivery_allowed'] is False, receipt
assert receipt['checks_failed'], receipt
PY
