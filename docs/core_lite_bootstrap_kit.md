# Core-Lite Bootstrap Kit

This kit defines the reusable files and checks for applying the core-lite workflow posture to ecosystem repositories.

## Reference implementations

```text
StegVerse-org/demo_ingest_engine
StegGhost/entity-sandbox-runner
StegVerse-org/demo-sandbox
```

## Required files

```text
tools/verify_core_lite_workflows.py
.github/workflows/<repo-core-lite-smoke-test>.yml
```

Note: workflow path is shown with the leading dot because this is the actual repository path.

## Required verifier behavior

```text
- declare allowed workflow filenames
- list actual workflow files
- fail if unexpected workflow files exist
- fail if required workflow files are missing
- write reports/core_lite/latest_status.txt
```

## Required workflow behavior

```text
- checkout repository
- run tools/verify_core_lite_workflows.py early
- upload reports/core_lite/ as an artifact
```

## Required status file

```text
reports/core_lite/latest_status.txt
```

Minimum fields:

```text
status=PASS|FAIL
allowed_workflows=<names>
actual_workflows=<names>
unexpected_workflows=<names>
missing_required_workflows=<names>
```

## Documentation files

Recommended:

```text
docs/core_lite_status.md
docs/core_lite_rollout_pattern.md
README_CORE_LITE.md
```

Optional for bridge repos:

```text
docs/active_sandbox_loop.md
docs/bridge_completion_receipt.md
docs/ecosystem_core_lite_rollout_index.md
```

## Bootstrap sequence

```text
1. Determine repo role.
2. Declare minimal active workflow set.
3. Add verifier.
4. Add posture smoke workflow.
5. Add status artifact upload.
6. Add documentation.
7. Remove or archive obsolete workflows.
8. Verify status=PASS.
```

## Current rollout state

```text
StegVerse-org/demo_ingest_engine: bridge source pattern
StegGhost/entity-sandbox-runner: bridge recipient pattern
StegVerse-org/demo-sandbox: first posture-only rollout target
```
