# ADR-002: Support URL-Based source_path

## Status
Accepted

## Context
The SDK Demo Test workflow triggers ingestion with artifact URLs, but the engine expected local file paths only.

## Decision
Add URL detection in the workflow:
- If `source_path` starts with `https://`, download to `incoming/remote_bundle.zip`
- Pass the local path to the CLI

## Consequences
- Remote bundles can be ingested without manual download
- CI-to-CI automation is enabled
- Local file paths continue to work unchanged
