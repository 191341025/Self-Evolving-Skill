"""Tests for core.models module."""

import pytest
from datetime import date, timedelta

from core.models import (
    LAMBDA_TABLE,
    TRUST_THRESHOLD,
    VERIFY_THRESHOLD,
    confidence,
    classify_confidence,
)


# ---------- Constants ----------

class TestConstants:
    def test_lambda_table_has_six_types(self):
        assert len(LAMBDA_TABLE) == 6

    def test_expected_types_present(self):
        expected = {
            "schema", "business_rule", "tool_experience",
            "query_pattern", "data_range", "data_snapshot",
        }
        assert set(LAMBDA_TABLE.keys()) == expected

    def test_thresholds(self):
        assert TRUST_THRESHOLD == 0.8
        assert VERIFY_THRESHOLD == 0.5


# ---------- confidence ----------

class TestConfidence:
    def test_today_confirmed_returns_one(self, today_str):
        """A knowledge entry confirmed today should have confidence 1.0."""
        result = confidence("schema", today_str)
        assert result == pytest.approx(1.0)

    def test_half_life_schema(self, days_ago):
        """After ~231 days, schema confidence should be ~0.5."""
        import math
        lam = LAMBDA_TABLE["schema"]
        t_half = math.log(2) / lam
        d = (date.today() - timedelta(days=int(round(t_half)))).isoformat()
        result = confidence("schema", d)
        assert abs(result - 0.5) < 0.02  # allow small rounding from int days

    def test_alpha_slows_decay(self, days_ago):
        """Positive feedback (alpha) should slow decay -> higher confidence."""
        base = confidence("schema", days_ago(100))
        boosted = confidence("schema", days_ago(100), alpha=5, beta=0)
        assert boosted > base

    def test_beta_speeds_decay(self, days_ago):
        """Negative feedback (beta) should speed decay -> lower confidence."""
        base = confidence("schema", days_ago(100))
        penalized = confidence("schema", days_ago(100), alpha=0, beta=5)
        assert penalized < base

    def test_invalid_type_raises(self, today_str):
        with pytest.raises(ValueError, match="Unknown knowledge_type"):
            confidence("nonexistent_type", today_str)

    def test_all_types_work(self, today_str):
        """All six types should return 1.0 when confirmed today."""
        for kt in LAMBDA_TABLE:
            assert confidence(kt, today_str) == pytest.approx(1.0)


# ---------- classify_confidence ----------

class TestClassifyConfidence:
    def test_trust(self):
        assert classify_confidence(0.9) == "TRUST"
        assert classify_confidence(1.0) == "TRUST"

    def test_trust_boundary(self):
        """Exactly 0.8 should be TRUST."""
        assert classify_confidence(0.8) == "TRUST"

    def test_verify(self):
        assert classify_confidence(0.7) == "VERIFY"
        assert classify_confidence(0.6) == "VERIFY"

    def test_verify_boundary(self):
        """Exactly 0.5 should be VERIFY."""
        assert classify_confidence(0.5) == "VERIFY"

    def test_revalidate(self):
        assert classify_confidence(0.49) == "REVALIDATE"
        assert classify_confidence(0.0) == "REVALIDATE"
