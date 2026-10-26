"""Verdikte und Tabellen als reine Funktionen: Schwellen und jede Zahl im Text an handgesetzten Werten."""

import math

import pytest

import mhu_constants as C
import mhu_evaluation as ev


def test_number_formats():
    assert ev.num(3.0) == "3,0" and ev.pct(0.6483) == "64,8 %" and ev.pct(1.0, 0) == "100 %" and ev.pct(None) == "–" and ev.pct(float("nan")) == "–"
    assert ev.count(1234567) == "1.234.567" and ev.count(41) == "41" and ev.count(None) == "nie" and ev.count(math.inf) == "über 2 Mio."


def test_settings_convert_percent_to_fractions():
    s = ev.Settings(n=11, q=55, rho=20, sd=10, delta=10)
    assert (s.qf, s.rhof, s.sdf, s.deltaf) == (0.55, 0.2, 0.1, 0.1)
    assert ev.Settings() == ev.Settings(n=C.DEFAULT_N, q=C.DEFAULT_Q, rho=C.DEFAULT_RHO, sd=C.DEFAULT_SD, delta=C.DEFAULT_DELTA)


def test_analysis_by_hand():
    a = ev.analyse(ev.Settings(n=3, q=60, rho=50, sd=0, delta=0))
    assert a.at_n["unabhaengig"] == pytest.approx(0.648) and a.at_n["signal"] == pytest.approx(0.624) and a.at_n["schwierigkeit"] == pytest.approx(0.648)
    assert a.at_n["gemischt"] == pytest.approx(0.648) and a.at_n["gewichtet"] == pytest.approx(0.648)
    assert a.limits["unabhaengig"] == 1.0 and a.limits["signal"] == pytest.approx(0.8) and a.limits["schwierigkeit"] == 1.0 and a.limits["gemischt"] == 1.0 and a.limits["gewichtet"] == 1.0
    assert a.needed["unabhaengig"] == 67 and a.needed["signal"] is None and a.needed["schwierigkeit"] == 67 and a.needed["gemischt"] == 67 and a.needed["gewichtet"] == 67
    assert a.ns == C.PLOT_N and all(len(v) == len(a.ns) for v in a.curves.values()) and a.curves["unabhaengig"][0] == pytest.approx(0.6) and a.curves["unabhaengig"][1] == pytest.approx(0.648)


def test_analysis_at_the_chosen_n_equals_the_curve_value():
    a = ev.analyse(ev.Settings(n=51, q=60, rho=20, sd=10, delta=20))
    i = a.ns.index(51)
    for key in C.MECHANISMS:
        assert a.at_n[key] == pytest.approx(a.curves[key][i], abs=1e-12), key


def test_mechanism_rows_by_hand():
    a = ev.analyse(ev.Settings(n=3, q=60, rho=50, sd=0, delta=0))
    rows = {r["Mechanismus"]: r for r in ev.mechanism_rows(a)}
    assert list(rows) == list(C.MECHANISMS.values())
    s = rows["Gemeinsames Signal"]
    assert s == {"Mechanismus": "Gemeinsames Signal", "Mehrheit richtig bei n = 3": "62,4 %", "Grenzwert (n → ∞)": "80,0 %", "Gutachter für 95 %": "nie"}
    assert rows["Unabhängige Gutachter"]["Gutachter für 95 %"] == "67" and rows["Verschieden gute Gutachter"]["Gutachter für 95 %"] == "67"


def test_mechanism_rows_when_the_pool_does_not_reach_the_target_within_201():
    a = ev.analyse(ev.Settings(n=11, q=52, rho=0, sd=0, delta=0))
    rows = {r["Mechanismus"]: r for r in ev.mechanism_rows(a)}
    assert rows["Verschieden gute Gutachter"]["Gutachter für 95 %"] == "nicht bis 201" and rows["Unabhängige Gutachter"]["Gutachter für 95 %"] == "1.691"


def test_verdict_state_by_hand():
    kind, text = ev.verdict_state(ev.analyse(ev.Settings(n=3, q=60, rho=50, sd=0, delta=0)))
    assert kind == "warning"
    assert text == ("Bei 3 Gutachtern mit 60 % Trefferquote liegt die Mehrheit bei unabhängigen Gutachtern in 64,8 % richtig (Grenzwert 100 %). "
                    "Mit gemeinsamem Hinweis (ρ = 50 %) sind es 62,4 % (Grenzwert 80,0 %). "
                    "Für 95 % brauchen unabhängige Gutachter 67, bei gemeinsamem Hinweis nie, bei schwierigen Fällen 67.")


