"""Orakel-Test mehrheitsurteil-demo: jede Wahrscheinlichkeit gegen einen ANDEREN Rechenweg.

* Aufzählung: alle 2^n Urteilsmuster von n ≤ 11 Gutachtern mit exakten Brüchen (statt Binomial-, Beta-Binomial- und Faltungsformeln).
* Beta-Binomial: die Wahrscheinlichkeitsfunktion mit ganzzahligen Beta-Parametern aus Fakultäten (statt scipy).
* Erzählung der Modelle: Stichproben aus der beschriebenen Entstehung der Urteile (Gutachter ziehen, Fall ziehen, gemeinsamen Hinweis ziehen) mit festem Zufalls-Seed, Bänder um die exakten Werte.
* Eigenschaften: Spiegelung q ↔ 1 − q, Monotonie in n, Annäherung an die Grenzwerte.
"""

import itertools
import math
from fractions import Fraction

import numpy as np
import pytest

import mhu_algorithm as A
import mhu_constants as C
import mhu_scenario as S


def frac(x):
    return Fraction(x).limit_denominator(10**9)


def enumerate_majority(qs, weights=None):
    """Wahrscheinlichkeit, dass die (gewichtete) Mehrheit richtig liegt, durch Aufzählung aller 2^n Urteilsmuster; Summe 0 zählt halb."""
    n = len(qs)
    w = weights or [1] * n
    total = Fraction(0)
    for pattern in itertools.product((1, -1), repeat=n):
        p = Fraction(1)
        for x, q in zip(pattern, qs):
            p *= q if x == 1 else 1 - q
        s = sum(wi * x for wi, x in zip(w, pattern))
        total += p * (1 if s > 0 else Fraction(1, 2) if s == 0 else 0)
    return total


# --- Aufzählung ------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 3, 5, 7, 9, 11])
@pytest.mark.parametrize("q", [Fraction(2, 5), Fraction(1, 2), Fraction(11, 20), Fraction(3, 5), Fraction(7, 10)])
def test_independent_matches_enumeration(n, q):
    assert A.majority_independent(n, float(q)) == pytest.approx(float(enumerate_majority([q] * n)), abs=1e-12)


@pytest.mark.parametrize("n", [1, 3, 7, 11])
@pytest.mark.parametrize("rho", [Fraction(0), Fraction(1, 10), Fraction(3, 10), Fraction(1, 2)])
def test_common_signal_matches_the_mixture_of_enumerations(n, rho):
    q = Fraction(3, 5)
    want = rho * q + (1 - rho) * enumerate_majority([q] * n)                        # mit Wahrscheinlichkeit ρ folgen alle dem Hinweis: richtig mit q; sonst unabhängig
    assert A.majority_common_signal(n, float(q), float(rho)) == pytest.approx(float(want), abs=1e-12)


