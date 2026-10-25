python - <<'PY'
import json
from pathlib import Path
receipt = json.loads(Path('smoke_reports/result_delivery/valid/latest_delivery_receipt.json').read_text())
assert receipt['delivery_status'] == 'READY_FOR_SUBMITTER', receipt
assert receipt['bounded_result_only'] is True, receipt
assert receipt['return_to_submitter'] is True, receipt
assert receipt['result_sha256'], receipt
PY
