# Testing Data Ingestion Route

This repository represents the StegVerse-org ingestion surface in the corrected testing data loop.

## Correct Testing Data Loop

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ User
```

## StegVerse-org Ingestion Responsibilities

| Step | Responsibility | Required receipt |
|------|----------------|------------------|
| `stegverse_org_ingestion_outbound` | Accept SDK/LLM Adapter-bound test data and route it to StegGhost. | org outbound ingestion receipt |
| `stegverse_org_ingestion_return` | Accept StegGhost return-validated bounded result and prepare user delivery. | org return ingestion receipt |

Every StegVerse-org ingestion step must send its action receipt to `master-records`.

## Handoff Rule

StegVerse-org ingestion must not advance a testing data packet unless the previous step has a local receipt and a `master-records` action receipt.

Outbound handoff requires:

```text
human_input receipt
sdk_or_llm_adapter_intake receipt
matching master-records receipts for both completed steps
```

Return handoff requires:

```text
human_input receipt
sdk_or_llm_adapter_intake receipt
stegverse_org_ingestion_outbound receipt
stegghost_ingestion_cge_admission receipt
ephemeral_sandbox_batch receipt
stegghost_ingestion_cge_return_validation receipt
matching master-records receipts for all completed steps
```

## SDK Reference Artifacts

The canonical schemas and validator live in `StegVerse-org/StegVerse-SDK`:

```text
schemas/testing-data-loop.schema.json
schemas/testing-data-loop-handoff.schema.json
scripts/validate_formal_testing_route.py
examples/testing_data_loop.json
examples/testing_data_loop_handoff.json
```
