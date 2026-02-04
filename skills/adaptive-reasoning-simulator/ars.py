"""
Adaptive Reasoning Simulator (ARS)
===================================
Boosts agent intelligence by simulating and adapting multiple reasoning paths
in parallel, then selecting the highest-scoring plan.

Usage:
    from ars import ARS
    sim = ARS()
    result = sim.invoke_ars(
        current_confidence=0.5,
        task_goal="Plan a 3-step cake recipe",
        current_context="Home kitchen, basic ingredients available",
        past_actions=["Checked pantry", "Found flour and sugar"]
    )
    print(result)
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("ARS")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[ARS %(levelname)s] %(message)s"))
    logger.addHandler(_h)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class SimulatedPath:
    """One candidate reasoning path produced by the simulator."""
    path_id: str
    branch_index: int
    goal: str
    variation_seed: int
    steps: list[str]
    success_prob: float
    raw_prompt: str


@dataclass
class ScoredPath:
    """A path after evaluation scoring."""
    path: SimulatedPath
    feasibility: float
    success: float
    novelty: float
    total_score: float


@dataclass
class AdaptResult:
    """Output of the adapt stage."""
    merged_plan: list[str]
    fallback_needed: bool
    memory_snapshot: dict[str, Any]
    top_path_id: str
    confidence_after: float


# ---------------------------------------------------------------------------
# Worker function (must be top-level for multiprocessing pickling)
# ---------------------------------------------------------------------------
def _simulate_single_path(args: tuple) -> dict:
    """
    Worker that simulates one reasoning path.
    Runs inside a child process via ProcessPoolExecutor.
    """
    branch_index, goal, variation_seed, rng_seed = args
    rng = np.random.default_rng(rng_seed)

    # Beta-distributed success probability (α=2, β=5 → right-skewed, realistic)
    success_prob = float(rng.beta(2.0, 5.0))

    # Generate plausible reasoning steps (deterministic from seed)
    step_pool = [
        f"Analyse sub-goal derived from '{goal}'",
        f"Gather resources relevant to '{goal}'",
        f"Prototype approach variation {variation_seed}",
        f"Validate intermediate result for branch {branch_index}",
        f"Iterate on feedback for variation {variation_seed}",
        f"Consolidate findings toward '{goal}'",
        f"Stress-test plan branch {branch_index}",
        f"Optimise step sequence (seed {variation_seed})",
    ]
    num_steps = int(rng.integers(3, len(step_pool) + 1))
    chosen = list(rng.choice(step_pool, size=num_steps, replace=False))

    prompt = f"Simulate path {branch_index} | goal: {goal} | variation: {variation_seed}"

    return {
        "path_id": hashlib.sha256(f"{goal}-{branch_index}-{variation_seed}".encode()).hexdigest()[:12],
        "branch_index": branch_index,
        "goal": goal,
        "variation_seed": variation_seed,
        "steps": chosen,
        "success_prob": success_prob,
        "raw_prompt": prompt,
    }


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------
class ARS:
    """
    Adaptive Reasoning Simulator.

    Parameters
    ----------
    num_branches : int
        Number of parallel reasoning paths to simulate (default 10).
    confidence_threshold : float
        Minimum confidence before ARS is invoked (default 0.7).
    sim_timeout : float
        Seconds before simulation times out (default 30).
    """

    def __init__(
        self,
        num_branches: int = 10,
        confidence_threshold: float = 0.7,
        sim_timeout: float = 30.0,
    ) -> None:
        self.num_branches = num_branches
        self.confidence_threshold = confidence_threshold
        self.sim_timeout = sim_timeout

        # Persistent memory across invocations
        self.memory: list[dict[str, Any]] = []
        self.simulation_log: list[dict[str, Any]] = []

        logger.info(
            "ARS initialised  branches=%d  threshold=%.2f  timeout=%.1fs",
            self.num_branches, self.confidence_threshold, self.sim_timeout,
        )

    # ------------------------------------------------------------------
    # 1. Capture state
    # ------------------------------------------------------------------
    def capture_state(
        self,
        task_goal: str,
        current_context: str,
        past_actions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Snapshot the current reasoning state into a portable dict."""
        state = {
            "id": uuid.uuid4().hex[:8],
            "task_goal": task_goal,
            "current_context": current_context,
            "past_actions": past_actions or [],
            "timestamp": time.time(),
            "memory_size": len(self.memory),
        }
        logger.info("State captured  id=%s  goal='%s'", state["id"], task_goal)
        return state

    # ------------------------------------------------------------------
    # 2. Simulate paths
    # ------------------------------------------------------------------
    def simulate_paths(self, state: dict[str, Any]) -> list[SimulatedPath]:
        """
        Launch *num_branches* parallel simulations via multiprocessing.
        Each worker generates a reasoning path with a Beta-distributed
        success probability.
        """
        goal = state["task_goal"]
        master_seed = int(hashlib.sha256(goal.encode()).hexdigest()[:8], 16)

        tasks = [
            (i, goal, (master_seed + i) % 10000, master_seed + i)
            for i in range(self.num_branches)
        ]

        paths: list[SimulatedPath] = []
        logger.info("Simulating %d paths in parallel …", self.num_branches)
        t0 = time.perf_counter()

        try:
            with ProcessPoolExecutor(max_workers=min(self.num_branches, 8)) as pool:
                futures = pool.map(
                    _simulate_single_path, tasks, timeout=self.sim_timeout,
                )
                for raw in futures:
                    paths.append(SimulatedPath(**raw))
        except FuturesTimeout:
            logger.warning("Simulation timed out after %.1fs", self.sim_timeout)

        elapsed = time.perf_counter() - t0
        logger.info("Simulation complete  paths=%d  elapsed=%.3fs", len(paths), elapsed)

        # Log
        self.simulation_log.append({
            "state_id": state["id"],
            "num_paths": len(paths),
            "elapsed": elapsed,
        })

        return paths

    # ------------------------------------------------------------------
    # 3. Evaluate paths
    # ------------------------------------------------------------------
    def evaluate_paths(self, paths: list[SimulatedPath]) -> list[ScoredPath]:
        """
        Score each path on three axes and return sorted (best first).

        - **feasibility**: inverse of step count (fewer steps → more feasible)
        - **success**: the Beta-sampled success_prob from simulation
        - **novelty**: mean edit-distance to every other path (higher → more novel)
        """
        if not paths:
            return []

        # Pre-compute step-text fingerprints for edit-distance
        step_texts = [" | ".join(p.steps) for p in paths]

        scored: list[ScoredPath] = []
        for idx, path in enumerate(paths):
            feasibility = 1.0 / max(len(path.steps), 1)
            success = path.success_prob

            # Novelty via pairwise SequenceMatcher
            distances = []
            for jdx, other_text in enumerate(step_texts):
                if jdx == idx:
                    continue
                ratio = SequenceMatcher(None, step_texts[idx], other_text).ratio()
                distances.append(1.0 - ratio)  # distance = 1 - similarity
            novelty = float(np.mean(distances)) if distances else 0.0

            total = 0.35 * feasibility + 0.40 * success + 0.25 * novelty

            scored.append(ScoredPath(
                path=path,
                feasibility=round(feasibility, 4),
                success=round(success, 4),
                novelty=round(novelty, 4),
                total_score=round(total, 4),
            ))

        scored.sort(key=lambda s: s.total_score, reverse=True)
        logger.info(
            "Evaluation done  best_score=%.4f  worst_score=%.4f",
            scored[0].total_score, scored[-1].total_score,
        )
        return scored

    # ------------------------------------------------------------------
    # 4. Adapt
    # ------------------------------------------------------------------
    def adapt(
        self,
        state: dict[str, Any],
        top_paths: list[ScoredPath],
        merge_top_n: int = 3,
    ) -> AdaptResult:
        """
        Merge the best *merge_top_n* paths into a single plan, update
        memory, and flag whether a fallback is needed.
        """
        if not top_paths:
            return AdaptResult(
                merged_plan=["[FALLBACK] No paths available — request human guidance."],
                fallback_needed=True,
                memory_snapshot={},
                top_path_id="none",
                confidence_after=0.0,
            )

        selected = top_paths[:merge_top_n]
        best = selected[0]

        # Merge: take unique steps from top paths, preserving order of first appearance
        seen: set[str] = set()
        merged_plan: list[str] = []
        for sp in selected:
            for step in sp.path.steps:
                if step not in seen:
                    seen.add(step)
                    merged_plan.append(step)

        # Confidence boost based on best score
        confidence_after = min(1.0, best.total_score + 0.25)
        fallback_needed = confidence_after < self.confidence_threshold

        # Persist to memory
        memory_entry = {
            "state_id": state["id"],
            "goal": state["task_goal"],
            "merged_plan": merged_plan,
            "best_score": best.total_score,
            "confidence_after": confidence_after,
            "fallback_needed": fallback_needed,
            "timestamp": time.time(),
        }
        self.memory.append(memory_entry)

        if fallback_needed:
            merged_plan.append("[FALLBACK] Confidence still below threshold — consider manual review.")
            logger.warning("Fallback flagged  confidence=%.2f", confidence_after)
        else:
            logger.info("Adaptation succeeded  confidence=%.2f", confidence_after)

        return AdaptResult(
            merged_plan=merged_plan,
            fallback_needed=fallback_needed,
            memory_snapshot=memory_entry,
            top_path_id=best.path.path_id,
            confidence_after=confidence_after,
        )

    # ------------------------------------------------------------------
    # 5. invoke_ars (full pipeline)
    # ------------------------------------------------------------------
    def invoke_ars(
        self,
        current_confidence: float,
        task_goal: str,
        current_context: str = "",
        past_actions: list[str] | None = None,
    ) -> AdaptResult | None:
        """
        Main entry point.  Runs the full ARS pipeline **only** when
        *current_confidence* is below the configured threshold.

        Returns
        -------
        AdaptResult or None
            None when confidence is already sufficient.
        """
        logger.info(
            "invoke_ars called  confidence=%.2f  threshold=%.2f",
            current_confidence, self.confidence_threshold,
        )

        if current_confidence >= self.confidence_threshold:
            logger.info("Confidence sufficient — ARS not needed.")
            return None

        state = self.capture_state(task_goal, current_context, past_actions)
        paths = self.simulate_paths(state)
        scored = self.evaluate_paths(paths)
        result = self.adapt(state, scored)
        return result

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    def get_memory(self) -> list[dict[str, Any]]:
        """Return a copy of the persistent memory store."""
        return list(self.memory)

    def get_simulation_log(self) -> list[dict[str, Any]]:
        """Return the raw simulation log."""
        return list(self.simulation_log)

    def __repr__(self) -> str:
        return (
            f"ARS(branches={self.num_branches}, "
            f"threshold={self.confidence_threshold}, "
            f"timeout={self.sim_timeout}s, "
            f"memory_entries={len(self.memory)})"
        )
