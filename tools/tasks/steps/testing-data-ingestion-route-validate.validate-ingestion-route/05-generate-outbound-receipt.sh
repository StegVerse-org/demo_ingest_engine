python scripts/generate_ingestion_receipt.py \
  --step-id stegverse_org_ingestion_outbound \
  --dataset-manifest-hash sha256:0000000000000000000000000000000000000000000000000000000000000000 \
  --previous-receipts examples/previous_receipts_outbound.json \
  --output /tmp/generated_outbound.json
python scripts/validate_ingestion_receipts.py /tmp/generated_outbound.json
