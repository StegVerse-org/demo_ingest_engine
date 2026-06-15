from __future__ import annotations

from pathlib import Path

ALLOWED_WORKFLOWS = {
    "declared-sandbox-task-smoke-test.yml",
    "result-intake-smoke-test.yml",
}

WORKFLOW_DIR = Path(".github/workflows")


def main() -> int:
    if not WORKFLOW_DIR.exists():
        print("FAIL: .github/workflows directory missing")
        return 1

    actual = sorted(p.name for p in WORKFLOW_DIR.iterdir() if p.is_file() and p.suffix in {".yml", ".yaml"})
    unexpected = [name for name in actual if name not in ALLOWED_WORKFLOWS]
    missing = [name for name in sorted(ALLOWED_WORKFLOWS) if name not in actual]

    print("allowed_workflows=", sorted(ALLOWED_WORKFLOWS))
    print("actual_workflows=", actual)

    if unexpected:
        print("FAIL: unexpected active workflows:", unexpected)
        return 1
    if missing:
        print("FAIL: missing required workflows:", missing)
        return 1

    print("PASS: core-lite workflow posture verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
