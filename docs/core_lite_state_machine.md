# Core-Lite State Machine

## Purpose

This document defines the canonical lifecycle for repositories entering the Core-Lite rollout program.

## State Flow

```text
DISCOVERED
  ↓
ROLLOUT_CANDIDATE
  ↓
ACTIVE_PATH_IDENTIFIED
  ↓
BASELINE_READY
  ↓
ACTIVATION_PENDING
  ↓
CORE_LITE_ACTIVE
```

## Transition Rules

```text
DISCOVERED -> ROLLOUT_CANDIDATE
  requires connector visibility and repository access.

ROLLOUT_CANDIDATE -> ACTIVE_PATH_IDENTIFIED
  requires a declared minimal purpose and workflow surface.

ACTIVE_PATH_IDENTIFIED -> BASELINE_READY
  requires verifier, posture workflow, status artifact, and baseline docs.

BASELINE_READY -> ACTIVATION_PENDING
  requires activation receipt and rollout queue entry.

ACTIVATION_PENDING -> CORE_LITE_ACTIVE
  requires a successful workflow run and artifact emission.
```

## Fail-Closed Behavior

A repository remains in its current state if any required transition condition is not satisfied.

No repository may skip states.
