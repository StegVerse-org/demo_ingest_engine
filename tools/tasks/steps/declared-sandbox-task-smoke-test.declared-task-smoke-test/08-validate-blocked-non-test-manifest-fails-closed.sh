set +e
python tools/validate_declared_sandbox_task.py \
  --manifest smoke_reports/declared_tasks/blocked_manifest.json \
  --policy configs/stegghost_declared_task_policy.json \
  --out-dir smoke_reports/manifest_receipts/blocked \
  --receipt-path-file smoke_reports/blocked_receipt_path.txt
status=$?
set -e
if [ "$status" -eq 0 ]; then
  echo "::error::Blocked manifest was accepted."
  exit 1
fi
