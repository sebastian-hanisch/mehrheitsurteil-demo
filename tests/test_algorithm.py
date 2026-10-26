"""Kern von Hand: jeder Mechanismus und jede Hilfsfunktion an Mini-Fällen, mit der Rechnung im Kommentar."""

import math

import pytest

import mhu_algorithm as A
import mhu_scenario as S


def test_odd_check():
    for bad in (0, 2, 4, -1):
        with pytest.raises(ValueError):
            A.check_odd(bad)
        with pytest.raises(ValueError):
            A.majority_independent(bad, 0.6)
    assert A.check_odd(7) == 7


def test_independent_majority_by_hand():
    # n = 1: q. n = 3: 3 q² (1 − q) + q³ = 3 q² − 2 q³ = 1,08 − 0,432 = 0,648 bei q = 0,6.
    assert A.majority_independent(1, 0.6) == pytest.approx(0.6)
    assert A.majority_independent(3, 0.6) == pytest.approx(0.648)
    # n = 5: 10 q³ (1 − q)² + 5 q⁴ (1 − q) + q⁵ = 0,3456 + 0,2592 + 0,07776 = 0,68256
    assert A.majority_independent(5, 0.6) == pytest.approx(0.68256)
    assert A.majority_independent(9, 0.5) == pytest.approx(0.5)             # Zufall bleibt Zufall
    assert A.majority_independent(7, 0.0) == 0.0 and A.majority_independent(7, 1.0) == 1.0


def test_independent_majority_is_symmetric_in_q():
    for n in (1, 3, 11, 101):
        assert A.majority_independent(n, 0.37) + A.majority_independent(n, 0.63) == pytest.approx(1.0)


def test_common_signal_by_hand():
    # ρ = 0,5, q = 0,6, n = 3: 0,5 · 0,6 + 0,5 · 0,648 = 0,624; Grenzwert 0,5 · 0,6 + 0,5 · 1 = 0,8
    assert A.majority_common_signal(3, 0.6, 0.5) == pytest.approx(0.624)
    assert A.limit_common_signal(0.6, 0.5) == pytest.approx(0.8)
    assert A.majority_common_signal(3, 0.6, 0.0) == pytest.approx(0.648) and A.majority_common_signal(3, 0.6, 1.0) == pytest.approx(0.6)
    assert A.limit_common_signal(0.4, 0.5) == pytest.approx(0.2)           # q < 1/2: Grenzwert ρ q + (1 − ρ) · 0
    assert A.limit_common_signal(0.5, 0.5) == pytest.approx(0.5)


def test_limits_of_independent_majority():
    assert (A.limit_independent(0.51), A.limit_independent(0.5), A.limit_independent(0.49)) == (1.0, 0.5, 0.0)


def test_beta_parameters_by_hand():
    # q = 2/3, s² = 1/18: κ = (2/9) / (1/18) − 1 = 3 → a = 2, b = 1
    a, b = A.beta_params(2 / 3, math.sqrt(1 / 18))
    assert a == pytest.approx(2.0) and b == pytest.approx(1.0)
    with pytest.raises(ValueError):
        A.beta_params(0.5, 0.5)                       # s² = q (1 − q): κ = 0
    with pytest.raises(ValueError):
        A.beta_params(0.6, 0.6)


def test_difficulty_by_hand():
    # p ~ Beta(2, 1) (Dichte 2p), n = 3: P(X = 3) = B(5, 1) / B(2, 1) = 2/5, P(X = 2) = 3 · B(4, 2) / B(2, 1) = 3/10 → P(X ≥ 2) = 0,7
    q, sd = 2 / 3, math.sqrt(1 / 18)
    assert A.majority_difficulty(3, q, sd) == pytest.approx(0.7)
    # Grenzwert P(p > 1/2) = 1 − (1/2)² = 0,75 (die Verteilungsfunktion von Beta(2, 1) ist x²)
    assert A.limit_difficulty(q, sd) == pytest.approx(0.75)
    assert A.majority_difficulty(3, 0.6, 0.0) == pytest.approx(0.648) and A.limit_difficulty(0.6, 0.0) == 1.0 and A.limit_difficulty(0.4, 0.0) == 0.0


def test_poisson_binomial_curve_by_hand():
    c = A.poisson_binomial_curve([0.6, 0.6, 0.6, 0.6, 0.6])
    assert sorted(c) == [1, 3, 5] and c[1] == pytest.approx(0.6) and c[3] == pytest.approx(0.648) and c[5] == pytest.approx(0.68256)
    # Gutachter A (0,9), B und C (je 0,5): mindestens zwei Richtige = 0,9 · P(B oder C richtig) + 0,1 · P(B und C richtig) = 0,9 · 0,75 + 0,1 · 0,25 = 0,7
    assert A.poisson_binomial_curve([0.9, 0.5, 0.5])[3] == pytest.approx(0.7)


def test_integer_weights_by_hand():
    assert A.integer_weights([0.6, 0.5, 0.4]) == [41, 0, -41]                  # 100 · ln 1,5 = 40,5 → 41
    assert A.integer_weights([0.9]) == [220]                                    # 100 · ln 9 = 219,7 → 220


