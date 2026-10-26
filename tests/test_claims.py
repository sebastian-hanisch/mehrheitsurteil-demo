"""Befunde der README als feste Werte: jede Zahl, die dort steht, ist hier nachgerechnet.

Alle Werte sind EXAKT gerechnet (Binomial-, Beta-Binomialverteilung, Faltung), nicht simuliert; die Tests prüfen deshalb die gerundeten Anzeigewerte und die Gutachterzahlen ohne Bänder.
"""

import math

import pytest

import mhu_algorithm as A
import mhu_constants as C
import mhu_evaluation as ev
from mhu_scenario import competences

P = ev.pct


def at(preset):
    return ev.analyse(ev.Settings(**C.PRESETS[preset]))


# --- Unabhängige Gutachter (der Satz von Condorcet) ------------------------------------------------------------------------------------------

def test_independent_majority_table():
    for q, want in ((0.51, "51,0 % 51,5 % 52,7 % 58,0 % 73,7 %"), (0.55, "55,0 % 57,5 % 63,3 % 84,4 % 99,9 %"), (0.6, "60,0 % 64,8 % 75,3 % 97,9 % 100,0 %"), (0.7, "70,0 % 78,4 % 92,2 % 100,0 % 100,0 %"),
                    (0.45, "45,0 % 42,5 % 36,7 % 15,6 % 0,1 %")):
        assert " ".join(P(A.majority_independent(n, q)) for n in (1, 3, 11, 101, 1001)) == want, q


def test_a_hit_rate_of_51_percent_needs_thousands():
    assert [A.needed_voters(t, lambda n: A.majority_independent(n, 0.51)) for t in (0.9, 0.95, 0.99)] == [4105, 6763, 13527]


# --- Reihe 1: wie viele Gutachter? -----------------------------------------------------------------------------------------------------------

NEEDED = {
    (51, 0.90): (4105, 6267, None), (51, 0.95): (6763, 23387, None), (51, 0.99): (13527, None, None),
    (52, 0.90): (1027, 1547, None), (52, 0.95): (1691, 5055, None), (52, 0.99): (3381, None, None),
    (55, 0.90): (163, 239, None), (55, 0.95): (269, 643, None), (55, 0.99): (539, None, None),
    (60, 0.90): (41, 55, 69), (60, 0.95): (67, 129, 219), (60, 0.99): (133, None, None),
    (65, 0.90): (17, 23, 21), (65, 0.95): (29, 49, 43), (65, 0.99): (57, None, 165),
    (70, 0.90): (9, 13, 11), (70, 0.95): (17, 23, 19), (70, 0.99): (31, None, 51),
}


def test_series_needed_table():
    rows = ev.series_needed()
    assert len(rows) == len(NEEDED)
    for r in rows:
        assert (r["unabhaengig"], r["signal"], r["schwierigkeit"]) == NEEDED[(r["q"], r["target"])], (r["q"], r["target"])


def test_a_common_hint_of_ten_percent_makes_99_percent_unreachable_up_to_a_hit_rate_of_70():
    rows = ev.series_needed()
    assert all(r["signal"] is None for r in rows if r["target"] == 0.99)
    # Grenzwert ρ q + (1 − ρ) = 0,1 q + 0,9: bei q = 0,7 genau 0,97 < 0,99
    assert A.limit_common_signal(0.7, 0.1) == pytest.approx(0.97)


def test_case_difficulty_of_five_points_makes_it_unreachable_at_low_hit_rates():
    rows = ev.series_needed()
    assert all(r["schwierigkeit"] is None for r in rows if r["q"] in (51, 52, 55))
    assert P(A.limit_difficulty(0.51, 0.05)) == "57,9 %" and P(A.limit_difficulty(0.7, 0.05)) == "100,0 %"


# --- Reihe 2: wo bleibt die Mehrheit stehen? -------------------------------------------------------------------------------------------------

def test_series_limits_signal():
    rows = {r["x"]: r for r in ev.series_limits() if r["mechanism"] == "signal"}
    assert [P(rows[x]["limit"]) for x in C.SERIES_RHOS] == ["100,0 %", "96,0 %", "92,0 %", "88,0 %", "84,0 %", "80,0 %"]
    assert [P(rows[x]["n11"]) for x in C.SERIES_RHOS] == ["75,3 %", "73,8 %", "72,3 %", "70,7 %", "69,2 %", "67,7 %"]
    assert [P(rows[x]["n101"]) for x in C.SERIES_RHOS] == ["97,9 %", "94,1 %", "90,3 %", "86,5 %", "82,7 %", "79,0 %"]
    assert [P(rows[x]["n1001"]) for x in C.SERIES_RHOS] == ["100,0 %", "96,0 %", "92,0 %", "88,0 %", "84,0 %", "80,0 %"]
    assert all(rows[x]["limit"] == pytest.approx(1 - 0.4 * x / 100) for x in C.SERIES_RHOS)


