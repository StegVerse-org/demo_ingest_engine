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
from .admissibility_engine import load_admissibility_policy, evaluate_admissibility, write_admissibility_reports
from .entity_runtime import resolve_entities, reports_root_for_entity
from .cross_entity_compare import compare_entities, write_comparison_reports
from .replay import replay_reports, write_replay_reports
from .convergence import analyze_convergence, write_convergence_reports
from .perturbation import apply_perturbation, write_perturbation_receipt
from .recovery import apply_recovery, write_recovery_receipt
from .wall_control import evaluate_interactions, write_interaction_reports
from .event_bus import emit_interaction_events, write_event_bus_reports
from .event_replay import replay_event_log, write_event_replay_reports
from .event_ledger import append_event_ledger, verify_event_ledger, write_event_ledger_reports
from .provenance_chain import append_provenance_step, verify_provenance_chain, write_provenance_reports
from .guardian_runtime import load_guardian_policy, evaluate_guardian_boundary, write_guardian_reports
from .experiment_runner import run_governance_experiment, write_experiment_reports
from .shadow_policy import load_shadow_policy, evaluate_shadow_scenarios, write_shadow_reports
from .stress_tester import load_stress_policy, run_stress_trials, write_stress_reports
from .policy_surface import build_policy_surface, write_policy_surface_reports
from .phase_diagram import build_phase_diagram, write_phase_reports
from .adversarial_mutation import load_adversarial_policy, generate_adversarial_trials, evaluate_adversarial_trials, write_adversarial_reports
from .experiment_batch import build_experiment_manifest, write_experiment_manifest
from .stability_heatmap import build_stability_heatmap, write_heatmap_reports
from .paper_reports import write_paper_ready_reports
from .coordinated_experiments import build_coordinated_batch, write_coordinated_batch
from .policy_conflicts import analyze_policy_conflicts, write_policy_conflict_reports
from .unified_verifier import verify_unified_provenance, write_unified_verification_reports
from .recovery_metrics import compute_recovery_metrics, write_recovery_metrics_reports
from .actuation_scaffold import load_actuation_policy, build_actuation_plan, write_actuation_reports
from .governance_visuals import build_governance_visuals
from .full_system_verifier import run_full_system_verification, write_full_system_verification
from .run_profile import load_run_profiles, apply_profile, write_run_profile_report
from .report_index import build_report_index, write_report_index
from .runtime_manifest import write_runtime_manifest
from .runtime_capabilities import detect_capabilities, write_capability_reports, write_stage_status
from .publication_pack import (
    build_publication_summary,
    write_publication_summary,
    build_demo_packet,
    write_demo_packet_report,
)

ROOT = Path(".").resolve()

def parse_args():
    parser = argparse.ArgumentParser(description="StegVerse ingestion engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    shared_args = [
        ("source", {"help": "source bundle path"}),
        ("--entity", {"default": None, "help": "target entity name"}),
        ("--all-entities", {"action": "store_true", "help": "run for all entities"}),
        ("--experiment", {"action": "store_true", "help": "run governance experiments"}),
        ("--trials", {"type": int, "default": 1, "help": "number of trials"}),
        ("--stress-test", {"action": "store_true", "help": "run stress tests"}),
        ("--policy-surface", {"action": "store_true", "help": "build policy surface"}),
        ("--phase-diagram", {"action": "store_true", "help": "build phase diagram"}),
        ("--adversarial", {"action": "store_true", "help": "run adversarial mutations"}),
        ("--paper-reports", {"action": "store_true", "help": "generate paper-ready reports"}),
        ("--coordinated-batch", {"action": "store_true", "help": "build coordinated experiment batch"}),
        ("--unified-verify", {"action": "store_true", "help": "run unified provenance verification"}),
        ("--actuation-plan", {"action": "store_true", "help": "build actuation plan"}),
        ("--visuals", {"action": "store_true", "help": "generate governance visuals"}),
        ("--full-verify", {"action": "store_true", "help": "run full system verification"}),
        ("--profile", {"choices": ["demo", "research"], "default": None, "help": "run profile"}),
        ("--publication-pack", {"action": "store_true", "help": "build publication pack"}),
    ]

    for name in ["plan", "install", "orchestrate"]:
        p = sub.add_parser(name)
        for arg_name, arg_kwargs in shared_args:
            p.add_argument(arg_name, **arg_kwargs)

    return parser.parse_args()

