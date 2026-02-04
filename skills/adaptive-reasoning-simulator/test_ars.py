#!/usr/bin/env python3
"""
Tests for ARS v2.0
==================
Run: python -m pytest test_ars.py -v
"""

import pytest
from ars import ARS, ARSValidationError, SimulatedPath, ScoredPath, AdaptResult


# ──────────────────────────────────────────────────────────
# Input validation
# ──────────────────────────────────────────────────────────

class TestValidation:
    def test_negative_confidence_rejected(self):
        sim = ARS()
        with pytest.raises(ARSValidationError, match="must be in"):
            sim.invoke_ars(current_confidence=-0.1, task_goal="test")

    def test_confidence_above_one_rejected(self):
        sim = ARS()
        with pytest.raises(ARSValidationError, match="must be in"):
            sim.invoke_ars(current_confidence=1.5, task_goal="test")

    def test_empty_goal_rejected(self):
        sim = ARS()
        with pytest.raises(ARSValidationError, match="non-empty string"):
            sim.invoke_ars(current_confidence=0.3, task_goal="")

    def test_whitespace_goal_rejected(self):
        sim = ARS()
        with pytest.raises(ARSValidationError, match="non-empty string"):
            sim.invoke_ars(current_confidence=0.3, task_goal="   ")

    def test_negative_branches_rejected(self):
        with pytest.raises(ARSValidationError, match="must be >= 1"):
            ARS(num_branches=-1)

    def test_invalid_scoring_weights_rejected(self):
        with pytest.raises(ARSValidationError, match="must sum to 1.0"):
            ARS(scoring_weights={"feasibility": 0.5, "success": 0.5, "novelty": 0.5})

    def test_missing_scoring_key_rejected(self):
        with pytest.raises(ARSValidationError, match="missing key"):
            ARS(scoring_weights={"feasibility": 0.5, "success": 0.5})


# ──────────────────────────────────────────────────────────
# Core pipeline
# ──────────────────────────────────────────────────────────

class TestPipeline:
    def test_high_confidence_returns_none(self):
        sim = ARS()
        result = sim.invoke_ars(current_confidence=0.9, task_goal="test")
        assert result is None

    def test_low_confidence_returns_result(self):
        sim = ARS(num_branches=3)
        result = sim.invoke_ars(
            current_confidence=0.3,
            task_goal="Plan a test",
            current_context="Test context",
            past_actions=["step 1"],
        )
        assert isinstance(result, AdaptResult)
        assert len(result.merged_plan) > 0
        assert 0.0 <= result.confidence_after <= 1.0

    def test_capture_state(self):
        sim = ARS()
        state = sim.capture_state("my goal", "context", ["action1"])
        assert state["task_goal"] == "my goal"
        assert state["current_context"] == "context"
        assert state["past_actions"] == ["action1"]
        assert "id" in state
        assert "timestamp" in state

    def test_simulate_paths_count(self):
        sim = ARS(num_branches=5)
        state = sim.capture_state("test", "ctx")
        paths = sim.simulate_paths(state)
        assert len(paths) == 5
        for p in paths:
            assert isinstance(p, SimulatedPath)
            assert len(p.steps) >= 3

    def test_evaluate_paths_sorted(self):
        sim = ARS(num_branches=5)
        state = sim.capture_state("test", "ctx")
        paths = sim.simulate_paths(state)
        scored = sim.evaluate_paths(paths)
        assert len(scored) == 5
        # Verify sorted descending by total_score
        for i in range(len(scored) - 1):
            assert scored[i].total_score >= scored[i + 1].total_score

    def test_evaluate_empty_paths(self):
        sim = ARS()
        scored = sim.evaluate_paths([])
        assert scored == []

    def test_adapt_empty_paths(self):
        sim = ARS()
        state = sim.capture_state("test", "ctx")
        result = sim.adapt(state, [])
        assert result.fallback_needed is True
        assert result.top_path_id == "none"

    def test_confidence_after_rounded(self):
        """Verify no floating point artifacts like 0.6929000000000001."""
        sim = ARS(num_branches=10)
        result = sim.invoke_ars(current_confidence=0.4, task_goal="test")
        assert result is not None
        # Should have at most 4 decimal places
        str_conf = str(result.confidence_after)
        if "." in str_conf:
            decimals = len(str_conf.split(".")[1])
            assert decimals <= 4, f"Too many decimals: {result.confidence_after}"