def test_series_limits_difficulty():
    rows = {r["x"]: r for r in ev.series_limits() if r["mechanism"] == "schwierigkeit"}
    assert [P(rows[x]["limit"]) for x in C.SERIES_SDS] == ["100,0 %", "97,5 %", "83,7 %", "74,3 %", "68,8 %"]
    assert [P(rows[x]["n11"]) for x in C.SERIES_SDS] == ["75,3 %", "74,3 %", "71,7 %", "68,8 %", "66,2 %"]
    assert [P(rows[x]["n101"]) for x in C.SERIES_SDS] == ["97,9 %", "92,2 %", "81,3 %", "73,4 %", "68,4 %"]
    assert [P(rows[x]["n1001"]) for x in C.SERIES_SDS] == ["100,0 %", "97,0 %", "83,4 %", "74,2 %", "68,7 %"]


# --- Reihe 3: gewichten --------------------------------------------------------------------------------------------------------------------

WEIGHTED = {
    0: ("75,3 %", "75,3 %", "92,6 %", "92,6 %", "97,9 %", "97,9 %"),
    10: ("74,5 %", "77,3 %", "92,3 %", "95,1 %", "97,8 %", "99,1 %"),
    20: ("73,8 %", "83,7 %", "92,3 %", "98,8 %", "97,8 %", "99,9 %"),
    30: ("73,4 %", "90,7 %", "92,6 %", "99,9 %", "98,0 %", "100,0 %"),
}


def test_series_weighted_table():
    rows = ev.series_weighted()
    table = {r["Spanne (Punkte)"]: tuple(v for k, v in r.items() if k != "Spanne (Punkte)") for r in ev.weighted_rows(rows)}
    for delta, want in WEIGHTED.items():
        assert table[delta] == want, delta


def test_weighting_never_loses_and_gains_more_with_a_wider_spread():
    rows = ev.series_weighted()
    assert all(r["weighted"] >= r["simple"] - 1e-9 for r in rows)
    gain = {d: next(r for r in rows if r["delta"] == d and r["n"] == 11)["weighted"] - next(r for r in rows if r["delta"] == d and r["n"] == 11)["simple"] for d in C.SERIES_DELTAS}
    assert list(gain.values()) == sorted(gain.values()) and gain[0] == pytest.approx(0.0, abs=1e-12) and gain[30] > 0.15


def test_simple_majority_barely_notices_the_spread():
    rows = ev.series_weighted()
    n11 = [r["simple"] for r in rows if r["n"] == 11]
    assert max(n11) - min(n11) < 0.02                                         # 73,4 % bis 75,3 %


# --- Presets ---------------------------------------------------------------------------------------------------------------------------------

def test_presets_tell_their_stories():
    a = at("Weisheit der Menge")
    assert P(a.at_n["unabhaengig"]) == "84,4 %" and len({round(v, 12) for v in a.at_n.values()}) == 1                         # ohne Abhängigkeit und Spanne fallen alle Mechanismen zusammen
    b = at("Schlechter als der Zufall")
    assert P(b.at_n["unabhaengig"]) == "15,6 %" and P(b.at_n["gewichtet"]) == "84,4 %" and b.limits["unabhaengig"] == 0.0         # mit bekannten Quoten dreht das Gewicht die Stimmen um
    c = at("Gemeinsamer Hinweis")
    assert P(c.at_n["signal"]) == "86,5 %" and P(c.limits["signal"]) == "88,0 %" and c.needed["signal"] is None and c.needed["unabhaengig"] == 67
    d = at("Schwierige Fälle")
    assert P(d.at_n["schwierigkeit"]) == "73,4 %" and P(d.limits["schwierigkeit"]) == "74,3 %" and d.needed["schwierigkeit"] is None
    e = at("Verschieden gute Gutachter")
    assert P(e.at_n["gemischt"]) == "73,4 %" and P(e.at_n["gewichtet"]) == "90,7 %" and P(e.at_n["unabhaengig"]) == "75,3 %" and e.needed["gewichtet"] == 15 and e.needed["gemischt"] == 63
    f = at("Elf Gutachter")
    assert [P(f.at_n[k]) for k in C.MECHANISMS] == ["63,3 %", "61,6 %", "61,3 %", "62,2 %", "68,2 %"] and f.needed["unabhaengig"] == 269 and f.needed["gewichtet"] == 117


def test_the_help_texts_name_the_numbers():
    for name, needle in (("Weisheit der Menge", "84,4 %"), ("Schlechter als der Zufall", "15,6 %"), ("Gemeinsamer Hinweis", "86,5 %"), ("Gemeinsamer Hinweis", "88 %"), ("Schwierige Fälle", "73,4 %"),
                         ("Schwierige Fälle", "74,3 %"), ("Verschieden gute Gutachter", "90,7 %"), ("Verschieden gute Gutachter", "73,4 %")):
        assert needle in C.PRESET_HELP[name], (name, needle)


def test_the_competence_pool_by_hand():
    qs = competences(0.6, 0.3, 11)
    assert sorted(round(float(x), 4) for x in qs) == sorted(round(0.6 + 0.3 * u, 4) for u in (0, -0.5, 0.5, -0.75, 0.25, -0.25, 0.75, -0.875, 0.125, -0.375, 0.625))
    assert math.isclose(sum(qs) / 11, 0.6, abs_tol=0.03)
