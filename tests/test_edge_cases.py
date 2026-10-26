"""Randfälle: Extremwerte der Regler, Invarianten jeder Analyse, ungerade Gutachterzahl aus der Adresszeile."""

import itertools
import os

import pytest
from streamlit.testing.v1 import AppTest

import mhu_algorithm as A
import mhu_constants as C
import mhu_evaluation as ev

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
GRID = list(itertools.product((1, 3, C.N_MAX), (C.Q_MIN, 50, C.Q_MAX), (C.RHO_MIN, C.RHO_MAX), (C.SD_MIN, C.SD_MAX), (C.DELTA_MIN, C.DELTA_MAX)))


@pytest.mark.parametrize("n,q,rho,sd,delta", GRID)
def test_invariants_at_the_extremes(n, q, rho, sd, delta):
    a = ev.analyse(ev.Settings(n=n, q=q, rho=rho, sd=sd, delta=delta))
    assert set(a.curves) == set(C.MECHANISMS) and set(a.at_n) == set(C.MECHANISMS)
    for key in C.MECHANISMS:
        assert all(-1e-12 <= p <= 1 + 1e-12 for p in a.curves[key]), key
        assert 0.0 <= a.at_n[key] <= 1.0 and 0.0 <= a.limits[key] <= 1.0
    # die Kurve bei n = 1 ist die Trefferquote (ungewichtet): ein einzelner Gutachter entscheidet
    assert a.curves["unabhaengig"][0] == pytest.approx(q / 100)
    # Grenzwert und Kurve gehen in dieselbe Richtung (oberhalb 50 % wächst die unabhängige Mehrheit)
    if q > 50:
        assert a.curves["unabhaengig"][-1] >= a.curves["unabhaengig"][0] and a.limits["unabhaengig"] == 1.0
    if q < 50:
        assert a.curves["unabhaengig"][-1] <= a.curves["unabhaengig"][0] and a.limits["unabhaengig"] == 0.0
    # Abhängigkeit hilft nie über 50 %; unter 50 % hebt sie die Mehrheit nie unter die unabhängige (sie ist dann eine Mischung mit q selbst)
    if q > 50:
        assert a.at_n["signal"] <= a.at_n["unabhaengig"] + 1e-12 and a.at_n["schwierigkeit"] <= a.at_n["unabhaengig"] + 1e-12
    kind, text = ev.verdict_state(a)
    assert kind in ("warning", "info") and text and len(ev.mechanism_rows(a)) == len(C.MECHANISMS)


def test_exactly_one_half_is_a_coin_flip_for_independent_voters():
    a = ev.analyse(ev.Settings(n=101, q=50, rho=0, sd=0, delta=0))
    assert a.at_n["unabhaengig"] == pytest.approx(0.5) and a.limits["unabhaengig"] == 0.5 and a.needed["unabhaengig"] is None
    assert a.at_n["gewichtet"] == pytest.approx(0.5) and a.limits["gewichtet"] == 0.5                  # alle Gewichte 0: jede Summe ist 0, der Gleichstand zählt halb


def test_a_single_voter_is_just_the_hit_rate():
    a = ev.analyse(ev.Settings(n=1, q=60, rho=30, sd=15, delta=0))
    assert a.at_n["unabhaengig"] == pytest.approx(0.6) and a.at_n["gemischt"] == pytest.approx(0.6) and a.at_n["gewichtet"] == pytest.approx(0.6)
    assert a.at_n["schwierigkeit"] == pytest.approx(0.6) and a.at_n["signal"] == pytest.approx(0.6)       # bei n = 1 hat die Abhängigkeit nichts zu bündeln


def test_beta_distribution_exists_for_every_slider_combination():
    for q in range(C.Q_MIN, C.Q_MAX + 1):
        a = A.beta_params(q / 100, C.SD_MAX / 100)
        assert a[0] > 0 and a[1] > 0


def test_pool_beyond_the_slider_n_is_still_defined():
    a = ev.analyse(ev.Settings(n=C.N_MAX, q=60, rho=0, sd=0, delta=30))
    assert len(a.qs) >= C.N_MAX and a.at_n["gemischt"] == pytest.approx(a.curves["gemischt"][-1])


def test_an_even_n_from_the_address_line_moves_up_to_the_next_odd_value():
    at = AppTest.from_file(APP, default_timeout=120)
    at.query_params["n"] = "12"
    at.run()
    assert not at.exception and at.slider(key="n_slider").value == 13
    at2 = AppTest.from_file(APP, default_timeout=120)
    at2.query_params["n"] = "999"
    at2.run()
    assert not at2.exception and at2.slider(key="n_slider").value == C.N_MAX
