# StegVerse Demo Ingestion Engine

![Run Ingestion](https://github.com/StegVerse-org/demo_ingest_engine/actions/workflows/run-ingest.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/StegVerse-org/demo_ingest_engine)

Release: v1.2.1  
Targets: stegverse-demo-suite, demo_suite_runner, demo_ingest_engine

Phone-first ingestion and orchestration engine for installing StegVerse demo bundles directly from GitHub Actions.

## New in this release

- **orchestrate mode** — plan all entities, install approved, cross-entity coordination
- **URL-based sources** — ingest from remote artifact URLs (SDK releases, CI artifacts)
- **manifest-aware bundles** — automatic target resolution from bundle manifests
- **plan mode** — preview mutations without applying changes
- **multi-repo orchestration** — coordinate across StegVerse org repos
- **per-target reports** — deterministic receipts, state chains, verification
- **updated target snapshots** — archival safety with rollback capability

## Quick Start

### Install

```bash
pip install -r requirements.txt
```

### Run locally

```bash
# Plan mode (preview only)
python -m ingest.cli plan incoming/bundle.zip

# Install mode (apply changes)
python -m ingest.cli install incoming/bundle.zip

# Orchestrate mode (plan + install + cross-entity coordination)
python -m ingest.cli orchestrate incoming/bundle.zip --all-entities
```

### Run from GitHub Actions

Trigger manually via workflow dispatch:
- **Mode**: `plan` | `install` | `orchestrate`
- **Source**: local path (`incoming/bundle.zip`) or URL (`https://...`)
- **Conflict**: `replace` | `archive`

## Architecture

```
Incoming Bundle → Mutation Classify → Governance → Admissibility → Guardian
                                      ↓
                              Cross-Entity Coordination (orchestrate mode)
                                      ↓
                              Event Bus → Ledger → Provenance Chain
                                      ↓
                              Reports → Index → Publication Pack
```

See [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) for full details.

## Integration

| Upstream | Trigger | Consumes |
|----------|---------|----------|
| StegVerse-SDK | Release tag (`v*`) | Wheel + sdist artifacts |
| StegVerse-org | Workflow dispatch | Any bundle URL |
| TV/TVC | Post-ingestion | Ephemeral secrets injection |
| GCAT-BCAT-Engine | Approved installs | Deployment verification |
| AaCT-E | Audit request | Full provenance chain |
| StegDB | State transitions | Monitoring + alerts |

## Reports

Each run produces 27+ deterministic reports:

| Report | Purpose |
|--------|---------|
| `execution_receipt.json` | Run authorization + bundle hash |
| `governance_receipt.json` | Policy evaluation verdict |
| `admissibility_receipt.json` | GCAT/BCAT threshold check |
| `guardian_receipt.json` | Boundary condition verdict |
| `shadow_policy_receipt.json` | Counterfactual scenario analysis |
| `state_0001.json` … `state_NNNN.json` | State chain progression |
| `state_chain.txt` | Human-readable state lineage |
| `verification_report.json` | 8-point integrity verification |
| `replay_verification.json` | Deterministic replay confirmation |
| `report_index.md` | Complete report inventory |

## License

MIT — see [LICENSE](LICENSE)
