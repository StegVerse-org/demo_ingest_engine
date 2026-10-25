set +e
python tools/intake_stegghost_result_receipt.py \
  --result smoke_reports/result_receipts/blocked_result.json \
  --out-dir smoke_reports/result_intake/blocked \
  --intake-path-file smoke_reports/blocked_result_intake_path.txt
status=$?
set -e
if [ "$status" -eq 0 ]; then
  echo "::error::Blocked result receipt was accepted."
  exit 1
fi
