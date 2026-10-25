set +e
python tools/build_delivery_receipt.py \
  --intake smoke_reports/result_intake/blocked/latest_stegghost_result_intake_receipt.json \
  --out-dir smoke_reports/result_delivery/blocked
status=$?
set -e
if [ "$status" -eq 0 ]; then
  echo "::error::Blocked intake produced delivery receipt."
  exit 1
fi
