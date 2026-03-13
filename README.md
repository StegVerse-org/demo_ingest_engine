# StegVerse Demo Ingestion Engine

Phone‑first ingestion system for installing StegVerse bundle updates into:

• stegverse-demo-suite  
• demo_suite_runner  

This repo supports **GitHub‑workflow driven installs**, meaning you can upload
bundles from an iPhone and run ingestion directly from the Actions tab.

## Workflow Use (Recommended)

1. Upload bundle to:

```
incoming/
```

2. Open **Actions → Run Ingestion**

3. Select:

```
target_repo
source_type
source_path
conflict_mode
```

4. Run workflow

Outputs:

• ingestion report  
• updated repo snapshot  
• deprecated archive (if used)

Artifacts appear in the workflow run.

## CLI (optional)

```
python ingest/cli.py install bundle.zip --target ../stegverse-demo-suite --archive
```

## Structure

```
incoming/           uploaded bundles
staging/            temporary extraction
reports/            ingestion reports
deprecated/         archived replaced files
updated_targets/    final repo snapshot
```

This engine removes manual file movement entirely.
