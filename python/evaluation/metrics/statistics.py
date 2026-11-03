"""Small-sample statistics for the FlowSeq evaluation.

These helpers exist because the v1.0.0 report compared two 20-case arms by
subtracting percentages. A one-case difference on n=20 is not an effect; the
report should say so with an interval and an exact paired test instead of
leaving the reader to infer significance from a delta column.
"""
from __future__ import annotations

import math
from math import comb


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """Wilson score interval for a binomial proportion.

    Returns None when there is no denominator; a 0/0 rate is undefined, not 0%
    and not 100%.
    """
    if n <= 0:
        return None
    p = successes / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def mcnemar_exact(discordant_skill_only: int, discordant_baseline_only: int) -> float:
    """Two-sided exact McNemar p-value (binomial test on discordant pairs).

    ``discordant_skill_only`` is the number of cases correct only with the skill;
    ``discordant_baseline_only`` is the number correct only without it.
    """
    b = int(discordant_skill_only)
    c = int(discordant_baseline_only)
    if b < 0 or c < 0:
        raise ValueError("discordant counts must be non-negative")
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(0, min(b, c) + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def minimum_detectable_difference(
    n_per_arm: int,
    p: float = 0.5,
    alpha: float = 0.05,
    power: float = 0.8,
) -> float:
    """Approximate MDE for two independent proportions (normal approximation).

    This is a sensitivity calculation, not a paired-test power. It answers
    "with this many cases, what gap could we detect at all?" and is reported as
    a rough floor. For paired designs the true power depends on the discordance
    rate, which is why the report also gives the exact McNemar p-value.
    """
    if n_per_arm <= 0:
        raise ValueError("n_per_arm must be positive")
    if not 0.0 < p < 1.0:
        raise ValueError("p must be between 0 and 1")
    z_alpha = _norm_ppf(1.0 - alpha / 2.0)
    z_power = _norm_ppf(power)
    return (z_alpha + z_power) * math.sqrt(2.0 * p * (1.0 - p) / n_per_arm)


def _norm_ppf(q: float) -> float:
    """Inverse standard normal CDF via the Acklam rational approximation."""
    if not 0.0 < q < 1.0:
        raise ValueError("q must be between 0 and 1")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if q < plow:
        r = math.sqrt(-2.0 * math.log(q))
        return (((((c[0] * r + c[1]) * r + c[2]) * r + c[3]) * r + c[4]) * r + c[5]) / \
               ((((d[0] * r + d[1]) * r + d[2]) * r + d[3]) * r + 1.0)
    if q > phigh:
        r = math.sqrt(-2.0 * math.log(1.0 - q))
        return -(((((c[0] * r + c[1]) * r + c[2]) * r + c[3]) * r + c[4]) * r + c[5]) / \
               ((((d[0] * r + d[1]) * r + d[2]) * r + d[3]) * r + 1.0)
    r = q - 0.5
    s = r * r
    return (((((a[0] * s + a[1]) * s + a[2]) * s + a[3]) * s + a[4]) * s + a[5]) * r / \
           (((((b[0] * s + b[1]) * s + b[2]) * s + b[3]) * s + b[4]) * s + 1.0)