def _run_optional_stage(reports_root: Path, stage_name: str, fn):
    try:
        result = fn()
        write_stage_status(reports_root, stage_name, "PASS", "stage completed")
        return result
    except Exception as e:
        write_stage_status(
            reports_root,
            stage_name,
            "SOFT_FAIL",
            str(e),
            extra={"exception_type": type(e).__name__},
        )
        print(f"{stage_name} soft-failed: {type(e).__name__}: {e}")
        return None

def run_for_entity(source: Path, mode: str, entity_name: str):
    reports_root = reports_root_for_entity(ROOT, entity_name)
    reports_root.mkdir(parents=True, exist_ok=True)
    mutation_receipt = classify_mutation(source, mode); mutation_receipt["entity"] = entity_name; write_mutation_receipt(reports_root, mutation_receipt)
    governance_policy = load_policy(ROOT / "configs" / "governance_policy.json")
    governance_receipt = evaluate_mutation(source, mode, governance_policy, mutation_type=mutation_receipt["mutation_type"]); governance_receipt["entity"] = entity_name; write_governance_receipt(reports_root, governance_receipt)
    admissibility_policy = load_admissibility_policy(ROOT / "configs" / "admissibility_policy.json")
    transition_receipt, admissibility_receipt = evaluate_admissibility(source, mode, mutation_receipt["mutation_type"], admissibility_policy); transition_receipt["entity"] = entity_name; admissibility_receipt["entity"] = entity_name; write_admissibility_reports(reports_root, transition_receipt, admissibility_receipt)
    guardian_policy = load_guardian_policy(ROOT / "configs" / "guardian_policy.json")
    guardian_receipt = evaluate_guardian_boundary(source, mode, guardian_policy); guardian_receipt["entity"] = entity_name; write_guardian_reports(reports_root, guardian_receipt)
    shadow_policy = load_shadow_policy(ROOT / "configs" / "shadow_policy.json")
    shadow_receipt = evaluate_shadow_scenarios(mode, mutation_receipt["mutation_type"], governance_receipt, admissibility_receipt, guardian_receipt, shadow_policy); shadow_receipt["entity"] = entity_name; write_shadow_reports(reports_root, shadow_receipt)
    allowed = governance_receipt["authorized"] and admissibility_receipt["admissible"] and guardian_receipt["verdict"] != "deny"
    report = {"entity": entity_name, "mode": mode, "source": str(source), "status": "authorized" if allowed else "denied", "mutation_receipt": mutation_receipt, "governance_receipt": governance_receipt, "transition_receipt": transition_receipt, "admissibility_receipt": admissibility_receipt, "guardian_receipt": guardian_receipt, "shadow_policy_receipt": shadow_receipt}
    perturbation_receipt = apply_perturbation(entity_name, report, mutation_receipt, governance_receipt); write_perturbation_receipt(reports_root, perturbation_receipt)
    recovery_receipt = apply_recovery(ROOT, entity_name); write_recovery_receipt(reports_root, recovery_receipt)
    receipt = write_receipts(reports_root, report, source)
    state_record = append_state(reports_root, receipt, report)
    write_summary(reports_root, receipt, state_record, report)
    write_state_graph_mermaid(reports_root)
    verification_result = verify_reports(reports_root); write_verification_reports(reports_root, verification_result)
    replay_result = replay_reports(reports_root); write_replay_reports(reports_root, replay_result)
    return {"entity": entity_name, "allowed": allowed, "verification_status": verification_result["status"], "replay_status": replay_result["status"], "guardian_verdict": guardian_receipt["verdict"], "shadow_scenarios": shadow_receipt.get("scenario_count", 0), "perturbed": perturbation_receipt.get("perturbation_enabled", False), "recovered": recovery_receipt.get("recovered", False)}

