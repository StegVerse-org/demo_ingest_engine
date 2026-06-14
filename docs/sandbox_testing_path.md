# Active Sandbox Testing Path

This document defines the current active purpose of the StegVerse-org to StegGhost sandbox path.

## Purpose

The active path is not a human review loop.

The active path is a bounded sandbox-testing loop:

```text
StegVerse-org SDK
or StegVerse-org LLM adapter
→ declared task packet
→ declared test manifest
→ manifest admissibility check
→ StegGhost ingestion
→ sandbox test processing
→ bounded test result receipt
→ result returned to the submitter through the StegVerse-org boundary
```

## Actor Roles

```text
StegVerse-org SDK / LLM adapter = submission interface
StegVerse-org = manifest validation, policy boundary, routing authority
StegGhost ingestion = recipient of admissible declared test tasks
StegGhost sandbox = bounded experiment processor
StegVerse-org = result receipt intake and return boundary
User or LLM = submitter who receives the result
```

## Manifest Rule

Only declared manifests that match the active sandbox test-task form are admissible.

```text
if manifest declares an admissible sandbox test task:
    route to StegGhost ingestion
else:
    FAIL_CLOSED
```

A manifest that declares install, execution outside the sandbox, repository mutation, governance review, planning, or conversational back-and-forth is not admissible on this path.

## Human Review Boundary

The submitter does not participate in a conversational review loop with the sandbox experiment.

The only human- or LLM-facing output for this path is the result of the submitted test.

```text
No back-and-forth with sandbox experiments.
No human override path.
No planning authority.
No install authority.
No execution authority outside the declared sandbox test process.
```

## Future Governance Review Utility

A governance-review utility may become useful after this part of the ecosystem has an AI entity with behavior that requires governance classification, escalation posture, or exception review.

That future utility is not part of the current active sandbox-testing path.

The existing review receipt workflow is therefore treated as experimental/future-governance infrastructure unless explicitly connected to a future AI entity governance path.

## Current Active Artifacts

Forward path artifacts should use names such as:

```text
declared_tasks/
manifest_receipts/
stegghost_dispatch/
```

Return path artifacts should use names such as:

```text
result_receipts/
result_delivery/
```

Review path artifacts should remain separate:

```text
review_receipts/
```

They must not be used to imply current planning authority for the sandbox-testing path.
