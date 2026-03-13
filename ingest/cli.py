from __future__ import annotations
import argparse
from pathlib import Path
from .receipt import write_receipts
from .state_graph import append_state
from .summary import write_summary
from .state_graph_visualization import write_state_graph_mermaid
from .governance_engine import load_policy, evaluate_mutation, write_governance_receipt
from .mutation_classifier import classify_mutation, write_mutation_receipt
from .verifier import verify_reports, write_verification_reports
from .admissibility_engine import (
    load_admissibility_policy,
    evaluate_admissibility,
    write_admissibility_reports,
)

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

    mutation_receipt = classify_mutation(source, args.cmd)
    write_mutation_receipt(reports_root, mutation_receipt)

    governance_policy = load_policy(ROOT / "configs" / "governance_policy.json")
    governance_receipt = evaluate_mutation(
        source, args.cmd, governance_policy, mutation_type=mutation_receipt["mutation_type"]
    )
    write_governance_receipt(reports_root, governance_receipt)

    admissibility_policy = load_admissibility_policy(ROOT / "configs" / "admissibility_policy.json")
    transition_receipt, admissibility_receipt = evaluate_admissibility(
        source, args.cmd, mutation_receipt["mutation_type"], admissibility_policy
    )
    write_admissibility_reports(reports_root, transition_receipt, admissibility_receipt)

    allowed = governance_receipt["authorized"] and admissibility_receipt["admissible"]

    report = {
        "mode": args.cmd,
        "source": str(source),
        "status": "authorized" if allowed else "denied",
        "mutation_receipt": mutation_receipt,
        "governance_receipt": governance_receipt,
        "transition_receipt": transition_receipt,
        "admissibility_receipt": admissibility_receipt,
    }

    receipt = write_receipts(reports_root, report, source)
    state_record = append_state(reports_root, receipt, report)
    write_summary(reports_root, receipt, state_record, report)
    write_state_graph_mermaid(reports_root)

    verification_result = verify_reports(reports_root)
    write_verification_reports(reports_root, verification_result)

    if allowed:
        print("Ingestion complete")
    else:
        print("Ingestion denied by governance or admissibility policy")

    print("Mutation receipt generated")
    print("Governance receipt generated")
    print("Transition receipt generated")
    print("Admissibility receipt generated")
    print("Execution receipts generated")
    print("State graph updated")
    print("Summary report generated")
    print("State graph visualization generated")
    print(f"Independent verification {verification_result['status']}")

if __name__ == "__main__":
    main()