# ──────────────────────────────────────────────────────────
# Memory management
# ──────────────────────────────────────────────────────────

class TestMemory:
    def test_memory_bounded(self):
        sim = ARS(num_branches=2, max_memory=3)
        for i in range(5):
            sim.invoke_ars(current_confidence=0.1, task_goal=f"task {i}")
        assert len(sim.memory) <= 3

    def test_memory_populated(self):
        sim = ARS(num_branches=2)
        sim.invoke_ars(current_confidence=0.3, task_goal="test")
        mem = sim.get_memory()
        assert len(mem) == 1
        assert "goal" in mem[0]
        assert mem[0]["goal"] == "test"

    def test_simulation_log_populated(self):
        sim = ARS(num_branches=2)
        sim.invoke_ars(current_confidence=0.3, task_goal="test")
        log = sim.get_simulation_log()
        assert len(log) == 1
        assert "num_paths" in log[0]
        assert log[0]["num_paths"] == 2


# ──────────────────────────────────────────────────────────
# Scoring weights
# ──────────────────────────────────────────────────────────

class TestScoring:
    def test_custom_weights_applied(self):
        # Novelty-heavy weighting should produce different rankings
        sim_default = ARS(num_branches=5)
        sim_novelty = ARS(
            num_branches=5,
            scoring_weights={"feasibility": 0.1, "success": 0.1, "novelty": 0.8},
        )
        state = sim_default.capture_state("test goal", "ctx")
        paths = sim_default.simulate_paths(state)

        scored_default = sim_default.evaluate_paths(paths)
        scored_novelty = sim_novelty.evaluate_paths(paths)

        # Same paths, different weights → potentially different top path
        # At minimum, scores should differ
        default_scores = [s.total_score for s in scored_default]
        novelty_scores = [s.total_score for s in scored_novelty]
        assert default_scores != novelty_scores

    def test_single_path_evaluation(self):
        sim = ARS(num_branches=1)
        state = sim.capture_state("test", "ctx")
        paths = sim.simulate_paths(state)
        scored = sim.evaluate_paths(paths)
        assert len(scored) == 1
        assert scored[0].novelty == 1.0  # single path = max novelty


# ──────────────────────────────────────────────────────────
# Determinism
# ──────────────────────────────────────────────────────────

class TestDeterminism:
    def test_same_goal_same_paths(self):
        """Same goal should produce identical paths (deterministic seeding)."""
        sim1 = ARS(num_branches=5)
        sim2 = ARS(num_branches=5)
        state1 = sim1.capture_state("identical goal", "ctx")
        state2 = sim2.capture_state("identical goal", "ctx")
        paths1 = sim1.simulate_paths(state1)
        paths2 = sim2.simulate_paths(state2)
        # Path IDs should match (sorted — as_completed order is non-deterministic)
        ids1 = sorted(p.path_id for p in paths1)
        ids2 = sorted(p.path_id for p in paths2)
        assert ids1 == ids2


# ──────────────────────────────────────────────────────────
# Repr and misc
# ──────────────────────────────────────────────────────────

class TestMisc:
    def test_repr(self):
        sim = ARS(num_branches=5, llm_backend="ollama")
        r = repr(sim)
        assert "branches=5" in r
        assert "llm=ollama" in r

    def test_repr_no_llm(self):
        sim = ARS()
        r = repr(sim)
        assert "llm=none" in r


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
