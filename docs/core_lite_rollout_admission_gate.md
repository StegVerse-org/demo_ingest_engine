# Core-Lite Rollout Admission Gate

This document defines when a repository may enter the ecosystem core-lite rollout queue.

Related lifecycle document:

```text
docs/core_lite_state_machine.md
```

## Purpose

Repository migration must be declared and bounded. A repo should not be modified merely because it exists. It must first pass an admission gate.

## Required admission criteria

```text
- repository is visible through connector access
- repository is not archived
- push or admin access is available
- active workflow surface can be inspected or safely initialized
- repo purpose can be stated in one sentence
```

## Preferred admission criteria

```text
- repository participates in an existing bridge, ingestion, sandbox, or governance path
- repository has workflow sprawl or unclear workflow posture
- repository has README or docs that can receive a posture pointer
- repository is small enough to serve as a safe rollout target before larger repos
```

## Admission states

```text
DISCOVERED
ROLLOUT_CANDIDATE
ACTIVE_PATH_IDENTIFIED
BASELINE_READY
ACTIVATION_PENDING
CORE_LITE_ACTIVE
BLOCKED
```

## State definitions

```text
DISCOVERED = repo is visible through connector access
ROLLOUT_CANDIDATE = repo appears relevant to the rollout queue
ACTIVE_PATH_IDENTIFIED = minimal active purpose and workflow set are declared
BASELINE_READY = verifier, workflow, status artifact, and docs exist
ACTIVATION_PENDING = next workflow run must confirm PASS
CORE_LITE_ACTIVE = verifier status is PASS and artifacts are emitted
BLOCKED = required access, visibility, or purpose is missing
```

## Current queue

```text
StegVerse-org/demo_ingest_engine: CORE_LITE_ACTIVE
StegGhost/entity-sandbox-runner: CORE_LITE_ACTIVE
StegVerse-org/demo-sandbox: BASELINE_READY / ACTIVATION_PENDING
Next repository: WAITING_FOR_DISCOVERY
```

## Fail-closed rule

If a repository cannot be inspected, cannot be accessed, or cannot state a minimal active path, it must not enter the rollout queue.

## Next expansion rule

The next repository should be admitted only after it becomes visible through connector access or is explicitly named for review.
