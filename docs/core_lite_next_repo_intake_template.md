# Core-Lite Next Repo Intake Template

## Repository

```text
<owner>/<repo>
```

## Intake State

```text
DISCOVERED
```

## Required Admission Checks

```text
- repository_visible: <true|false>
- repository_archived: <true|false>
- push_or_admin_access: <true|false>
- purpose_declared: <true|false>
- active_workflow_surface_declared: <true|false>
```

## One-Sentence Purpose

```text
<state the bounded repo purpose here>
```

## Minimal Active Workflow Surface

```text
<workflow-1.yml>
<workflow-2.yml if required>
```

## Planned Bootstrap Files

```text
tools/verify_core_lite_workflows.py
.github/workflows/<repo-core-lite-smoke-test>.yml
docs/core_lite_status.md
README_CORE_LITE.md
```

## Promotion Path

```text
DISCOVERED
→ ROLLOUT_CANDIDATE
→ ACTIVE_PATH_IDENTIFIED
→ BASELINE_READY
→ ACTIVATION_PENDING
→ CORE_LITE_ACTIVE
```

## Stop Conditions

```text
- repository not visible
- repository access missing
- repository archived
- purpose cannot be bounded
- active workflow surface cannot be declared
```
