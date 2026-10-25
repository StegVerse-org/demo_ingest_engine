python - <<'PY'
import json
from pathlib import Path
receipt = json.loads(Path('smoke_reports/result_intake/valid/latest_stegghost_result_intake_receipt.json').read_text())
assert receipt['verdict'] == 'ACCEPTED_FOR_DELIVERY', receipt
assert receipt['accepted'] is True, receipt
assert receipt['delivery_allowed'] is True, receipt
assert receipt['bounded_result_only'] is True, receipt
assert receipt['ready_for_return'] is True, receipt
assert receipt['return_to_submitter'] is True, receipt
PY
