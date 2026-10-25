cat > smoke_reports/declared_tasks/blocked_manifest.json <<'JSON'
{
  "schema": "stegverse.declared_sandbox_test_task.v1",
  "task_type": "install",
  "requested_mode": "install",
  "submitter": {
    "interface": "StegVerse-org SDK",
    "submitter_type": "human",
    "submitter_ref": "smoke-test"
  },
  "target": {
    "recipient": "StegGhost ingestion",
    "sandbox_only": false
  },
  "test": {
    "name": "blocked_install_attempt",
    "input_ref": "smoke_reports/declared_tasks/blocked_manifest.json"
  },
  "boundary": {
    "sandbox_only": false,
    "return_result_only": false,
    "conversation_loop_allowed": true,
    "human_review_required": true,
    "install_authority": true,
    "execution_authority_outside_sandbox": true,
    "repository_mutation_allowed": true
  }
}
JSON
