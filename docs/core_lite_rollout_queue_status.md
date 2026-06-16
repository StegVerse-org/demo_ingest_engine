# Core-Lite Rollout Queue Status

## Queue Snapshot

```text
StegVerse-org/demo_ingest_engine    CORE_LITE_ACTIVE
StegGhost/entity-sandbox-runner     CORE_LITE_ACTIVE
StegVerse-org/demo-sandbox          ACTIVATION_PENDING
Next repository                     WAITING_FOR_DISCOVERY
```

## Promotion Rules

```text
BASELINE_READY -> ACTIVATION_PENDING
  requires:
  - verifier present
  - posture workflow present
  - status artifact declared
  - activation receipt exists

ACTIVATION_PENDING -> CORE_LITE_ACTIVE
  requires:
  - workflow execution reports PASS
  - reports/core_lite artifact emitted
```

## Current Blockers

```text
- connector currently exposes only demo-sandbox as the next rollout target
- root README updates may be deferred if connector filtering blocks edits
```
