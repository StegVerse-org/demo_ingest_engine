python scripts/run_org_ingestion_step.py \
  --step-id stegverse_org_ingestion_outbound \
  --dataset-manifest-hash sha256:0000000000000000000000000000000000000000000000000000000000000000 \
  --previous-receipts examples/previous_receipts_outbound.json \
  --output /tmp/runner_outbound.json
python scripts/validate_ingestion_receipts.py /tmp/runner_outbound.json
