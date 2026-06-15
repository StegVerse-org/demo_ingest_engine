# Core-Lite Rollout Pattern

This document defines the reusable core-lite posture pattern established by the StegVerse-org to StegGhost sandbox-testing bridge.

## Purpose

The pattern reduces workflow sprawl while preserving deterministic verification.

Each repo should keep only the workflow entry points that prove the active path for that repo.

Everything else should be removed or archived as a non-active stub.

## Active Workflow Rule

```text
One repo should declare its required active workflows explicitly.
The verifier must fail if any unexpected workflow remains active.
The verifier must fail if a required workflow is missing.
The verifier must write a local status artifact.
```

## Status Artifact Rule

Each verifier should write:

```text
reports/core_lite/latest_status.txt
```

The file should include:

```text
status=PASS|FAIL
allowed_workflows=<comma-separated names>
actual_workflows=<comma-separated names>
unexpected_workflows=<comma-separated names>
missing_required_workflows=<comma-separated names>
```

For repos that allow archived workflow stubs, the file may also include:

```text
archived_workflow_stubs=<comma-separated names>
```

## Archived Stub Rule

If a legacy workflow file cannot be deleted immediately, it may remain only as an inert archived stub.

The first line must be:

```text
# core-lite archived workflow stub
```

A file with this marker must not contain runnable GitHub Actions syntax.

## Current Bridge Implementation

```text
StegVerse-org/demo_ingest_engine
- active workflows:
  - declared-sandbox-task-smoke-test.yml
  - result-intake-smoke-test.yml
- status artifact:
  - reports/core_lite/latest_status.txt

StegGhost/entity-sandbox-runner
- active workflow:
  - stegghost-task-packet-smoke-test.yml
- status artifact:
  - reports/core_lite/latest_status.txt
- archived stubs allowed only with marker
```

## Repo Adoption Checklist

```text
1. Identify the active path the repo is responsible for proving.
2. Declare the minimal allowed workflow set.
3. Add or update tools/verify_core_lite_workflows.py.
4. Make the verifier fail closed on unexpected active workflows.
5. Make the verifier write reports/core_lite/latest_status.txt.
6. Upload reports/core_lite/ as workflow artifacts.
7. Remove legacy workflow files where possible.
8. Convert non-deletable workflow remnants into archived stubs.
9. Add README badges only for active workflows.
10. Document the active path in docs/active_sandbox_loop.md or an equivalent repo-local file.
```

## Boundary Invariants

```text
No install authority unless explicitly declared as the active repo purpose.
No outside-sandbox authority for sandbox-testing paths.
No planning authority on bounded testing paths.
No conversation loop with sandbox experiments.
No repository mutation unless that mutation is the declared active path.
Only bounded result return to the authorized submitter or upstream boundary.
```

## Completion Criteria

A repo is core-lite complete when:

```text
- the active workflow set is minimal and declared
- verifier status is PASS
- status artifact is produced
- README reflects only active workflow badges
- docs describe the active path
- legacy workflows are removed or inert archived stubs
```
