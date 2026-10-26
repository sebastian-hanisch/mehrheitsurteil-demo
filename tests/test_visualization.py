"""Abbildungen: Aufbau, gesperrte Achsen, Werte an der Hand-Analyse."""

import math

import pytest

import mhu_constants as C
import mhu_evaluation as ev
import mhu_visualization as V


def locked(fig):
    return all(ax.fixedrange for ax in fig.select_xaxes()) and all(ax.fixedrange for ax in fig.select_yaxes())


def test_curves_figure_by_hand():
    a = ev.analyse(ev.Settings(n=11, q=60, rho=50, sd=0, delta=0))
    fig = V.build_curves(a)
    assert [t.name for t in fig.data] == list(C.MECHANISMS.values()) and list(fig.data[0].x) == list(C.PLOT_N)
    assert fig.data[0].y[0] == pytest.approx(0.6) and fig.data[0].y[1] == pytest.approx(0.648) and fig.data[1].y[1] == pytest.approx(0.624)
    assert fig.layout.xaxis.type == "log" and tuple(fig.layout.yaxis.range) == (0, 1.02) and locked(fig)
    marks = [s for s in fig.layout.shapes if s.type == "line"]
    assert any(s.x0 == 11 for s in marks) and any(s.y0 == 0.5 for s in marks)                         # senkrechte Linie bei n, waagerechte beim Zufall
    assert len({t.line.dash for t in fig.data}) == len(C.MECHANISMS)                                  # verschiedene Strichart, damit sich deckende Linien sichtbar bleiben


def _needed():
    return [{"q": q, "target": t, "unabhaengig": 100 + q, "signal": None if q == 51 else 200, "schwierigkeit": math.inf if q == 52 else 300} for q in C.SERIES_QS for t in C.SERIES_TARGETS]


def test_needed_figure_leaves_gaps_for_never_and_for_beyond_the_search_range():
    fig = V.build_needed(_needed(), 0.95)
    bars = [t for t in fig.data if t.type == "bar"]
    assert [b.name for b in bars][0] == "Unabhängig" and len(bars) == 3
    assert list(bars[0].x) == [f"{q} %" for q in C.SERIES_QS] and list(bars[0].y) == [100 + q for q in C.SERIES_QS]
    assert bars[1].y[0] is None and bars[1].y[1] == 200 and bars[2].y[1] is None and bars[2].y[0] == 300
    assert fig.layout.yaxis.type == "log" and locked(fig)


def test_limits_figure_has_the_limit_as_a_dashed_line():
    rows = [{"mechanism": "signal", "x": r, "limit": 1 - 0.004 * r, "n11": 0.7, "n101": 0.9, "n1001": 0.95} for r in C.SERIES_RHOS]
    fig = V.build_limits(rows, "signal")
    assert [t.name for t in fig.data] == ["11 Gutachter", "101 Gutachter", "1001 Gutachter", "Grenzwert"] and fig.data[3].line.dash == "dash"
    assert list(fig.data[0].x) == list(C.SERIES_RHOS) and fig.layout.xaxis.title.text == "ρ in %" and locked(fig)
    other = [{"mechanism": "schwierigkeit", "x": s, "limit": 0.9, "n11": 0.7, "n101": 0.8, "n1001": 0.85} for s in C.SERIES_SDS]
    assert V.build_limits(other, "schwierigkeit").layout.xaxis.title.text.startswith("Streuung")


def test_weighted_figure_has_a_pair_of_lines_per_n():
    rows = [{"delta": d, "n": n, "simple": 0.75, "weighted": 0.8} for d in C.SERIES_DELTAS for n in C.SERIES_NS_WEIGHTED]
    fig = V.build_weighted(rows)
    assert [t.name for t in fig.data] == [f"{kind}, n = {n}" for n in C.SERIES_NS_WEIGHTED for kind in ("einfach", "gewichtet")]
    assert list(fig.data[0].x) == list(C.SERIES_DELTAS) and locked(fig)
