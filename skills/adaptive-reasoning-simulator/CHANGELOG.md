# Changelog

## [2.0.0] — 2026-02-04

### Added
- **Error handling**: try-except around ProcessPool/ThreadPool execution, Ollama HTTP calls, SequenceMatcher — pipeline never crashes, returns fallback `AdaptResult` on internal errors
- **Input validation**: `ARSValidationError` for bad confidence values, empty goals, invalid scoring weights, negative branch counts
- **Ollama LLM integration**: `llm_backend="ollama"` enables real LLM reasoning for path generation via `/api/generate` endpoint. Falls back to templates if Ollama unreachable
- **Configurable scoring weights**: `scoring_weights={"feasibility": 0.35, "success": 0.40, "novelty": 0.25}` — must sum to 1.0
- **Bounded memory**: `deque(maxlen=max_memory)` replaces unbounded `list` — prevents memory leaks in long-running agents
- **ThreadPoolExecutor** for template mode — 10-50x faster than ProcessPoolExecutor for non-LLM workloads
- **Benchmark method**: `benchmark(task_goal, num_runs, branches_list)` for parameter tuning
- **numpy optional**: Falls back to `random.betavariate()` + `random.sample()` if numpy unavailable
- **BenchmarkResult dataclass**: Structured benchmark output
- **23 pytest tests**: Validation (7), Pipeline (8), Memory (3), Scoring (2), Determinism (1), Misc (2)
- **Complex demo scenario**: Smart contract vulnerability analysis with high uncertainty
- **Novelty-weighted scenario**: Exploration mode for creative tasks
- **REVIEW.md**: Detailed Opus-level code review with prioritized findings

### Fixed
- **Floating-point artifact**: `confidence_after` now uses `round(..., 4)` — no more `0.6929000000000001`
- **Confidence boost**: Replaced arbitrary `+0.25` with scaled boost `min(0.35, best_score * 0.6)` — better scores earn bigger boosts
- **Log interleaving**: Separated logging from print output flow

### Changed
- `self.memory` and `self.simulation_log` changed from `list` to `deque(maxlen=100)`
- `simulate_paths()` uses `as_completed()` instead of `pool.map()` for better error isolation
- `_simulate_single_path` accepts `llm_config` tuple element for LLM-powered path generation
- Demo expanded from 3 to 6 scenarios (simple, complex, exploration, skip, validation, benchmarks)

## [1.0.0] — 2026-02-04

### Added
- Initial ARS implementation: capture → simulate → evaluate → adapt pipeline
- ProcessPoolExecutor-based parallel simulation
- Beta-distributed success probability (numpy)
- SequenceMatcher-based novelty scoring
- 3 weighted scoring axes: feasibility (0.35), success (0.40), novelty (0.25)
- Persistent memory and simulation log
- 3-scenario demo (low/mid confidence + skip)
- SKILL.md documentation
