from __future__ import annotations
import argparse
from pathlib import Path
from .receipt import write_receipts
from .state_graph import append_state

ROOT = Path(".").resolve()

def parse_args():
    parser = argparse.ArgumentParser(description="StegVerse ingestion engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.add_argument("source")

    i = sub.add_parser("install")
    i.add_argument("source")

    return parser.parse_args()

def main():
    args = parse_args()
    source = Path(args.source).resolve()

    reports_root = ROOT / "reports"
    reports_root.mkdir(exist_ok=True)

    report = {
        "mode": args.cmd,
        "source": str(source),
        "status": "simulated"
    }

    receipt = write_receipts(reports_root, report, source)
    append_state(reports_root, receipt, report)

    print("Ingestion complete")
    print("Execution receipts generated")
    print("State graph updated")

if __name__ == "__main__":
    main()