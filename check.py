#!/usr/bin/env python3
"""Run all quality checks: pytest, pyright, ruff, tach."""
from __future__ import annotations

import subprocess
import sys


def run(label: str, cmd: list[str]) -> bool:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd)
    ok = result.returncode == 0
    print(f"\n  {'OK' if ok else 'FAILED'}: {label}")
    return ok


checks = [
    ("pytest", ["uv", "run", "pytest"]),
    ("pyright", ["uv", "run", "pyright"]),
    ("ruff", ["uv", "run", "ruff", "check", "packages/"]),
    ("tach", ["uv", "run", "tach", "check-external"]),
]

results = [run(label, cmd) for label, cmd in checks]

print(f"\n{'=' * 60}")
for (label, _), ok in zip(checks, results):
    status = "OK    " if ok else "FAILED"
    print(f"  {status}  {label}")
print(f"{'=' * 60}\n")

sys.exit(0 if all(results) else 1)
