cat > smoke_reports/result_receipts/blocked_result.json <<'JSON'
{
  "test_result_receipt_version": "1.0",
  "created_at_utc": "2026-01-01T00:00:00Z",
  "result_status": "COMPLETED",
  "result_summary": "This malformed result should fail closed.",
  "bounded_result_only": false,
  "ready_for_return": false,
  "return_to_submitter": false
}
JSON
