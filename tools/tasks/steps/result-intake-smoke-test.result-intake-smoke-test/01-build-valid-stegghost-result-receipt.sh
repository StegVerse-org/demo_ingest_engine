mkdir -p smoke_reports/result_receipts smoke_reports/result_intake smoke_reports/result_delivery
cat > smoke_reports/result_receipts/valid_result.json <<'JSON'
{
  "test_result_receipt_version": "1.0",
  "created_at_utc": "2026-01-01T00:00:00Z",
  "intake_receipt_path": "sandbox_intake_receipts/latest_stegghost_sandbox_intake_receipt.json",
  "intake_receipt_sha256": "smoke",
  "test": {
    "name": "smoke_result_return",
    "input_ref": "smoke"
  },
  "submitter": {
    "interface": "StegVerse-org LLM adapter",
    "submitter_type": "llm",
    "submitter_ref": "smoke-test"
  },
  "result_status": "COMPLETED",
  "result_summary": "Smoke result is bounded and ready for return.",
  "bounded_result_only": true,
  "ready_for_return": true,
  "return_to_submitter": true
}
JSON
