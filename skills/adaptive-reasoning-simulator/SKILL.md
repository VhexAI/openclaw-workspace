---
name: adaptive-reasoning-simulator
version: 1.0.0
description: >
  Boost agent intelligence by simulating multiple parallel reasoning paths,
  scoring them on feasibility / success / novelty, and adaptively merging the
  best into a single plan.  Uses multiprocessing + numpy for fast Beta-sampled
  simulations.  Drop-in Python class — call `invoke_ars()` whenever confidence
  is low and watch the agent self-improve.
---

# Adaptive Reasoning Simulator (ARS)

> **TL;DR** — When your agent isn't sure what to do, ARS spins up N parallel
> "what-if" reasoning branches, scores them, and hands back a merged plan with
> a confidence boost.

## Quick Start

```bash
pip install numpy          # only external dep
python demo.py             # full 3-scenario demo
```

```python
from ars import ARS

sim = ARS(num_branches=10, confidence_threshold=0.7, sim_timeout=30)
result = sim.invoke_ars(
    current_confidence=0.4,
    task_goal="Plan a 3-step cake recipe",
    current_context="Home kitchen, basic ingredients",
    past_actions=["Checked pantry", "Found flour and sugar"],
)
print(result.merged_plan)
```

## Class API

### `ARS(num_branches=10, confidence_threshold=0.7, sim_timeout=30)`

| Param | Default | Purpose |
|---|---|---|
| `num_branches` | 10 | Parallel reasoning paths to simulate |
| `confidence_threshold` | 0.7 | Confidence below this triggers ARS |
| `sim_timeout` | 30.0 | Seconds before simulation times out |

Internal stores: `self.memory` (list of dicts), `self.simulation_log`.

### `capture_state(task_goal, current_context, past_actions) → dict`

Snapshots the current goal, context, and action history into a portable state
dictionary used by downstream stages.

### `simulate_paths(state) → list[SimulatedPath]`

Launches `num_branches` workers via `ProcessPoolExecutor`.  Each worker:

1. Builds prompt: `"Simulate path X | goal: Y | variation: Z"`
2. Draws `success_prob` from `numpy.random.beta(2, 5)`
3. Selects a random subset of reasoning steps

Returns a list of `SimulatedPath` dataclass instances.

### `evaluate_paths(paths) → list[ScoredPath]`

Scores every path on three weighted axes:

| Axis | Weight | How |
|---|---|---|
| Feasibility | 0.35 | Inverse of step count |
| Success | 0.40 | Beta-sampled `success_prob` |
| Novelty | 0.25 | Mean edit-distance (SequenceMatcher) to peers |

Returns paths sorted best-first.

### `adapt(state, top_paths, merge_top_n=3) → AdaptResult`

Merges the top N paths into a single deduplicated plan, updates persistent
memory, and sets `fallback_needed = True` if post-boost confidence is still
below threshold.

### `invoke_ars(current_confidence, task_goal, ...) → AdaptResult | None`

**Main entry point.**  If `current_confidence >= threshold` → returns `None`
(nothing to do).  Otherwise runs the full pipeline:

    capture_state → simulate_paths → evaluate_paths → adapt

## Demo Output (abridged)

```
Scenario 1 — 10 branches, low confidence (0.4)
🏆  Top path ID : 3a8f1c…
📈  Confidence  : 0.72
⚠️   Fallback    : False

📋  Merged plan:
    1. Analyse sub-goal derived from 'Plan a 3-step cake recipe'
    2. Gather resources relevant to 'Plan a 3-step cake recipe'
    3. Validate intermediate result for branch 7
    ...
```

## Troubleshooting

| Issue | Fix |
|---|---|
| Slow on low-core machines | Reduce `num_branches` to 5 |
| Timeouts | Increase `sim_timeout` or reduce branches |
| Low novelty scores | Increase branches for more diversity |

## Files

| File | Purpose |
|---|---|
| `ars.py` | Core ARS class + worker |
| `demo.py` | 3-scenario demo script |
| `requirements.txt` | `numpy>=1.24` |
| `SKILL.md` | This file |
