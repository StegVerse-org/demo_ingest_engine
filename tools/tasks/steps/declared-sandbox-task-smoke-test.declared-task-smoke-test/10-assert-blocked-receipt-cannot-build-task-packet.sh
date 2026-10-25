set +e
python tools/build_stegghost_task_packet.py \
  --receipt smoke_reports/manifest_receipts/blocked/latest_declared_task_manifest_receipt.json \
  --out-dir smoke_reports/stegghost_dispatch/blocked
status=$?
set -e
if [ "$status" -eq 0 ]; then
  echo "::error::Blocked receipt produced a task packet."
  exit 1
fi
