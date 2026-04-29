# StegVerse Demo Ingestion Engine — Architecture

## Overview

The Demo Ingestion Engine is a deterministic pipeline for installing StegVerse demo bundles with archival safety, reproducible change tracking, and governance enforcement.

## Core Components

### 1. Mutation Classifier
- Analyzes incoming bundles for mutation type
- Generates mutation receipts

### 2. Governance Engine
- Evaluates mutations against governance policy
- Produces authorization verdicts

### 3. Admissibility Engine
- GCAT/BCAT-based admissibility evaluation
- Transition analysis and boundary checks

### 4. Guardian Runtime
- Boundary enforcement for entities
- Shadow policy evaluation

### 5. Cross-Entity Coordination
- Multi-entity divergence/convergence analysis
- Interaction policy evaluation
- Event bus and ledger management

### 6. Verification & Replay
- Deterministic replay validation
- State graph verification
- Full system verification

## Data Flow

```
Incoming Bundle → Mutation Classify → Governance → Admissibility → Guardian → Install/Archive
                                      ↓
                              Cross-Entity Coordination (if multi-entity)
                                      ↓
                              Event Bus → Ledger → Provenance Chain
                                      ↓
                              Reports → Index → Publication Pack
```

## Directory Structure

```
demo_ingest_engine/
├── bundles/              # Incoming bundle storage
├── configs/              # Policy configurations
├── docs/
│   └── architecture/
│       └── ARCHITECTURE.md
│       └── decisions/    # ADRs
├── incoming/             # Staged bundles
├── reports/              # Generated reports
├── src/
│   └── ingest/           # Core engine modules
├── tests/                # Test suite
└── updated_targets/      # Post-install targets
```

## Governance Policies

- `governance_policy.json` — Authorization rules
- `admissibility_policy.json` — GCAT/BCAT thresholds
- `guardian_policy.json` — Boundary conditions
- `shadow_policy.json` — Scenario evaluation
- `adversarial_policy.json` — Adversarial test generation
- `stress_test_policy.json` — Load testing parameters
- `actuation_policy.json` — Deployment actuation rules

## Integration Points

- **SDK Demo Test workflow** — Triggers ingestion post-release
- **TV/TVC** — Ephemeral secret injection during install
- **GCAT-BCAT-Engine** — Receives approved installations
- **AaCT-E** — Audits complete provenance chain
- **StegDB** — Monitors all state transitions
