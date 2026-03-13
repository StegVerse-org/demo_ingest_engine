from __future__ import annotations
import argparse
from pathlib import Path
from .receipt import write_receipts
from .state_graph import append_state
from .summary import write_summary
from .state_graph_visualization import write_state_graph_mermaid

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
    state_record = append_state(reports_root, receipt, report)
    write_summary(reports_root, receipt, state_record, report)
    write_state_graph_mermaid(reports_root)

    print("Ingestion complete")
    print("Execution receipts generated")
    print("State graph updated")
    print("Summary report generated")
    print("State graph visualization generated")

if __name__ == "__main__":
    main()