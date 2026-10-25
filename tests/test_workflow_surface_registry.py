"""G17 workflow-surface registry for demo_ingest_engine: the workflow files equal the
registry's surfaces[]; no gated trigger; every folded workflow's verbatim record is
pinned; the catalog verifies ALLOW and covers every folded job. Stdlib only (runs
under tools/tasks/run_plain_tests.py or unittest)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "control/workflow-surface-registry.json").read_text())
CATALOG = json.loads((ROOT / "tools/tasks/task_catalog.json").read_text())
GATED = ("workflow_dispatch", "schedule", "repository_dispatch", "issues", "workflow_run")


def test_workflow_files_equal_registered_surfaces():
    actual = sorted(p.name for p in (ROOT / ".github/workflows").iterdir() if p.suffix in (".yml", ".yaml"))
    registered = sorted(Path(s["path"]).name for s in REGISTRY["surfaces"])
    assert actual == registered, (actual, registered)
    assert len(actual) <= REGISTRY["preferred_repository_workflow_count_max"]


def test_no_gated_trigger_on_any_surface():
    for s in REGISTRY["surfaces"]:
        text = (ROOT / s["path"]).read_text()
        on = text.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
        for t in GATED:
            assert f"  {t}:" not in on, (s["path"], t)


def test_folded_records_pinned_and_covered():
    groups = {g["id"]: g for g in CATALOG["groups"]}
    for f in REGISTRY["folded"]:
        path = ROOT / f["verbatim_record"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == f["verbatim_sha256"], f["workflow"]
        assert f["catalog_group"] in groups, f["catalog_group"]
        assert set(groups[f["catalog_group"]]["events"]) == {"pull_request", "push"}


def test_catalog_verifies_allow():
    proc = subprocess.run([sys.executable, str(ROOT / "tools/tasks/run_catalog.py"), "verify"],
                          capture_output=True, text=True)
    assert proc.returncode == 0 and json.loads(proc.stdout)["disposition"] == "ALLOW", proc.stdout


class RegistryTests(unittest.TestCase):
    def test_all(self):
        for fn in (test_workflow_files_equal_registered_surfaces, test_no_gated_trigger_on_any_surface,
                   test_folded_records_pinned_and_covered, test_catalog_verifies_allow):
            fn()


if __name__ == "__main__":
    unittest.main()
