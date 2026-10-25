python tools/validate_declared_sandbox_task.py \
  --manifest smoke_reports/declared_tasks/admissible_manifest.json \
  --policy configs/stegghost_declared_task_policy.json \
  --out-dir smoke_reports/manifest_receipts/admissible \
  --receipt-path-file smoke_reports/admissible_receipt_path.txt
