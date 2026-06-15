# Active Cross-Repo Sandbox Loop

This document defines the active sandbox-testing loop between `StegVerse-org/demo_ingest_engine` and `StegGhost/entity-sandbox-runner`.

## Repositories

```text
StegVerse-org/demo_ingest_engine = authority boundary, task declaration, route packet builder, result intake, delivery receipt
StegGhost/entity-sandbox-runner = sandbox recipient, intake validation, bounded result receipt
```

## Active Flow

```text
StegVerse-org SDK / LLM adapter
→ declared sandbox test manifest
→ manifest validation
→ ADMISSIBLE_TEST_TASK or FAIL_CLOSED
→ route-only StegGhost task packet
→ StegGhost intake validation
→ ACCEPTED_FOR_SANDBOX_TEST or FAIL_CLOSED
→ bounded test result receipt
→ StegVerse-org result intake
→ ACCEPTED_FOR_DELIVERY or FAIL_CLOSED
→ delivery receipt
→ READY_FOR_SUBMITTER
```

## Active Org Workflows

```text
Declared Sandbox Task Smoke Test
Result Intake Smoke Test
```

## StegGhost Workflow

```text
StegGhost Core-Lite Smoke Test
```

## Org-Side Artifacts

```text
configs/stegghost_declared_task_policy.json
tools/validate_declared_sandbox_task.py
tools/build_stegghost_task_packet.py
tools/intake_stegghost_result_receipt.py
tools/build_delivery_receipt.py
```

## StegGhost-Side Artifacts

```text
tools/validate_stegghost_task_packet.py
tools/build_test_result_receipt.py
```

## Boundary Invariants

```text
No install authority
No outside-sandbox authority
No planning authority
No conversation loop
No repository mutation
Only bounded result return to submitter
```

## Fail-Closed Points

```text
Invalid declared manifest → FAIL_CLOSED
Blocked requested mode → FAIL_CLOSED
Non-route-only task packet → FAIL_CLOSED
Rejected StegGhost intake → no result receipt
Malformed result receipt → FAIL_CLOSED
Rejected Org result intake → no delivery receipt
```

## Non-Active / Future Paths

The old sandbox receipt receiver and experimental governance review workflow entry points were removed from `.github/workflows/` because they are not part of the active core-lite sandbox-testing loop.

The related tools may remain for future entity-governance work, but they must not be treated as current execution, planning, review, or install authority.