def test_weighted_curve_by_hand():
    # nur Gutachter A hat Gewicht ≠ 0: das Urteil gehört ihm, also 0,9 bei k = 1 und k = 3
    c = A.weighted_curve([0.9, 0.5, 0.5], [220, 0, 0])
    assert c[1] == pytest.approx(0.9) and c[3] == pytest.approx(0.9)
    assert A.weighted_curve([0.5], [0])[1] == pytest.approx(0.5)                # Summe 0 zählt halb
    assert A.weighted_curve([0.4], [-41])[1] == pytest.approx(0.6)              # negatives Gewicht dreht das Urteil um
    # gleiche Gewichte = einfache Mehrheit
    simple = A.poisson_binomial_curve([0.6, 0.7, 0.55])
    assert A.weighted_curve([0.6, 0.7, 0.55], [1, 1, 1])[3] == pytest.approx(simple[3])


def test_weighted_curve_with_unequal_weights_by_hand():
    # q = (0,8, 0,6, 0,6), Gewichte (3, 1, 1): A allein gewinnt gegen B und C nur, wenn nicht beide gegen ihn sind: Summe > 0.
    # A richtig (0,8): Summe = 3 ± 1 ± 1 ≥ 1 > 0 immer. A falsch (0,2): Summe = −3 ± 1 ± 1 ≤ −1 immer. Also P = 0,8.
    assert A.weighted_curve([0.8, 0.6, 0.6], [3, 1, 1])[3] == pytest.approx(0.8)
    # Gewichte (1, 1, 1) dagegen: mindestens zwei Richtige = 0,8 · (1 − 0,4 · 0,4) + 0,2 · 0,36 = 0,672 + 0,072 = 0,744
    assert A.weighted_curve([0.8, 0.6, 0.6], [1, 1, 1])[3] == pytest.approx(0.744)


def test_needed_voters_by_hand():
    prob = lambda n: A.majority_independent(n, 0.6)
    assert A.needed_voters(0.9, prob, 1.0) == 41
    assert prob(41) >= 0.9 > prob(39)
    assert A.needed_voters(0.6, prob, 1.0) == 1                                  # schon ein Gutachter genügt
    assert A.needed_voters(0.95, prob, 0.9) is None                              # der Grenzwert liegt darunter: nie
    assert A.needed_voters(0.95, lambda n: 0.5, 1.0) == math.inf                  # Grenzwert erlaubt es, die Suche kommt nicht ans Ziel


def test_needed_voters_returns_the_smallest_odd_number():
    for q, target in ((0.55, 0.9), (0.6, 0.95), (0.7, 0.99), (0.52, 0.8)):
        prob = lambda n: A.majority_independent(n, q)
        n = A.needed_voters(target, prob, 1.0)
        assert n % 2 == 1 and prob(n) >= target and (n == 1 or prob(n - 2) < target), (q, target)


def test_van_der_corput_and_competences_by_hand():
    assert [S.van_der_corput(j) for j in (1, 2, 3, 4)] == [0.5, 0.25, 0.75, 0.125] and S.van_der_corput(0) == 0.0
    # u = 2 · vdc − 1: 0, −0,5, +0,5 → q + δ · u
    assert S.competences(0.6, 0.2, 3).tolist() == pytest.approx([0.6, 0.5, 0.7])
    assert S.competences(0.6, 0.0, 4).tolist() == [0.6] * 4 and S.competences(0.7, 0.2, 1).tolist() == [0.7]
    qs = S.competences(0.6, 0.3, 255)
    assert sum(qs) / len(qs) == pytest.approx(0.6, abs=0.002) and min(qs) >= 0.3 and max(qs) < 0.9
    assert min(S.competences(0.8, 0.3, 64)) >= 0.5 and max(S.competences(0.8, 0.3, 64)) <= 0.99      # nach oben bei 0,99 gekappt


def test_needed_voters_at_the_edges_of_the_search():
    # Ziel genau erreicht: prob(n) = n / 100 erreicht 0,07 bei n = 7 und der Grenzwert gleich dem Ziel lässt die Suche zu
    assert A.needed_voters(0.07, lambda n: n / 100, 1.0) == 7
    assert A.needed_voters(0.9, lambda n: min(0.9, n / 10), 0.9) == 9                    # Grenzwert = Ziel: erreichbar, nicht „nie“
    assert A.needed_voters(0.91, lambda n: min(0.9, n / 10), 0.9) is None
    assert A.needed_voters(0.5, lambda n: 0.5, 1.0) == 1 and A.needed_voters(0.9, lambda n: n / 10, 1.0) == 9
    assert A.needed_voters(0.61, lambda n: n / 100, 1.0) == 61 and A.needed_voters(0.63, lambda n: n / 100, 1.0) == 63       # die Suche trifft auch Zahlen zwischen den Zweierpotenzen
    assert A.needed_voters(0.64, lambda n: n / 100, 1.0) == 65 and A.needed_voters(0.02, lambda n: n / 100, 1.0) == 3
    calls = []
    assert A.needed_voters(0.9, lambda n: calls.append(n) or n / 10, 1.0) == 9 and max(calls) <= 15


def test_beta_parameters_below_one():
    # κ = 0,25 / (1/6) − 1 = 0,5 → a = b = 0,25 (U-förmig, erlaubt); κ = 1 → a = b = 0,5 gerade noch gültig
    a, b = A.beta_params(0.5, math.sqrt(0.25 / 1.5))
    assert a == pytest.approx(0.25) and b == pytest.approx(0.25)
    assert A.beta_params(0.5, math.sqrt(0.125))[0] == pytest.approx(0.5)
