"""
Atomic formula layer for the confidence decay model.

All functions are pure (no side effects, no I/O) except days_since which
reads the current date. Composition of formulas happens in models.py.
"""

import math
from datetime import date


def exponential_decay(lambda_val: float, t: float) -> float:
    """Pure exponential decay: e^(-lambda * t).

    Args:
        lambda_val: Decay rate (>= 0).
        t: Elapsed time in days (>= 0).

    Returns:
        Decay factor in the range (0, 1].

    Raises:
        ValueError: If lambda_val < 0 or t < 0.
    """
    if lambda_val < 0:
        raise ValueError(f"lambda_val must be >= 0, got {lambda_val}")
    if t < 0:
        raise ValueError(f"t must be >= 0, got {t}")
    return math.exp(-lambda_val * t)


def bayesian_factor(alpha: int, beta: int) -> float:
    """Bayesian adjustment factor: (beta + 1) / (alpha + 1).

    Encodes feedback history as a multiplier on the decay rate:
      - No feedback (alpha=0, beta=0) -> 1.0 (no adjustment)
      - More successes -> factor < 1 (slower decay)
      - More failures  -> factor > 1 (faster decay)

    Args:
        alpha: Number of positive/success feedback events (>= 0).
        beta:  Number of negative/failure feedback events (>= 0).

    Returns:
        Adjustment factor (positive float).

    Raises:
        ValueError: If alpha < 0 or beta < 0.
    """
    if alpha < 0:
        raise ValueError(f"alpha must be >= 0, got {alpha}")
    if beta < 0:
        raise ValueError(f"beta must be >= 0, got {beta}")
    return (beta + 1) / (alpha + 1)


def effective_lambda(lambda_base: float, alpha: int, beta: int) -> float:
    """Effective decay rate adjusted by Bayesian feedback.

    effective_lambda = lambda_base * bayesian_factor(alpha, beta)

    Args:
        lambda_base: Base decay rate (>= 0).
        alpha: Number of positive/success feedback events (>= 0).
        beta:  Number of negative/failure feedback events (>= 0).

    Returns:
        Adjusted decay rate (>= 0).

    Raises:
        ValueError: If any argument is negative.
    """
    if lambda_base < 0:
        raise ValueError(f"lambda_base must be >= 0, got {lambda_base}")
    # alpha/beta validation delegated to bayesian_factor
    return lambda_base * bayesian_factor(alpha, beta)


def days_since(confirmed_date: str) -> int:
    """Calculate the number of days from confirmed_date to today.

    Args:
        confirmed_date: Date string in YYYY-MM-DD format.

    Returns:
        Non-negative integer representing elapsed days.

    Raises:
        ValueError: If confirmed_date is not a valid YYYY-MM-DD string
                     or represents a future date.
    """
    try:
        d = date.fromisoformat(confirmed_date)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"confirmed_date must be a valid YYYY-MM-DD string, got {confirmed_date!r}"
        ) from exc

    delta = (date.today() - d).days
    if delta < 0:
        raise ValueError(
            f"confirmed_date {confirmed_date} is in the future "
            f"({-delta} days ahead)"
        )
    return delta
