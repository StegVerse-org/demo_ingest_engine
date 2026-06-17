# Core-Lite Status Manifest Receipt

## Machine-readable source

```text
docs/core_lite_status_manifest.json
```

## Human-readable status

```text
CORE_LITE_FRAMEWORK_READY
READY_FOR_NEXT_REPO_ADMISSION
```

## Current rollout queue

```text
StegVerse-org/demo_ingest_engine    CORE_LITE_ACTIVE
StegGhost/entity-sandbox-runner     CORE_LITE_ACTIVE
StegVerse-org/demo-sandbox          ACTIVATION_PENDING
NEXT_VISIBLE_OR_NAMED_REPOSITORY    WAITING_FOR_DISCOVERY
```

## Next required action

```text
Promote demo-sandbox after workflow PASS, then admit the next visible or explicitly named repository through the admission gate.
```

## Fail-closed conditions

```text
- repository_not_visible
- repository_access_missing
- repository_archived
- repo_purpose_unbounded
- active_workflow_surface_undeclared
```
