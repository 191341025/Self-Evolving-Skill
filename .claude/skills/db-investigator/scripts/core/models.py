"""
Composition model layer for the confidence decay model.

Combines atomic formulas from core.formulas into higher-level confidence
calculations. No I/O — all state is passed in as arguments.
"""

from .formulas import days_since, effective_lambda, exponential_decay

# Lambda base values per knowledge type (daily decay rate)
LAMBDA_TABLE: dict[str, float] = {
    "schema":          0.003,   # t_half ~ 231 days
    "business_rule":   0.008,   # t_half ~  87 days
    "tool_experience": 0.005,   # t_half ~ 139 days
    "query_pattern":   0.015,   # t_half ~  46 days
    "data_range":      0.035,   # t_half ~  20 days
    "data_snapshot":   0.050,   # t_half ~  14 days
}

# Confidence thresholds
TRUST_THRESHOLD: float = 0.8
VERIFY_THRESHOLD: float = 0.5


def confidence(
    knowledge_type: str,
    confirmed_date: str,
    alpha: int = 0,
    beta: int = 0,
    c0: float = 1.0,
) -> float:
    """Calculate confidence C(t) for a knowledge entry.

    C(t) = C0 * e^(-lambda_eff * t)
    where lambda_eff = lambda_base * bayesian_factor(alpha, beta)
          t = days_since(confirmed_date)

    Args:
        knowledge_type: Must be a key in LAMBDA_TABLE.
        confirmed_date: YYYY-MM-DD format string.
        alpha: Number of success feedback events (>= 0).
        beta: Number of failure feedback events (>= 0).
        c0: Initial confidence (default 1.0). Set by invalidate to 0.1.

    Returns:
        Confidence value in the range [0.0, 1.0].

    Raises:
        ValueError: If knowledge_type is not in LAMBDA_TABLE.
    """
    if knowledge_type not in LAMBDA_TABLE:
        raise ValueError(
            f"Unknown knowledge_type {knowledge_type!r}. "
            f"Valid types: {sorted(LAMBDA_TABLE.keys())}"
        )

    lambda_base = LAMBDA_TABLE[knowledge_type]
    t = days_since(confirmed_date)
    lambda_eff = effective_lambda(lambda_base, alpha, beta)
    return c0 * exponential_decay(lambda_eff, t)


def classify_confidence(c_value: float) -> str:
    """Classify a confidence value into a trust tier.

    Args:
        c_value: Confidence score (caller is responsible for valid range).

    Returns:
        "TRUST"      if c_value >= 0.8
        "VERIFY"     if 0.5 <= c_value < 0.8
        "REVALIDATE" if c_value < 0.5
    """
    if c_value >= TRUST_THRESHOLD:
        return "TRUST"
    if c_value >= VERIFY_THRESHOLD:
        return "VERIFY"
    return "REVALIDATE"
