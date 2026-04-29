#!/usr/bin/env python3
"""Basic CLI tests."""

import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [sys.executable, "-m", "ingest.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "plan" in result.stdout
    assert "install" in result.stdout
    assert "orchestrate" in result.stdout


def test_plan_help():
    result = subprocess.run(
        [sys.executable, "-m", "ingest.cli", "plan", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "source" in result.stdout
