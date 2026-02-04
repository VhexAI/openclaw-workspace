#!/usr/bin/env python3
"""
ARS Demo v2.0
=============
Demonstrates the full Adaptive Reasoning Simulator pipeline across
multiple scenarios including complex tasks with high uncertainty.

Usage:
    python demo.py
    python demo.py --llm          # Enable Ollama LLM integration
    python demo.py --benchmark    # Run performance benchmarks
"""

from __future__ import annotations
import argparse
import json
import sys
import textwrap
from ars import ARS, ARSValidationError, BenchmarkResult


def divider(title: str) -> None:
    print(f"\n{'=' * 64}")
    print(f"  {title}")
    print("=" * 64)


def print_result(result, sim: ARS) -> None:
    if result is None:
        print("\n✅  ARS skipped — confidence already sufficient.\n")
        return

    print(f"\n🏆  Top path ID : {result.top_path_id}")
    print(f"📈  Confidence  : {result.confidence_after:.4f}")
    print(f"⚠️   Fallback    : {result.fallback_needed}")
    print(f"🤖  LLM used    : {result.memory_snapshot.get('llm_used', False)}\n")

    print("📋  Merged plan:")
    for i, step in enumerate(result.merged_plan, 1):
        prefix = "  ⚠️" if step.startswith("[FALLBACK]") or step.startswith("[ERROR]") else "   "
        print(f"{prefix} {i}. {step}")

    print(f"\n🧠  Memory snapshot:")
    print(textwrap.indent(json.dumps(result.memory_snapshot, indent=2, default=str), "    "))

    log = sim.get_simulation_log()
    if log:
        entry = log[-1]
        print(f"\n📊  Simulation log (last run):")
        print(f"    paths generated : {entry['num_paths']}")
        print(f"    elapsed         : {entry['elapsed']:.4f}s")
        print(f"    llm used        : {entry.get('llm_used', False)}")

    print()


def run_scenario(
    label: str,
    num_branches: int,
    confidence: float,
    goal: str,
    context: str,
    past: list[str],
    llm_backend: str | None = None,
    llm_model: str = "llama3.2",
    scoring_weights: dict[str, float] | None = None,
) -> None:
    divider(label)
    sim = ARS(
        num_branches=num_branches,
        llm_backend=llm_backend,
        llm_model=llm_model,
        scoring_weights=scoring_weights,
    )
    result = sim.invoke_ars(
        current_confidence=confidence,
        task_goal=goal,
        current_context=context,
        past_actions=past,
    )
    print_result(result, sim)


def run_validation_tests() -> None:
    """Demonstrate input validation catches bad inputs."""
    divider("Validation Tests — Error Handling")
    tests = [
        ("Negative confidence", {"current_confidence": -0.5, "task_goal": "test"}),
        ("Confidence > 1", {"current_confidence": 1.5, "task_goal": "test"}),
        ("Empty goal", {"current_confidence": 0.3, "task_goal": "   "}),
    ]
    sim = ARS()
    for label, kwargs in tests:
        try:
            sim.invoke_ars(**kwargs)
            print(f"  ❌ {label}: should have raised ARSValidationError")
        except ARSValidationError as exc:
            print(f"  ✅ {label}: caught → {exc}")
        except Exception as exc:
            print(f"  ❌ {label}: unexpected error → {exc}")
    print()


def run_benchmarks(llm_backend: str | None = None) -> None:
    """Run and display performance benchmarks."""
    divider("Performance Benchmarks")
    sim = ARS(llm_backend=llm_backend)
    results = sim.benchmark(
        task_goal="Optimize a distributed cache eviction policy",
        num_runs=3,
        branches_list=[5, 10, 20],
    )
    print(f"\n{'Branches':>10} {'Avg Time':>10} {'Best':>8} {'Worst':>8} "
          f"{'Mean':>8} {'Steps':>7} {'Fallback':>10}")
    print("-" * 70)
    for r in results:
        print(f"{r.num_branches:>10} {r.elapsed_seconds:>9.4f}s {r.best_score:>8.4f} "
              f"{r.worst_score:>8.4f} {r.mean_score:>8.4f} {r.plan_step_count:>7} "
              f"{'YES' if r.fallback_triggered else 'no':>10}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="ARS Demo v2.0")
    parser.add_argument("--llm", action="store_true", help="Enable Ollama LLM integration")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarks")
    args = parser.parse_args()

    llm = "ollama" if args.llm else None

    # ── Scenario 1: Classic cake recipe (simple) ──
    run_scenario(
        label="Scenario 1 — 10 branches, low confidence (0.4), simple goal",
        num_branches=10,
        confidence=0.4,
        goal="Plan a 3-step cake recipe",
        context="Home kitchen, basic ingredients (flour, sugar, eggs, butter, milk)",
        past=["Checked pantry", "Found flour and sugar", "Preheated oven to 350°F"],
        llm_backend=llm,
        llm_model=args.model,
    )

    # ── Scenario 2: Complex crypto bounty with high uncertainty ──
    run_scenario(
        label="Scenario 2 — 10 branches, very low confidence (0.15), crypto bounty",
        num_branches=10,
        confidence=0.15,
        goal="Analyze smart contract vulnerability for $50k bug bounty — "
             "reentrancy attack vector in DeFi lending protocol with proxy upgrades",
        context="Solidity 0.8.x, OpenZeppelin UUPS proxy, Compound-fork lending pool. "
                "Contract verified on Etherscan. Previous audits missed flash loan interactions.",
        past=[
            "Identified proxy pattern (UUPS)",
            "Reviewed storage layout — potential slot collision",
            "Traced flash loan callback flow",
            "Found unchecked external call in liquidation path",
        ],
        llm_backend=llm,
        llm_model=args.model,
    )

    # ── Scenario 3: Ensemble scoring — weighted toward novelty ──
    run_scenario(
        label="Scenario 3 — Novelty-weighted scoring (exploration mode)",
        num_branches=10,
        confidence=0.3,
        goal="Design a novel consensus mechanism for IoT mesh networks",
        context="Resource-constrained devices, intermittent connectivity, Byzantine faults",
        past=["Reviewed PBFT limitations", "Sketched DAG-based approach"],
        scoring_weights={"feasibility": 0.20, "success": 0.30, "novelty": 0.50},
        llm_backend=llm,
        llm_model=args.model,
    )

    # ── Scenario 4: Confidence already high → skip ──
    run_scenario(
        label="Scenario 4 — confidence already high (0.9) → ARS skipped",
        num_branches=10,
        confidence=0.9,
        goal="Plan a 3-step cake recipe",
        context="Home kitchen",
        past=[],
    )

    # ── Validation tests ──
    run_validation_tests()

    # ── Benchmarks (optional) ──
    if args.benchmark:
        run_benchmarks(llm_backend=llm)


if __name__ == "__main__":
    main()
