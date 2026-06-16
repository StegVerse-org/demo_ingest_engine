# Core-Lite Operator Handoff

## Current Framework State

```text
CORE_LITE_FRAMEWORK_READY
```

## Current Queue

```text
StegVerse-org/demo_ingest_engine    CORE_LITE_ACTIVE
StegGhost/entity-sandbox-runner     CORE_LITE_ACTIVE
StegVerse-org/demo-sandbox          ACTIVATION_PENDING
Next repository                     WAITING_FOR_DISCOVERY
```

## Next Operator Action

When another repository becomes visible or is explicitly named, apply this sequence:

```text
1. Confirm repository access.
2. Confirm repository is not archived.
3. Identify the repo purpose in one sentence.
4. Identify minimal active workflow surface.
5. Apply docs/core_lite_bootstrap_kit.md.
6. Record state transition using docs/core_lite_state_machine.md.
7. Update docs/core_lite_rollout_queue_status.md.
```

## Do Not Proceed If

```text
- repository is not visible
- repository access is missing
- repo purpose cannot be stated
- active path cannot be bounded
```

## Canonical Entry Point

```text
docs/core_lite_master_index.md
```