def main():
    args = parse_args()
    source = Path(args.source).resolve()
    reports_root = ROOT / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)

    capabilities = detect_capabilities()
    write_capability_reports(reports_root, capabilities)

    if args.profile:
        profiles = load_run_profiles(ROOT / "configs" / "run_profiles.json")
        applied = apply_profile(args, args.profile, profiles)
        write_run_profile_report(reports_root, args.profile, applied)

    entities = resolve_entities(ROOT, entity=getattr(args, "entity", None), all_entities=getattr(args, "all_entities", False))

    # ORCHESTRATE mode: plan all, then install approved
    if args.cmd == "orchestrate":
        print(f"=== ORCHESTRATION MODE ===")
        print(f"Entities: {entities}")
        print(f"Source: {source}")

        plan_results = []
        for entity_name in entities:
            print(f"\n[PLAN] Entity: {entity_name}")
            result = run_for_entity(source, "plan", entity_name)
            plan_results.append(result)
            print(f"[PLAN] {entity_name}: allowed={result['allowed']} guardian={result['guardian_verdict']}")

        install_results = []
        for result in plan_results:
            entity_name = result["entity"]
            if result["allowed"]:
                print(f"\n[INSTALL] Entity: {entity_name}")
                install_result = run_for_entity(source, "install", entity_name)
                install_results.append(install_result)
                print(f"[INSTALL] {entity_name}: status=complete")
            else:
                print(f"\n[SKIP] Entity: {entity_name} — denied by governance/admissibility/guardian")
                install_results.append(result)

        if len(entities) > 1:
            print(f"\n[COORDINATION] Cross-entity analysis")
            divergence = compare_entities(ROOT, entities)
            write_comparison_reports(ROOT, divergence)
            print(f"[COORDINATION] Divergence: state={divergence['state_hash_diverged']} mutation={divergence['mutation_type_diverged']} governance={divergence['governance_diverged']}")

            convergence = analyze_convergence(ROOT, entities)
            write_convergence_reports(ROOT, convergence)
            print(f"[COORDINATION] Convergence: replay={convergence['replay_converged']} state={convergence['state_hash_converged']} overall={convergence['overall_converged']}")

            interaction_receipt = evaluate_interactions(ROOT, entities)
            write_interaction_reports(ROOT, interaction_receipt)
            allowed_edges = sum(1 for e in interaction_receipt["edges"] if e["permitted"])
            blocked_edges = sum(1 for e in interaction_receipt["edges"] if not e["permitted"])
            print(f"[COORDINATION] Interactions: allowed={allowed_edges} blocked={blocked_edges}")

            event_log = emit_interaction_events(ROOT, entities, interaction_receipt)
            write_event_bus_reports(ROOT, event_log)
            print(f"[COORDINATION] Events: count={event_log['event_count']}")

            ledger_batch = append_event_ledger(ROOT, event_log)
            ledger_verification = verify_event_ledger(ROOT)
            write_event_ledger_reports(ROOT, ledger_batch, ledger_verification)
            print(f"[COORDINATION] Ledger: {ledger_verification['status']} batch={ledger_batch['batch_id']}")

            provenance_step = append_provenance_step(ROOT)
            provenance_verification = verify_provenance_chain(ROOT)
            write_provenance_reports(ROOT, provenance_step, provenance_verification)
            print(f"[COORDINATION] Provenance: {provenance_verification['status']} step={provenance_step['step_id']}")

            conflicts = analyze_policy_conflicts(ROOT, entities)
            write_policy_conflict_reports(reports_root, conflicts)
            print(f"[COORDINATION] Policy conflicts: count={conflicts['conflict_count']}")

            recovery = compute_recovery_metrics(ROOT, entities)
            write_recovery_metrics_reports(reports_root, recovery)
            print(f"[COORDINATION] Recovery metrics: rate={recovery['recovery_rate']:.2f}")

        orchestration_report = {
            "mode": "orchestrate",
            "entities": entities,
            "plan_results": [{"entity": r["entity"], "allowed": r["allowed"], "guardian_verdict": r["guardian_verdict"]} for r in plan_results],
            "install_results": [{"entity": r["entity"], "allowed": r["allowed"], "verification_status": r["verification_status"], "replay_status": r["replay_status"]} for r in install_results],
        }
        receipt = write_receipts(reports_root, orchestration_report, source)
        write_summary(reports_root, receipt, None, orchestration_report)

        print(f"\n=== ORCHESTRATION COMPLETE ===")
        for r in install_results:
            status = "INSTALLED" if r["allowed"] else "DENIED"
            print(f"  {r['entity']}: {status}")

        index_data = build_report_index(reports_root)
        write_report_index(reports_root, index_data)
        return

    # Standard plan/install mode
    results = [run_for_entity(source, args.cmd, entity_name) for entity_name in entities]

    flags = {
        "experiment": args.experiment,
        "stress_test": args.stress_test,
        "policy_surface": args.policy_surface,
        "phase_diagram": args.phase_diagram,
        "adversarial": args.adversarial,
        "paper_reports": args.paper_reports,
        "coordinated_batch": args.coordinated_batch,
        "unified_verify": args.unified_verify,
        "actuation_plan": args.actuation_plan,
        "visuals": args.visuals,
        "full_verify": args.full_verify,
        "publication_pack": args.publication_pack,
        "profile": args.profile,
    }
    write_runtime_manifest(reports_root, args.cmd, source, entities, flags)

    governance_policy = load_policy(ROOT / "configs" / "governance_policy.json")
    admissibility_policy = load_admissibility_policy(ROOT / "configs" / "admissibility_policy.json")
    guardian_policy = load_guardian_policy(ROOT / "configs" / "guardian_policy.json")

    stress_results = None
    surface = None
    phase = None
    adversarial_eval = None

    manifest = build_experiment_manifest(args.cmd, entities, max(1, getattr(args, "trials", 1)), getattr(args, "stress_test", False), getattr(args, "policy_surface", False), getattr(args, "phase_diagram", False))
    write_experiment_manifest(reports_root, manifest)

    if getattr(args, "coordinated_batch", False):
        batch = build_coordinated_batch(args.cmd, entities, "governance_batch", max(1, getattr(args, "trials", 1)))
        write_coordinated_batch(reports_root, batch)
        print(f"Coordinated batch generated: steps={len(batch['steps'])}")

    if len(entities) > 1:
        divergence = compare_entities(ROOT, entities); write_comparison_reports(ROOT, divergence); print(f"Cross-entity divergence computed: state={divergence['state_hash_diverged']} mutation={divergence['mutation_type_diverged']} governance={divergence['governance_diverged']}")
        convergence = analyze_convergence(ROOT, entities); write_convergence_reports(ROOT, convergence); print(f"Cross-entity convergence computed: replay={convergence['replay_converged']} state={convergence['state_hash_converged']} overall={convergence['overall_converged']}")
        interaction_receipt = evaluate_interactions(ROOT, entities); write_interaction_reports(ROOT, interaction_receipt)
        allowed_edges = sum(1 for e in interaction_receipt["edges"] if e["permitted"]); blocked_edges = sum(1 for e in interaction_receipt["edges"] if not e["permitted"]); print(f"Interaction policy evaluated: allowed_edges={allowed_edges} blocked_edges={blocked_edges}")
        event_log = emit_interaction_events(ROOT, entities, interaction_receipt); write_event_bus_reports(ROOT, event_log); print(f"Event bus emitted: count={event_log['event_count']}")
        event_replay_result = replay_event_log(reports_root); write_event_replay_reports(reports_root, event_replay_result); print(f"Event replay {event_replay_result['status']}")
        ledger_batch = append_event_ledger(ROOT, event_log); ledger_verification = verify_event_ledger(ROOT); write_event_ledger_reports(ROOT, ledger_batch, ledger_verification); print(f"Event ledger {ledger_verification['status']} batch={ledger_batch['batch_id']}")
        provenance_step = append_provenance_step(ROOT); provenance_verification = verify_provenance_chain(ROOT); write_provenance_reports(ROOT, provenance_step, provenance_verification); print(f"Provenance chain {provenance_verification['status']} step={provenance_step['step_id']}")
        conflicts = analyze_policy_conflicts(ROOT, entities); write_policy_conflict_reports(reports_root, conflicts); print(f"Policy conflicts analyzed: count={conflicts['conflict_count']}")
        recovery = compute_recovery_metrics(ROOT, entities); write_recovery_metrics_reports(reports_root, recovery); print(f"Recovery metrics generated: rate={recovery['recovery_rate']:.2f}")

    if getattr(args, "experiment", False):
        experiment = run_governance_experiment(ROOT, results, max(1, getattr(args, "trials", 1))); write_experiment_reports(reports_root, experiment); print(f"Experiment runner complete: trials={experiment['trial_count']} verification_rate={experiment['verification_rate']:.2f} replay_rate={experiment['replay_rate']:.2f}")

    if getattr(args, "stress_test", False):
        stress_policy = load_stress_policy(ROOT / "configs" / "stress_test_policy.json"); stress_results = run_stress_trials(stress_policy, governance_policy, admissibility_policy, guardian_policy); write_stress_reports(reports_root, stress_results); print(f"Stress test complete: trials={stress_results['trial_count']} allow_rate={stress_results['allow_rate']:.2f} deny_rate={stress_results['deny_rate']:.2f}")

    if getattr(args, "policy_surface", False):
        surface = build_policy_surface(governance_policy, admissibility_policy, guardian_policy); write_policy_surface_reports(reports_root, surface); print(f"Policy surface generated: modes={len(surface['modes'])} mutation_types={len(surface['mutation_types'])}")

    if getattr(args, "phase_diagram", False):
        if surface is None: surface = build_policy_surface(governance_policy, admissibility_policy, guardian_policy)
        phase = build_phase_diagram(surface, stress_results); write_phase_reports(reports_root, phase); print(f"Phase diagram generated: regions={len(phase['regions'])}")

    if getattr(args, "adversarial", False):
        adversarial_policy = load_adversarial_policy(ROOT / "configs" / "adversarial_policy.json")
        generated = generate_adversarial_trials(adversarial_policy); adversarial_eval = evaluate_adversarial_trials(generated, governance_policy, admissibility_policy, guardian_policy); write_adversarial_reports(reports_root, generated, adversarial_eval); print(f"Adversarial mutations generated: trials={adversarial_eval['trial_count']} failure_zones={len(adversarial_eval['failure_zone_counts'])}")

    if getattr(args, "paper_reports", False):
        if surface is not None:
            heatmap = build_stability_heatmap(surface, stress_results); write_heatmap_reports(reports_root, heatmap); print("Stability heatmap generated")
        write_paper_ready_reports(reports_root, stress_results, phase, surface, adversarial_eval); print("Paper-ready reports generated")

    if getattr(args, "unified_verify", False):
        unified = verify_unified_provenance(ROOT); write_unified_verification_reports(reports_root, unified); print(f"Unified provenance verification {unified['status']}")

    if getattr(args, "actuation_plan", False):
        act_policy = load_actuation_policy(ROOT / "configs" / "actuation_policy.json"); act_plan = build_actuation_plan(source, entities, act_policy); write_actuation_reports(reports_root, act_plan); print(f"Actuation plan generated: actions={len(act_plan['actions'])} enabled={act_plan['enabled']}")

    if getattr(args, "visuals", False):
        visuals = _run_optional_stage(reports_root, "visuals", lambda: build_governance_visuals(reports_root))
        if visuals is not None:
            print(f"Visualizations generated: count={len(visuals['generated_files'])}")

    if getattr(args, "full_verify", False):
        full = _run_optional_stage(reports_root, "full_system_verification", lambda: run_full_system_verification(reports_root))
        if full is not None:
            write_full_system_verification(reports_root, full)
            print(f"Full system verification {full['status']}")

    if getattr(args, "publication_pack", False):
        summary = build_publication_summary(reports_root)
        write_publication_summary(reports_root, summary)
        print(f"Publication summary generated: present={summary['present_count']} missing={summary['missing_count']}")
        packet = build_demo_packet(reports_root)
        write_demo_packet_report(reports_root, packet)
        print(f"Demo packet generated: files={packet['file_count']} zip={packet['zip_name']}")

    index_data = build_report_index(reports_root)
    write_report_index(reports_root, index_data)

    for result in results:
        if result["allowed"]: print(f"Entity {result['entity']}: Ingestion complete")
        else: print(f"Entity {result['entity']}: Ingestion denied by governance or admissibility policy")
        print(f"Entity {result['entity']}: Guardian verdict {result['guardian_verdict']}")
        print(f"Entity {result['entity']}: Shadow scenarios evaluated {result['shadow_scenarios']}")
        print(f"Entity {result['entity']}: Independent verification {result['verification_status']}")
        print(f"Entity {result['entity']}: Deterministic replay {result['replay_status']}")
        if result["perturbed"]: print(f"Entity {result['entity']}: Perturbation applied")
        if result["recovered"]: print(f"Entity {result['entity']}: Recovery applied")

if __name__ == "__main__":
    main()
