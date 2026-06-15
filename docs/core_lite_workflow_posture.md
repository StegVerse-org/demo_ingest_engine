# Core-Lite Workflow Posture

This repository keeps only the active sandbox-testing workflow entry points in GitHub Actions.

## Active Workflows

```text
Declared Sandbox Task Smoke Test
Result Intake Smoke Test
```

These workflows verify the active sandbox-testing path:

```text
StegVerse-org SDK / LLM adapter
→ declared sandbox test manifest
→ manifest validation
→ route-only StegGhost task packet
→ StegGhost bounded result receipt
→ StegVerse-org result intake
→ delivery receipt
→ result ready for submitter
```

## Removed From Active Workflow Surface

The following workflows were removed from `.github/workflows/` because they are not part of the current active core-lite path:

```text
Receive StegGhost Sandbox Receipt
Experimental Governance Review Utility
```

The underlying tools may remain in the repository for future governance/entity work, but they are not active workflow entry points.

## Current Boundary

```text
No install authority
No outside-sandbox authority
No planning authority
No conversation loop
No repository mutation
Only bounded result return to submitter
```

## Future Work

Future governance-review utility work should be added only after an AI entity or governance actor requires that path. Until then, the active path remains declared test task in, bounded result out.
