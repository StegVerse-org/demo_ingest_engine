mkdir -p smoke_reports/declared_tasks smoke_reports/manifest_receipts smoke_reports/stegghost_dispatch
cat > smoke_reports/declared_tasks/admissible_manifest.json <<'JSON'
{
  "schema": "stegverse.declared_sandbox_test_task.v1",
  "task_type": "sandbox_test",
  "requested_mode": "test",
  "submitter": {
    "interface": "StegVerse-org LLM adapter",
    "submitter_type": "llm",
    "submitter_ref": "smoke-test"
  },
  "target": {
    "recipient": "StegGhost ingestion",
    "sandbox_only": true
  },
  "test": {
    "name": "smoke_declared_task_validation",
    "input_ref": "smoke_reports/declared_tasks/admissible_manifest.json",
    "expected_output": "bounded_result_receipt"
  },
  "boundary": {
    "sandbox_only": true,
    "return_result_only": true,
    "conversation_loop_allowed": false,
    "human_review_required": false,
    "install_authority": false,
    "execution_authority_outside_sandbox": false,
    "repository_mutation_allowed": false
  }
}
JSON
