#!/usr/bin/env python3
"""
ARS Demo — "Plan a 3-step cake recipe"
=======================================
Runs the full Adaptive Reasoning Simulator pipeline and pretty-prints the
results.  Also demonstrates the fallback path by lowering branches to 5.

Usage:
    python demo.py
"""

from __future__ import annotations
import json, textwrap
from ars import ARS


def divider(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def run_scenario(
    label: str,
    num_branches: int,
    confidence: float,
    goal: str,
    context: str,
    past: list[str],
) -> None:
    divider(label)
    sim = ARS(num_branches=num_branches)
    result = sim.invoke_ars(
        current_confidence=confidence,
        task_goal=goal,
        current_context=context,
        past_actions=past,
    )

    if result is None:
        print("\n✅  ARS skipped — confidence already sufficient.\n")
        return

    print(f"\n🏆  Top path ID : {result.top_path_id}")
    print(f"📈  Confidence  : {result.confidence_after:.2f}")
    print(f"⚠️   Fallback    : {result.fallback_needed}\n")

    print("📋  Merged plan:")
    for i, step in enumerate(result.merged_plan, 1):
        print(f"    {i}. {step}")

    print(f"\n🧠  Memory snapshot:")
    print(textwrap.indent(json.dumps(result.memory_snapshot, indent=2, default=str), "    "))

    # Show simulation log
    log = sim.get_simulation_log()
    if log:
        entry = log[-1]
        print(f"\n📊  Simulation log (last run):")
        print(f"    paths generated : {entry['num_paths']}")
        print(f"    elapsed         : {entry['elapsed']:.4f}s")

    print()


def main() -> None:
    goal = "Plan a 3-step cake recipe"
    context = "Home kitchen, basic ingredients (flour, sugar, eggs, butter, milk)"
    past = ["Checked pantry", "Found flour and sugar", "Preheated oven to 350°F"]

    # ── Scenario 1: full 10-branch run ──
    run_scenario(
        label="Scenario 1 — 10 branches, low confidence (0.4)",
        num_branches=10,
        confidence=0.4,
        goal=goal,
        context=context,
        past=past,
    )

    # ── Scenario 2: reduced to 5 branches (issue mitigation) ──
    run_scenario(
        label="Scenario 2 — 5 branches (reduced for speed), low confidence (0.5)",
        num_branches=5,
        confidence=0.5,
        goal=goal,
        context=context,
        past=past,
    )

    # ── Scenario 3: confidence already high → ARS skipped ──
    run_scenario(
        label="Scenario 3 — confidence already high (0.9) → ARS skipped",
        num_branches=10,
        confidence=0.9,
        goal=goal,
        context=context,
        past=past,
    )


if __name__ == "__main__":
    main()
