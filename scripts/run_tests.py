#!/usr/bin/env python3
"""Run the full test suite and produce a concise summary report."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def classify_reason(test: unittest.TestCase, tb: str) -> str:
    """Extract a short reason from a traceback."""
    last_line = tb.strip().splitlines()[-1] if tb.strip() else "Unknown"
    if "No such file or directory" in tb:
        # Pull out the missing path
        for line in tb.splitlines():
            if "No such file or directory" in line:
                path = line.split("No such file or directory:")[-1].strip().strip("'\"")
                rel = path.replace(str(ROOT) + "/", "")
                return f"missing: {rel}"
    if "ModuleNotFoundError" in tb:
        mod = last_line.split("No module named")[-1].strip().strip("'\"")
        return f"missing module: {mod}"
    if "Missing" in tb and ("interpreter" in tb or "binary" in tb or "env" in tb):
        for line in tb.splitlines():
            if "Missing" in line:
                return line.split(":")[-1].strip() if ":" in line else "missing runtime"
    if "ConnectionError" in tb or "URLError" in tb or "TimeoutError" in tb:
        return "network unavailable"
    if "CalledProcessError" in tb:
        return "subprocess failed"
    # Fallback: use last line, truncated
    return last_line[:120] if len(last_line) > 120 else last_line


def short_name(test: unittest.TestCase) -> str:
    """Return a compact test name."""
    full = str(test)
    # Format: test_method (module.Class)
    if " (" in full and full.endswith(")"):
        method, rest = full.split(" (", 1)
        rest = rest.rstrip(")")
        parts = rest.split(".")
        # Use just the test method name — it's descriptive enough
        return method
    return full


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py", top_level_dir=str(ROOT))

    # Run with minimal verbosity to suppress noise
    import io
    runner = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0)
    result = runner.run(suite)

    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errors = len(result.errors)

    # Detect environment
    slurm_envs = ROOT / "slurm" / "envs"
    env_count = sum(1 for p in slurm_envs.iterdir() if p.is_dir()) if slurm_envs.exists() else 0
    experiments_exist = (ROOT / "experiments").exists()
    reports_exist = any((ROOT / "reports" / "framework-runs").glob("*/manifest.json")) if (ROOT / "reports" / "framework-runs").exists() else False

    # Print report
    print()
    print("=" * 56)
    print("  SkillFoundry Test Report")
    print("=" * 56)
    print()
    print(f"  Total:   {total}")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Errors:  {errors}")
    print()

    if result.failures or result.errors:
        print("-" * 56)
        if result.failures:
            print(f"  Failures ({len(result.failures)}):")
            for test, tb in result.failures:
                reason = classify_reason(test, tb)
                print(f"    x {short_name(test)}")
                print(f"      -> {reason}")
            print()

        if result.errors:
            print(f"  Errors ({len(result.errors)}):")
            for test, tb in result.errors:
                reason = classify_reason(test, tb)
                print(f"    ! {short_name(test)}")
                print(f"      -> {reason}")
            print()

    print("-" * 56)
    print("  Environment:")
    print(f"    Python:          {sys.version.split()[0]}")
    print(f"    Slurm envs:      {env_count} found")
    print(f"    Experiments dir:  {'yes' if experiments_exist else 'no'}")
    print(f"    Framework runs:  {'yes' if reports_exist else 'no'}")
    print("=" * 56)

    return 0 if not result.failures and not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