def test_verdict_state_branches():
    _, none = ev.verdict_state(ev.analyse(ev.Settings(n=101, q=55, rho=0, sd=0, delta=0)))
    assert "Ohne gemeinsamen Hinweis und ohne Fallschwierigkeit ist jeder dieser Mechanismen der unabhängige Fall." in none and "Spanne" not in none and "84,4 %" in none
    kind, bad = ev.verdict_state(ev.analyse(ev.Settings(n=101, q=45, rho=0, sd=0, delta=0)))
    assert kind == "warning" and "schlechter als der Zufall" in bad and "15,6 %" in bad
    kind, mixed = ev.verdict_state(ev.analyse(ev.Settings(n=11, q=60, rho=0, sd=0, delta=30)))
    assert kind == "info" and "(Spanne ±30 Punkte) zählt die einfache Mehrheit 73,4 %, die gewichtete 90,7 %." in mixed
    kind, diff = ev.verdict_state(ev.analyse(ev.Settings(n=101, q=60, rho=0, sd=15, delta=0)))
    assert kind == "warning" and "Bei schwierigen Fällen (Streuung 15 Punkte) sind es 73,4 % (Grenzwert 74,3 %)." in diff


def _needed_rows():
    base = {"unabhaengig": 100, "signal": 200, "schwierigkeit": 300}
    return [{"q": q, "target": t, **base} for q in C.SERIES_QS for t in C.SERIES_TARGETS]


def test_needed_rows_and_verdict_by_hand():
    rows = _needed_rows()
    rows[0] = {"q": 51, "target": 0.90, "unabhaengig": 4105, "signal": None, "schwierigkeit": math.inf}
    table = ev.needed_rows(rows)
    assert table[0] == {"Trefferquote": "51 %", "Ziel": "90 %", "Unabhängig": "4.105", "Gemeinsamer Hinweis (ρ = 10 %)": "nie", "Schwierige Fälle (Streuung 5 Punkte)": "über 2 Mio."}
    assert table[1]["Ziel"] == "95 %" and table[2]["Ziel"] == "99 %" and len(table) == len(rows)
    rows2 = _needed_rows()
    for r in rows2:
        if r["q"] == 51 and r["target"] == 0.95:
            r["unabhaengig"] = 6763
        if r["q"] == 70 and r["target"] == 0.95:
            r["unabhaengig"] = 17
        if r["q"] == 70 and r["target"] == 0.99:
            r.update(unabhaengig=31, signal=None, schwierigkeit=51)
    kind, text = ev.verdict_needed(rows2)
    assert kind == "info" and text == ("Für 95 % brauchen unabhängige Gutachter bei 51 % Trefferquote 6.763, bei 70 % nur 17. "
                                      "Für 99 % und 70 % Trefferquote: 31 unabhängig, nie mit gemeinsamem Hinweis von 10 %, 51 bei schwierigen Fällen (Streuung 5 Punkte).")


def _limit_rows():
    rows = []
    for rho in C.SERIES_RHOS:
        rows.append({"mechanism": "signal", "x": rho, "limit": 1 - 0.004 * rho, "n11": 0.7, "n101": 0.9, "n1001": 0.95})
    for sd in C.SERIES_SDS:
        rows.append({"mechanism": "schwierigkeit", "x": sd, "limit": 1 - 0.01 * sd, "n11": 0.7, "n101": 0.8, "n1001": 0.85})
    return rows


def test_limit_rows_and_verdict_by_hand():
    rows = _limit_rows()
    sig = ev.limit_rows(rows, "signal")
    assert len(sig) == len(C.SERIES_RHOS) and sig[0] == {"ρ (%)": 0, "n = 11": "70,0 %", "n = 101": "90,0 %", "n = 1001": "95,0 %", "Grenzwert": "100,0 %"}
    assert list(ev.limit_rows(rows, "schwierigkeit")[0])[0] == "Streuung (Punkte)" and len(ev.limit_rows(rows, "schwierigkeit")) == len(C.SERIES_SDS)
    kind, text = ev.verdict_limits(rows)
    assert kind == "info" and text == ("Bei q = 60 % bleibt die Mehrheit mit gemeinsamem Hinweis von ρ = 50 % bei 80,0 % stehen (bei 1001 Gutachtern 95,0 %) "
                                       "und mit Fallschwierigkeit bei Streuung 20 Punkten bei 80,0 % (bei 1001: 85,0 %); unabhängig wäre es 100 %.")


def test_weighted_rows_and_verdict_by_hand():
    rows = [{"delta": d, "n": n, "simple": 0.75 + 0.001 * d, "weighted": 0.75 + 0.005 * d} for d in C.SERIES_DELTAS for n in C.SERIES_NS_WEIGHTED]
    table = ev.weighted_rows(rows)
    assert len(table) == len(C.SERIES_DELTAS) and table[0] == {"Spanne (Punkte)": 0, "n = 11: einfach": "75,0 %", "n = 11: gewichtet": "75,0 %", "n = 51: einfach": "75,0 %", "n = 51: gewichtet": "75,0 %",
                                                              "n = 101: einfach": "75,0 %", "n = 101: gewichtet": "75,0 %"}
    kind, text = ev.verdict_weighted(rows)
    assert kind == "info" and text == ("Bei 11 Gutachtern und einer Spanne von ±30 Punkten liegt die einfache Mehrheit in 78,0 % richtig, die gewichtete in 90,0 %. "
                                       "Ohne Spanne sind beide gleich (75,0 %). Die Gewichte setzen bekannte Trefferquoten voraus.")
