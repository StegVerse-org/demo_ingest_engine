from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime
from .extract import extract_if_zip
from .config import ROOT
from .orchestrator import resolve_targets, orchestrate_plan, orchestrate_install
from .report import write_json, write_markdown

def parse_args():
    parser = argparse.ArgumentParser(description="StegVerse ingestion engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("source"); p.add_argument("--target", dest="target_repo", default=None); p.add_argument("--target-set", default=None)
    i = sub.add_parser("install")
    i.add_argument("source"); i.add_argument("--target", dest="target_repo", default=None); i.add_argument("--target-set", default=None); i.add_argument("--archive", action="store_true")
    o = sub.add_parser("orchestrate")
    o.add_argument("source"); o.add_argument("--target-set", required=True); o.add_argument("--archive", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    stamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    staging_root = ROOT / "staging"
    work_root = ROOT / "updated_targets" / stamp
    archive_root = ROOT / "deprecated" / stamp
    reports_root = ROOT / "reports"
    source = Path(args.source).resolve()
    source_dir = extract_if_zip(source, staging_root)
    target_repo = getattr(args, "target_repo", None)
    target_set = getattr(args, "target_set", None)
    targets = resolve_targets(target_repo, target_set)

    if args.cmd == "plan":
        result_targets = orchestrate_plan(source_dir, targets, work_root)
        report = {"mode":"plan","source":str(source),"conflict_mode":"none","apply_mode":"preview","targets":result_targets}
    else:
        archive = getattr(args, "archive", False)
        result_targets = orchestrate_install(source_dir, targets, work_root, archive_root, archive)
        report = {"mode":args.cmd,"source":str(source),"conflict_mode":"archive-and-replace" if archive else "replace","apply_mode":"artifact-only","targets":result_targets}

    write_json(reports_root / "ingestion_report.json", report)
    write_json(reports_root / "ingestion_plan.json", report)
    write_markdown(reports_root / "ingestion_report.md", report)
    print("Ingestion complete")
    print(f"Report: {reports_root / 'ingestion_report.md'}")

if __name__ == "__main__":
    main()
