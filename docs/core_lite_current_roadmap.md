# Core-Lite Current Roadmap

## Roadmap State

```text
FRAMEWORK_READY
READY_FOR_NEXT_REPO_ADMISSION
```

## Phase 1 — Bridge Foundation

Status: COMPLETE

```text
StegVerse-org/demo_ingest_engine
→ StegGhost/entity-sandbox-runner
→ StegVerse-org/demo_ingest_engine
```

Delivered:

```text
- declared sandbox task validation
- route-only StegGhost task packet
- StegGhost intake validation
- bounded test result receipt
- Org result intake
- fail-closed invalid path handling
```

## Phase 2 — Core-Lite Workflow Posture

Status: COMPLETE

Delivered:

```text
- minimal active workflow declarations
- workflow posture verifier
- reports/core_lite/latest_status.txt status artifact
- artifact upload pattern
- archived workflow stub rule
```

## Phase 3 — Rollout Framework

Status: COMPLETE

Delivered:

```text
- bootstrap kit
- rollout admission gate
- state machine
- queue status
- master index
- framework manifest
- activation seal
- operator handoff
- ready receipt
```

## Phase 4 — First Rollout Target

Status: ACTIVATION_PENDING

Target:

```text
StegVerse-org/demo-sandbox
```

Delivered:

```text
- baseline verifier
- posture smoke workflow
- core-lite status doc
- README addendum
- activation receipt
```

Remaining:

```text
- next workflow run reports PASS
- root README pointer added if connector filtering allows
```

## Phase 5 — Next Repository Admission

Status: WAITING_FOR_DISCOVERY

Entry condition:

```text
- repository is visible through connector access, or
- repository is explicitly named for review
```

Admission path:

```text
DISCOVERED
→ ROLLOUT_CANDIDATE
→ ACTIVE_PATH_IDENTIFIED
→ BASELINE_READY
→ ACTIVATION_PENDING
→ CORE_LITE_ACTIVE
```

## Current Next Action

```text
Promote demo-sandbox after workflow PASS, then admit the next visible or named repository through the admission gate.
```
