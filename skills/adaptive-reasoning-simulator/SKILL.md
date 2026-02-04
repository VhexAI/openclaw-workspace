---
name: adaptive-reasoning-simulator
version: 2.0.0
description: >
  Boost agent intelligence by simulating multiple parallel reasoning paths,
  scoring them on feasibility / success / novelty, and adaptively merging the
  best into a single plan.  v2.0 adds error handling, input validation,
  optional Ollama LLM integration, configurable scoring weights, bounded memory,
  ThreadPool optimization, and benchmarking.
---

# Adaptive Reasoning Simulator (ARS) v2.0

> **TL;DR** — When your agent isn't sure what to do, ARS spins up N parallel
> "what-if" reasoning branches, scores them, and hands back a merged plan with
> a confidence boost. Now with optional LLM-powered reasoning via Ollama.

## What's New in v2.0

- **Error handling** — try-except on all external calls, graceful degradation
- **Input validation** — rejects bad confidence, empty goals, invalid weights
- **Ollama LLM integration** — optional real reasoning instead of templates
- **Configurable scoring weights** — no more magic numbers
- **ThreadPoolExecutor** for template mode — 10-50x faster than ProcessPool
- **Bounded memory** — deque with configurable max entries (default 100)
- **Floating-point fix** — no more `0.6929000000000001`
- **Benchmark method** — measure performance across branch counts
- **numpy optional** — falls back to stdlib `random` if numpy unavailable
- **23 passing tests** — validation, pipeline, memory, scoring, determinism

## Quick Start

```bash
pip install numpy          # recommended (optional — stdlib fallback exists)
python demo.py             # full 4-scenario demo + validation tests
python demo.py --benchmark # include performance benchmarks
python demo.py --llm       # enable Ollama LLM integration
```

```python
from ars import ARS

# Template mode (fast, no dependencies beyond numpy)
sim = ARS(num_branches=10, confidence_threshold=0.7, sim_timeout=30)
result = sim.invoke_ars(
    current_confidence=0.4,
    task_goal="Plan a 3-step cake recipe",
    current_context="Home kitchen, basic ingredients",
    past_actions=["Checked pantry", "Found flour and sugar"],
)
print(result.merged_plan)

# LLM mode (richer reasoning, requires Ollama running)
sim = ARS(llm_backend="ollama", llm_model="llama3.2")
result = sim.invoke_ars(
    current_confidence=0.15,
    task_goal="Analyze smart contract reentrancy vulnerability",
)
```

## Class API

### `ARS(num_branches=10, confidence_threshold=0.7, sim_timeout=30, ...)`

| Param | Default | Purpose |
|---|---|---|
| `num_branches` | 10 | Parallel reasoning paths to simulate |
| `confidence_threshold` | 0.7 | Confidence below this triggers ARS |
| `sim_timeout` | 30.0 | Seconds before simulation times out |
| `scoring_weights` | `{f:0.35, s:0.40, n:0.25}` | Custom axis weights (must sum to 1.0) |
| `max_memory` | 100 | Maximum memory entries before rotation |
| `llm_backend` | None | `"ollama"` or None for template-only |
| `llm_model` | `"llama3.2"` | Ollama model name |
| `llm_base_url` | `http://localhost:11434` | Ollama API URL |

### `invoke_ars(current_confidence, task_goal, ...) → AdaptResult | None`

**Main entry point.** Returns `None` if confidence is sufficient. Otherwise
runs: `capture_state → simulate_paths → evaluate_paths → adapt`

Raises `ARSValidationError` on bad inputs. Returns fallback `AdaptResult` on
internal pipeline errors (never crashes).

### `benchmark(task_goal, num_runs=5, branches_list) → list[BenchmarkResult]`

Run ARS multiple times with different branch counts. Returns timing and quality
metrics for parameter tuning.

### Scoring Axes

| Axis | Default Weight | How |
|---|---|---|
| Feasibility | 0.35 | Inverse of step count (fewer → more feasible) |
| Success | 0.40 | Beta-sampled probability (LLM paths get +0.15 boost) |
| Novelty | 0.25 | Mean edit-distance to peer paths via SequenceMatcher |

### Exploration Mode

Weight novelty higher for creative/exploratory tasks:

```python
sim = ARS(scoring_weights={"feasibility": 0.20, "success": 0.30, "novelty": 0.50})
```

## Demo Scenarios

1. **Simple goal** — 10 branches, cake recipe, template mode
2. **Complex crypto bounty** — 10 branches, smart contract vulnerability, high uncertainty
3. **Novelty-weighted** — exploration mode for IoT consensus design
4. **High confidence** — ARS correctly skips when not needed
5. **Validation tests** — demonstrates input rejection
6. **Benchmarks** (optional) — timing across 5/10/20 branches

## Benchmark Results (template mode, no LLM)

| Branches | Avg Time | Confidence | Steps |
|---|---|---|---|
| 5 | 0.006s | 0.80 | 14 |
| 10 | 0.022s | 0.78 | 12 |
| 20 | 0.096s | 0.77 | 12 |

## Testing

```bash
python -m pytest test_ars.py -v
# 23 tests: validation (7), pipeline (8), memory (3), scoring (2), determinism (1), misc (2)
```

## Files

| File | Purpose |
|---|---|
| `ars.py` | Core ARS class v2.0 + worker + Ollama integration |
| `demo.py` | Multi-scenario demo with benchmarks |
| `test_ars.py` | 23-test pytest suite |
| `requirements.txt` | `numpy>=1.24` |
| `REVIEW.md` | Detailed code review (Opus analysis) |
| `CHANGELOG.md` | Version history |
| `SKILL.md` | This file |
