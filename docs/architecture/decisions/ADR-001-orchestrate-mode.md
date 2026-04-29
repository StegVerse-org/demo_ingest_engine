# ADR-001: Add orchestrate Mode to CLI

## Status
Accepted

## Context
The `run-ingest.yml` workflow offered `orchestrate` as a mode choice, but the CLI (`cli.py`) only implemented `plan` and `install`. This created a mismatch where triggering `orchestrate` would fail with:
```
invalid choice: 'orchestrate' (choose from 'plan', 'install')
```

## Decision
Add `orchestrate` as a first-class CLI command that:
1. Runs `plan` for all detected entities
2. Runs `install` only for entities that pass governance/admissibility/guardian
3. Performs cross-entity coordination (divergence, convergence, interactions)
4. Generates a unified orchestration report

## Consequences
- Workflow YAML and CLI are now consistent
- Multi-entity deployments are automated
- Failed entities are skipped with clear logging
- Cross-entity analysis runs only when multiple entities exist
