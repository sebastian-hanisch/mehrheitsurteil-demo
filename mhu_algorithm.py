"""Kern: Wie oft liegt eine Mehrheit richtig? Alle Wahrscheinlichkeiten werden EXAKT gerechnet (Binomialverteilung, Beta-Binomialverteilung, Faltung), nicht simuliert.

Zwei Entscheidungsmöglichkeiten, die erste ist die richtige. Ein Gutachter urteilt richtig mit der Trefferquote q. Gutachterzahl n ist ungerade (kein Unentschieden), die einfache
Mehrheit entscheidet. Beim gewichteten Votum mit ganzzahligen Gewichten zählt ein Gleichstand der gewichteten Summen halb.
"""

import math

import numpy as np
from scipy.stats import beta, betabinom, binom

import mhu_constants as C


def check_odd(n: int) -> int:
    if n < 1 or n % 2 == 0:
        raise ValueError(f"Gutachterzahl muss ungerade und positiv sein: {n}")
    return n


def majority_independent(n: int, q: float) -> float:
    """P(mehr als n/2 von n unabhängigen Gutachtern mit Trefferquote q liegen richtig)."""
    check_odd(n)
    return float(binom.sf(n // 2, n, q))


def majority_common_signal(n: int, q: float, rho: float) -> float:
    """Mit Wahrscheinlichkeit rho folgen alle einem gemeinsamen Hinweis (richtig mit Wahrscheinlichkeit q), sonst unabhängig."""
    return rho * q + (1 - rho) * majority_independent(n, q)


def beta_params(q: float, sd: float) -> tuple[float, float]:
    """Parameter (a, b) der Beta-Verteilung mit Mittel q und Standardabweichung sd; ValueError, wenn sd zu groß ist (sd² ≥ q (1 − q))."""
    kappa = q * (1 - q) / sd**2 - 1
    if kappa <= 0:
        raise ValueError(f"Streuung {sd} zu groß für q = {q}")
    return q * kappa, (1 - q) * kappa


def majority_difficulty(n: int, q: float, sd: float) -> float:
    """Die Trefferquote p hängt vom Fall ab (Beta-verteilt mit Mittel q, Standardabweichung sd); innerhalb eines Falls urteilen die Gutachter unabhängig (Beta-Binomial)."""
    check_odd(n)
    if sd == 0:
        return majority_independent(n, q)
    a, b = beta_params(q, sd)
    return float(betabinom.sf(n // 2, n, a, b))


def limit_independent(q: float) -> float:
    """Grenzwert für n → ∞ bei unabhängigen Gutachtern: 1 für q > 1/2, 1/2 bei q = 1/2, 0 für q < 1/2."""
    return 1.0 if q > 0.5 else (0.5 if q == 0.5 else 0.0)


def limit_common_signal(q: float, rho: float) -> float:
    return rho * q + (1 - rho) * limit_independent(q)


def limit_difficulty(q: float, sd: float) -> float:
    """Grenzwert bei Fallschwierigkeit: die Wahrscheinlichkeit, dass ein Fall „mehrheitlich lösbar“ ist (p > 1/2)."""
    if sd == 0:
        return limit_independent(q)
    a, b = beta_params(q, sd)
    return float(beta.sf(0.5, a, b))


def poisson_binomial_curve(qs) -> dict:
    """Mehrheit richtig für die ersten k Gutachter (k ungerade), die Trefferquoten qs nacheinander dazugenommen; exakte Faltung der Verteilung der Zahl der Richtigen."""
    dist = np.array([1.0])
    out = {}
    for k, q in enumerate(qs, start=1):
        new = np.zeros(k + 1)
        new[:k] += dist * (1 - q)
        new[1:] += dist * q
        dist = new
        if k % 2 == 1:
            out[k] = float(dist[k // 2 + 1:].sum())
    return out


def integer_weights(qs) -> list:
    """Gewicht je Gutachter: round(100 · ln(q / (1 − q))); unter q = 1/2 negativ (dessen Votum wird umgedreht)."""
    return [int(round(C.WEIGHT_SCALE * math.log(q / (1 - q)))) for q in qs]


def weighted_curve(qs, weights) -> dict:
    """Gewichtete Mehrheit richtig für die ersten k Gutachter (k ungerade): die Summe der gewichteten Stimmen (+w bei richtig, −w bei falsch) größer 0; Summe 0 zählt halb. Exakte Faltung."""
    total = sum(abs(w) for w in weights)
    size = 2 * total + 1
    dist = np.zeros(size)
    dist[total] = 1.0
    out = {}
    for k, (q, w) in enumerate(zip(qs, weights), start=1):
        new = np.zeros(size)
        for shift, p in ((w, q), (-w, 1 - q)):
            lo_new, hi_new = max(shift, 0), size + min(shift, 0)
            new[lo_new:hi_new] += p * dist[lo_new - shift:hi_new - shift]
        dist = new
        if k % 2 == 1:
            out[k] = float(dist[total + 1:].sum() + 0.5 * dist[total])
    return out


def needed_voters(target: float, prob, limit: float = 1.0):
    """Kleinste ungerade Gutachterzahl, bei der prob(n) ≥ target gilt (prob wächst mit n).

    None, wenn der Grenzwert `limit` unter dem Ziel liegt (dann wird es nie erreicht); math.inf, wenn das Ziel bis SEARCH_CAP Gutachter nicht erreicht wird, obwohl der Grenzwert es erlaubt.
    Suche: Verdoppeln bis zum Treffer, dann Halbieren über die ungeraden Zahlen n = 2k + 1."""
    if limit < target - 1e-12:
        return None
    if prob(1) >= target:
        return 1
    lo, hi = 1, 3
    while prob(hi) < target:
        lo, hi = hi, 2 * hi + 1
        if hi > C.SEARCH_CAP:
            return math.inf
    k_lo, k_hi = (lo + 1) // 2, (hi - 1) // 2                  # gesucht: kleinstes k mit prob(2k + 1) ≥ target; k_hi erfüllt es
    while k_lo < k_hi:
        mid = (k_lo + k_hi) // 2
        if prob(2 * mid + 1) >= target:
            k_hi = mid
        else:
            k_lo = mid + 1
    return 2 * k_lo + 1
