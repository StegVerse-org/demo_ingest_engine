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
from .entity_runtime import resolve_entities, reports_root_for_entity

ROOT = Path(".").resolve()

def parse_args():
    parser = argparse.ArgumentParser(description="StegVerse ingestion engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan")
    p.add_argument("source")
    p.add_argument("--entity", default=None)
    p.add_argument("--all-entities", action="store_true")

    i = sub.add_parser("install")
    i.add_argument("source")
    i.add_argument("--entity", default=None)
    i.add_argument("--all-entities", action="store_true")

    return parser.parse_args()

def run_for_entity(source: Path, mode: str, entity_name: str):
    reports_root = reports_root_for_entity(ROOT, entity_name)
    reports_root.mkdir(parents=True, exist_ok=True)

    mutation_receipt = classify_mutation(source, mode)
    mutation_receipt["entity"] = entity_name
    write_mutation_receipt(reports_root, mutation_receipt)

    governance_policy = load_policy(ROOT / "configs" / "governance_policy.json")
    governance_receipt = evaluate_mutation(
        source, mode, governance_policy, mutation_type=mutation_receipt["mutation_type"]
    )
    governance_receipt["entity"] = entity_name
    write_governance_receipt(reports_root, governance_receipt)

    admissibility_policy = load_admissibility_policy(ROOT / "configs" / "admissibility_policy.json")
    transition_receipt, admissibility_receipt = evaluate_admissibility(
        source, mode, mutation_receipt["mutation_type"], admissibility_policy
    )
    transition_receipt["entity"] = entity_name
    admissibility_receipt["entity"] = entity_name
    write_admissibility_reports(reports_root, transition_receipt, admissibility_receipt)

    allowed = governance_receipt["authorized"] and admissibility_receipt["admissible"]

    report = {
        "entity": entity_name,
        "mode": mode,
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

    return {
        "entity": entity_name,
        "allowed": allowed,
        "verification_status": verification_result["status"],
    }

def main():
    args = parse_args()
    source = Path(args.source).resolve()

    entities = resolve_entities(ROOT, entity=getattr(args, "entity", None), all_entities=getattr(args, "all_entities", False))
    results = [run_for_entity(source, args.cmd, entity_name) for entity_name in entities]

    for result in results:
        if result["allowed"]:
            print(f"Entity {result['entity']}: Ingestion complete")
        else:
            print(f"Entity {result['entity']}: Ingestion denied by governance or admissibility policy")
        print(f"Entity {result['entity']}: Independent verification {result['verification_status']}")

if __name__ == "__main__":
    main()