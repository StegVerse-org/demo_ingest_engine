python - <<'PY'
import json
from pathlib import Path
packet = json.loads(Path('smoke_reports/stegghost_dispatch/admissible/latest_stegghost_task_packet.json').read_text())
assert packet['route_allowed'] is True, packet
assert packet['route_authority'] == 'route_only', packet
assert packet['recipient'] == 'StegGhost ingestion', packet
assert packet['result_receipt_required'] is True, packet
assert packet['return_result_to_submitter'] is True, packet
assert packet['install_authority'] is False, packet
assert packet['outside_sandbox_authority'] is False, packet
assert packet['planning_authority'] is False, packet
assert packet['conversation_loop_allowed'] is False, packet
assert packet['repository_mutation_allowed'] is False, packet
PY
