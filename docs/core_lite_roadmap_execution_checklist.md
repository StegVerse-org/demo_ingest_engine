# Core-Lite Roadmap Execution Checklist

## Current Execution Target

```text
StegVerse-org/demo-sandbox
```

## Promotion Checklist

To promote `demo-sandbox` from `ACTIVATION_PENDING` to `CORE_LITE_ACTIVE`:

```text
1. Confirm core-lite-posture-smoke-test.yml runs.
2. Confirm tools/verify_core_lite_workflows.py exits PASS.
3. Confirm reports/core_lite/latest_status.txt is generated.
4. Confirm reports/core_lite/ is uploaded as an artifact.
5. Update docs/core_lite_rollout_queue_status.md.
6. Update docs/ecosystem_core_lite_rollout_index.md.
7. Record CORE_LITE_ACTIVE state in the next receipt.
```

## Next Repository Admission Checklist

When another repository becomes visible or is explicitly named:

```text
1. Confirm connector visibility.
2. Confirm repository is not archived.
3. Confirm push or admin access.
4. State repository purpose in one sentence.
5. Inspect or safely initialize workflow surface.
6. Apply docs/core_lite_bootstrap_kit.md.
7. Record state using docs/core_lite_state_machine.md.
8. Update queue status.
```

## Stop Conditions

```text
- repository cannot be inspected
- repository purpose cannot be bounded
- active workflow surface cannot be declared
- connector access is missing
```
