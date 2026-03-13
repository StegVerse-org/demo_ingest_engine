from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime
from .extract import extract_if_zip
from .config import ROOT
from .manifest import load_bundle_manifest, resolve_targets_from_manifest
from .orchestrator import resolve_targets, orchestrate_plan, orchestrate_install
from .report import write_json, write_markdown
from .policy_loader import load_policy
from .mutation_governance import evaluate_mutation
from .receipt import write_receipts

def parse_args():
    parser = argparse.ArgumentParser(description="StegVerse ingestion engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("source"); p.add_argument("--target", dest="target_repo", default=None); p.add_argument("--target-set", default=None)
    i = sub.add_parser("install")
    i.add_argument("source"); i.add_argument("--target", dest="target_repo", default=None); i.add_argument("--target-set", default=None); i.add_argument("--archive", action="store_true")
    o = sub.add_parser("orchestrate")
    o.add_argument("source"); o.add_argument("--target-set", default=None); o.add_argument("--archive", action="store_true")
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
    manifest = load_bundle_manifest(source_dir)

    target_repo = getattr(args, "target_repo", None)
    target_set = getattr(args, "target_set", None)
    if not target_repo and not target_set:
        resolved = resolve_targets_from_manifest(manifest)
        if isinstance(resolved, list):
            targets = resolved
        elif isinstance(resolved, dict) and resolved.get("target_set"):
            targets = resolve_targets(None, resolved["target_set"])
        else:
            targets = resolve_targets(None, "runtime_stack")
    else:
        targets = resolve_targets(target_repo, target_set)

    governance_receipt = None
    if args.cmd in {"install", "orchestrate"}:
        policy = load_policy()
        governance_receipt = evaluate_mutation(source_dir, source, targets, policy, manifest)
        write_json(reports_root / "governance_receipt.json", governance_receipt)
        if not governance_receipt["mutation_authorized"]:
            report = {
                "mode": args.cmd,
                "source": str(source),
                "conflict_mode": "archive-and-replace" if getattr(args, "archive", False) else "replace",
                "apply_mode": "artifact-only",
                "bundle_manifest": manifest,
                "governance_receipt": governance_receipt,
                "targets": [{"repo": t, "added": [], "replaced": [], "skipped": [], "archived": []} for t in targets],
            }
            write_json(reports_root / "ingestion_report.json", report)
            write_json(reports_root / "ingestion_plan.json", report)
            write_markdown(reports_root / "ingestion_report.md", report)
            write_receipts(reports_root, report, source, manifest, governance_receipt)
            print("Mutation denied by governance policy")
            print(f"Report: {reports_root / 'ingestion_report.md'}")
            raise SystemExit(2)

    if args.cmd == "plan":
        result_targets = orchestrate_plan(source_dir, targets, work_root)
        report = {"mode":"plan","source":str(source),"conflict_mode":"none","apply_mode":"preview","bundle_manifest":manifest,"targets":result_targets}
    else:
        archive = getattr(args, "archive", False) or bool(manifest and manifest.get("conflict_mode") == "archive-and-replace")
        result_targets = orchestrate_install(source_dir, targets, work_root, archive_root, archive)
        report = {"mode":args.cmd,"source":str(source),"conflict_mode":"archive-and-replace" if archive else "replace","apply_mode":"artifact-only","bundle_manifest":manifest,"governance_receipt":governance_receipt,"targets":result_targets}

    write_json(reports_root / "ingestion_report.json", report)
    write_json(reports_root / "ingestion_plan.json", report)
    write_markdown(reports_root / "ingestion_report.md", report)
    write_receipts(reports_root, report, source, manifest, governance_receipt)
    print("Ingestion complete")
    print(f"Report: {reports_root / 'ingestion_report.md'}")

if __name__ == "__main__":
    main()
