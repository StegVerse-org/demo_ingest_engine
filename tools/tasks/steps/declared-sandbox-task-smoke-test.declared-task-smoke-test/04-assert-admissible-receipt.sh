python - <<'PY'
import json
from pathlib import Path
receipt = json.loads(Path('smoke_reports/manifest_receipts/admissible/latest_declared_task_manifest_receipt.json').read_text())
assert receipt['verdict'] == 'ADMISSIBLE_TEST_TASK', receipt
assert receipt['admissible'] is True, receipt
assert receipt['route_to_stegghost_ingestion'] is True, receipt
assert receipt['emit_result_receipt'] is True, receipt
assert receipt['return_result_to_submitter'] is True, receipt
assert receipt['install_authority'] is False, receipt
assert receipt['execution_authority_outside_sandbox'] is False, receipt
assert receipt['planning_authority'] is False, receipt
assert receipt['conversation_loop_allowed'] is False, receipt
PY
