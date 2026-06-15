# Ecosystem Core-Lite Rollout Index

This index identifies the files and checks that should be copied or adapted when applying the core-lite workflow posture to another ecosystem repository.

Canonical bootstrap kit:

```text
docs/core_lite_bootstrap_kit.md
```

## Source Pattern Repositories

```text
StegVerse-org/demo_ingest_engine
StegGhost/entity-sandbox-runner
```

## Required Repo Files

```text
tools/verify_core_lite_workflows.py
docs/core_lite_rollout_pattern.md
README.md active workflow badge section
```

## Optional Repo Files

```text
docs/active_sandbox_loop.md
docs/bridge_completion_receipt.md
docs/core_lite_workflow_posture.md
docs/core_lite_autonomous_progress.md
```

## Required Workflow Behavior

```text
1. Checkout repo.
2. Run tools/verify_core_lite_workflows.py early.
3. Continue only if verifier reports PASS.
4. Upload reports/core_lite/ as an artifact.
5. Upload any repo-specific smoke-test reports.
```

## Required Status Output

```text
reports/core_lite/latest_status.txt
```

The status file should include the repo-local equivalent of:

```text
status=PASS|FAIL
allowed_workflows=<workflow names>
actual_workflows=<workflow names>
unexpected_workflows=<workflow names>
missing_required_workflows=<workflow names>
```

If archived stubs are supported, also include:

```text
archived_workflow_stubs=<workflow names>
```

## Adoption Order

```text
1. Identify repo active path.
2. Identify minimal active workflow set.
3. Remove obsolete workflows where possible.
4. Convert non-deletable remnants to inert archived stubs if allowed.
5. Add verifier.
6. Add status artifact output.
7. Add README badge links only for active workflows.
8. Add active-path documentation.
9. Add completion receipt.
10. Run the remaining smoke workflow.
```

## Fail-Closed Rule

Any unexpected active workflow must fail the verifier.

Any missing required workflow must fail the verifier.

Archived stubs are historical residue only and must not define an active workflow.

## Candidate Next Repos

```text
StegVerse-org/demo_ingest_engine is complete enough to serve as the Org-side source pattern.
StegGhost/entity-sandbox-runner is complete enough to serve as the recipient-side source pattern.
Next candidate repos should be selected by active dependency on this bridge or workflow sprawl risk.
```

## First Rollout Target

```text
StegVerse-org/demo-sandbox
```

Selection basis:

```text
- same organization as the Org-side bridge repo
- adjacent to demo ingestion and sandbox bridge work
- public repository with admin and push access available
- suitable first target before applying the pattern to larger governance repos
```

Initial rollout goal:

```text
- inspect active workflow surface
- identify minimal active path
- add verifier/status output
- remove or archive unnecessary workflows
- add README/docs pointers only after active path is confirmed
```

Current rollout state:

```text
StegVerse-org/demo-sandbox: BASELINE_READY
```

Activation receipt:

```text
StegVerse-org/demo-sandbox/docs/core_lite_activation_receipt.md
```

Remaining activation work:

```text
- next workflow run reports PASS
- root README pointer added if connector filtering allows
```
