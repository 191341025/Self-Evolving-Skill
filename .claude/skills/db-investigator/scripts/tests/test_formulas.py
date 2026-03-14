"""Tests for core.formulas module."""

import math
import pytest
from datetime import date, timedelta

from core.formulas import exponential_decay, bayesian_factor, effective_lambda, days_since


# ---------- exponential_decay ----------

class TestExponentialDecay:
    def test_t_zero_returns_one(self):
        """At t=0, decay should be 1.0 regardless of lambda."""
        assert exponential_decay(0.003, 0) == 1.0
        assert exponential_decay(0.05, 0) == 1.0

    def test_half_life_schema(self):
        """Schema lambda=0.003 -> half-life ~ 231 days."""
        lam = 0.003
        t_half = math.log(2) / lam  # ~231.05
        result = exponential_decay(lam, t_half)
        assert abs(result - 0.5) < 1e-6

    def test_large_t_approaches_zero(self):
        """For large t the decay value should be very close to zero."""
        result = exponential_decay(0.003, 10000)
        assert result < 1e-10

    def test_lambda_zero_always_one(self):
        """When lambda=0 the value never decays."""
        assert exponential_decay(0, 100) == 1.0
        assert exponential_decay(0, 0) == 1.0

    def test_negative_lambda_raises(self):
        with pytest.raises(ValueError):
            exponential_decay(-0.1, 10)

    def test_negative_t_raises(self):
        with pytest.raises(ValueError):
            exponential_decay(0.003, -1)


# ---------- bayesian_factor ----------

class TestBayesianFactor:
    def test_no_feedback(self):
        """(0,0) -> 1.0, no adjustment."""
        assert bayesian_factor(0, 0) == 1.0

    def test_positive_feedback_slows_decay(self):
        """(3,0) -> (0+1)/(3+1) = 0.25."""
        assert bayesian_factor(3, 0) == pytest.approx(0.25)

    def test_negative_feedback_speeds_decay(self):
        """(0,2) -> (2+1)/(0+1) = 3.0."""
        assert bayesian_factor(0, 2) == pytest.approx(3.0)

    def test_equal_feedback(self):
        """(1,1) -> 2/2 = 1.0."""
        assert bayesian_factor(1, 1) == 1.0

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            bayesian_factor(-1, 0)

    def test_negative_beta_raises(self):
        with pytest.raises(ValueError):
            bayesian_factor(0, -1)

    def test_float_alpha(self):
        """Float alpha (from soft signal): (0+1)/(0.3+1) = 1/1.3."""
        assert bayesian_factor(0.3, 0) == pytest.approx(1 / 1.3)

    def test_float_beta(self):
        """Float beta: (0.3+1)/(0+1) = 1.3."""
        assert bayesian_factor(0, 0.3) == pytest.approx(1.3)

    def test_float_both(self):
        """Mixed float: (0.6+1)/(1.3+1) = 1.6/2.3."""
        assert bayesian_factor(1.3, 0.6) == pytest.approx(1.6 / 2.3)


# ---------- effective_lambda ----------

class TestEffectiveLambda:
    def test_no_feedback_same_as_base(self):
        """With alpha=0, beta=0 the effective lambda equals the base."""
        assert effective_lambda(0.003, 0, 0) == pytest.approx(0.003)

    def test_positive_feedback_reduces_lambda(self):
        result = effective_lambda(0.003, 3, 0)
        assert result == pytest.approx(0.003 * 0.25)

    def test_negative_lambda_base_raises(self):
        with pytest.raises(ValueError):
            effective_lambda(-0.01, 0, 0)

    def test_negative_alpha_raises(self):
        with pytest.raises(ValueError):
            effective_lambda(0.003, -1, 0)


# ---------- days_since ----------

class TestDaysSince:
    def test_today_returns_zero(self, today_str):
        assert days_since(today_str) == 0

    def test_past_date_positive(self, days_ago):
        assert days_since(days_ago(10)) == 10
        assert days_since(days_ago(365)) == 365

    def test_future_date_raises(self):
        future = (date.today() + timedelta(days=5)).isoformat()
        with pytest.raises(ValueError, match="future"):
            days_since(future)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            days_since("01-01-2026")

    def test_garbage_raises(self):
        with pytest.raises(ValueError):
            days_since("not-a-date")