def beta_binomial_majority(n, a, b):
    """P(X > n/2) für X ~ Beta-Binomial(n, a, b) mit ganzen a, b aus Fakultäten: C(n, k) B(k + a, n − k + b) / B(a, b), B(x, y) = (x − 1)! (y − 1)! / (x + y − 1)!."""
    beta = lambda x, y: Fraction(math.factorial(x - 1) * math.factorial(y - 1), math.factorial(x + y - 1))
    return sum(math.comb(n, k) * beta(k + a, n - k + b) / beta(a, b) for k in range(n // 2 + 1, n + 1))


@pytest.mark.parametrize("n", [1, 3, 5, 11, 51])
@pytest.mark.parametrize("a,b", [(1, 1), (2, 1), (3, 2), (2, 3), (4, 4), (6, 3)])
def test_difficulty_matches_the_beta_binomial_from_factorials(n, a, b):
    q = a / (a + b)
    sd = math.sqrt(q * (1 - q) / (a + b + 1))                                         # κ = a + b
    assert A.majority_difficulty(n, q, sd) == pytest.approx(float(beta_binomial_majority(n, a, b)), abs=1e-9)


@pytest.mark.parametrize("a,b", [(2, 1), (3, 2), (6, 3), (1, 1)])
def test_difficulty_limit_matches_the_beta_distribution_function(a, b):
    """P(p > 1/2) für ganze a, b über die Binomialsumme: 1 − I_{1/2}(a, b) = P(Bin(a + b − 1, 1/2) ≤ a − 1)."""
    q = a / (a + b)
    sd = math.sqrt(q * (1 - q) / (a + b + 1))
    want = sum(math.comb(a + b - 1, k) for k in range(a)) / 2 ** (a + b - 1)
    assert A.limit_difficulty(q, sd) == pytest.approx(want, abs=1e-12)


@pytest.mark.parametrize("delta,n", [(0.0, 7), (0.1, 7), (0.2, 9), (0.3, 11), (0.3, 5)])
def test_mixed_and_weighted_match_the_enumeration(delta, n):
    qs = list(S.competences(0.6, delta, n))
    exact = [frac(x) for x in qs]
    assert A.poisson_binomial_curve(qs)[n] == pytest.approx(float(enumerate_majority([Fraction(x) for x in qs])), abs=1e-12)
    w = A.integer_weights(qs)
    assert A.weighted_curve(qs, w)[n] == pytest.approx(float(enumerate_majority([Fraction(x) for x in qs], w)), abs=1e-12)
    assert len(exact) == n


def test_the_enumeration_oracle_is_not_vacuous():
    """Verschiedene Mechanismen geben verschiedene Werte, und das Gewichten ändert etwas, sobald die Gutachter verschieden gut sind (sonst prüften die Vergleiche nichts)."""
    n = 9
    qs = list(S.competences(0.6, 0.3, n))
    simple = float(enumerate_majority([Fraction(x) for x in qs]))
    weighted = float(enumerate_majority([Fraction(x) for x in qs], A.integer_weights(qs)))
    assert weighted > simple + 0.05
    assert A.majority_common_signal(n, 0.6, 0.3) < A.majority_independent(n, 0.6) - 0.03 and A.majority_difficulty(n, 0.6, 0.15) < A.majority_independent(n, 0.6) - 0.02


# --- Stichproben der beschriebenen Entstehung ------------------------------------------------------------------------------------------------

SAMPLES = 200_000
BAND = 0.006                                      # Standardabweichung höchstens 0,0011; fünf Standardabweichungen


def rng(seed):
    return np.random.default_rng(seed)


def test_independent_story():
    n, q = 11, 0.55
    x = rng(1).random((SAMPLES, n)) < q                                   # jeder Gutachter richtig mit Wahrscheinlichkeit q
    assert (x.sum(axis=1) > n / 2).mean() == pytest.approx(A.majority_independent(n, q), abs=BAND)


def test_common_signal_story():
    n, q, rho = 11, 0.6, 0.3
    r = rng(2)
    follow = r.random(SAMPLES) < rho                                      # in diesem Anteil der Fälle folgen alle dem Hinweis
    signal_right = r.random(SAMPLES) < q
    own = r.random((SAMPLES, n)) < q
    right = np.where(follow, signal_right, own.sum(axis=1) > n / 2)
    assert right.mean() == pytest.approx(A.majority_common_signal(n, q, rho), abs=BAND)


def test_difficulty_story():
    n, q, sd = 11, 0.6, 0.15
    a, b = A.beta_params(q, sd)
    r = rng(3)
    p = r.beta(a, b, size=SAMPLES)                                        # Trefferquote des Falls
    right = r.binomial(n, p) > n / 2                                      # innerhalb des Falls unabhängige Gutachter
    assert right.mean() == pytest.approx(A.majority_difficulty(n, q, sd), abs=BAND)
    assert (p > 0.5).mean() == pytest.approx(A.limit_difficulty(q, sd), abs=BAND)


def test_mixed_and_weighted_story():
    n = 15
    qs = S.competences(0.6, 0.25, n)
    r = rng(4)
    x = np.where(r.random((SAMPLES, n)) < qs, 1, -1)
    assert (x.sum(axis=1) > 0).mean() == pytest.approx(A.poisson_binomial_curve(list(qs))[n], abs=BAND)
    w = np.array(A.integer_weights(list(qs)))
    s = (x * w).sum(axis=1)
    got = (s > 0).mean() + 0.5 * (s == 0).mean()
    assert got == pytest.approx(A.weighted_curve(list(qs), list(w))[n], abs=BAND)


# --- Eigenschaften ---------------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("q", [0.51, 0.55, 0.6, 0.7])
def test_independent_majority_grows_with_n_above_one_half_and_falls_below(q):
    ns = list(range(1, 400, 2))
    up = [A.majority_independent(n, q) for n in ns]
    down = [A.majority_independent(n, 1 - q) for n in ns]
    assert all(b >= a - 1e-12 for a, b in zip(up, up[1:])) and all(b <= a + 1e-12 for a, b in zip(down, down[1:]))


@pytest.mark.parametrize("rho,q", [(0.1, 0.6), (0.3, 0.6), (0.5, 0.55)])
def test_common_signal_approaches_its_limit(rho, q):
    assert A.majority_common_signal(20001, q, rho) == pytest.approx(A.limit_common_signal(q, rho), abs=2e-3)


@pytest.mark.parametrize("q,sd", [(0.6, 0.05), (0.6, 0.15), (0.55, 0.1), (0.7, 0.2)])
def test_difficulty_approaches_its_limit_and_grows_with_n_above_half(q, sd):
    assert A.majority_difficulty(20001, q, sd) == pytest.approx(A.limit_difficulty(q, sd), abs=3e-3)
    ns = list(range(1, 300, 2))
    vals = [A.majority_difficulty(n, q, sd) for n in ns]
    assert all(b >= a - 1e-12 for a, b in zip(vals, vals[1:])) and vals[-1] < A.limit_difficulty(q, sd) + 1e-9


def test_dependence_never_beats_independence_above_one_half():
    for n in (3, 11, 51, 201):
        base = A.majority_independent(n, 0.6)
        assert A.majority_common_signal(n, 0.6, 0.3) <= base + 1e-12 and A.majority_difficulty(n, 0.6, 0.15) <= base + 1e-12


def test_weighted_majority_is_never_worse_than_simple_for_known_competences_in_the_samples():
    for delta in (0.0, 0.1, 0.2, 0.3):
        qs = list(S.competences(0.6, delta, 101))
        simple = A.poisson_binomial_curve(qs)
        weighted = A.weighted_curve(qs, A.integer_weights(qs))
        for n in (3, 11, 51, 101):
            assert weighted[n] >= simple[n] - 1e-9, (delta, n)


def test_needed_voters_matches_a_linear_scan():
    for q, target in ((0.6, 0.9), (0.55, 0.9), (0.52, 0.8), (0.7, 0.99)):
        prob = lambda n: A.majority_independent(n, q)
        scan = next(n for n in range(1, 5000, 2) if prob(n) >= target)
        assert A.needed_voters(target, prob, 1.0) == scan, (q, target)
    prob = lambda n: A.majority_common_signal(n, 0.6, 0.1)
    scan = next(n for n in range(1, 5000, 2) if prob(n) >= 0.94)
    assert A.needed_voters(0.94, prob, A.limit_common_signal(0.6, 0.1)) == scan and A.needed_voters(0.97, prob, A.limit_common_signal(0.6, 0.1)) is None


def test_constants_stay_inside_the_defined_models():
    for q in range(C.Q_MIN, C.Q_MAX + 1):
        for sd in (0, C.SD_MAX):
            if sd:
                assert (sd / 100) ** 2 < (q / 100) * (1 - q / 100)                 # Beta-Parameter existieren
    assert C.PLOT_N[0] == 1 and C.PLOT_N[-1] <= C.N_MAX and all(n % 2 == 1 for n in C.PLOT_N)
