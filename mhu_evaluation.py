"""Auswertung: Einstellungen, Kurven über der Gutachterzahl, Tabellen, Verdikte als reine Funktionen (ohne Streamlit) und die festen Reihen (alle exakt gerechnet)."""

import math
from dataclasses import dataclass

import mhu_algorithm as A
import mhu_constants as C
from mhu_scenario import competences, mean_competence


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x, digits: int = 1) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{100 * x:.{digits}f} %".replace(".", ",")


def count(n) -> str:
    """Gutachterzahl mit Tausenderpunkt; None = nie erreichbar, unendlich = erst jenseits der Suchgrenze."""
    if n is None:
        return "nie"
    if n == math.inf:
        return f"über {C.SEARCH_CAP // 1_000_000} Mio."
    return f"{n:,}".replace(",", ".")


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    q: int = C.DEFAULT_Q
    rho: int = C.DEFAULT_RHO
    sd: int = C.DEFAULT_SD
    delta: int = C.DEFAULT_DELTA

    @property
    def qf(self) -> float:
        return self.q / 100

    @property
    def rhof(self) -> float:
        return self.rho / 100

    @property
    def sdf(self) -> float:
        return self.sd / 100

    @property
    def deltaf(self) -> float:
        return self.delta / 100


@dataclass
class Analysis:
    settings: Settings
    ns: tuple            # Gutachterzahlen der Kurven (ungerade)
    curves: dict         # Mechanismus -> Liste der Wahrscheinlichkeiten über ns
    at_n: dict           # Mechanismus -> Wahrscheinlichkeit bei settings.n
    limits: dict         # Mechanismus -> Grenzwert für n → ∞
    needed: dict         # Mechanismus -> kleinste Gutachterzahl für 95 % (None: nie)
    qs: list             # Trefferquoten der ersten max(ns) Gutachter im Modell „verschieden gut“


TARGET = 0.95


def pool(settings: Settings, size: int) -> list:
    return list(competences(settings.qf, settings.deltaf, size))


def analyse(settings: Settings) -> Analysis:
    q, rho, sd = settings.qf, settings.rhof, settings.sdf
    ns = C.PLOT_N
    qs = pool(settings, max(max(ns), settings.n))
    simple = A.poisson_binomial_curve(qs)
    weighted = A.weighted_curve(qs, A.integer_weights(qs))
    curves = {
        "unabhaengig": [A.majority_independent(n, q) for n in ns],
        "signal": [A.majority_common_signal(n, q, rho) for n in ns],
        "schwierigkeit": [A.majority_difficulty(n, q, sd) for n in ns],
        "gemischt": [simple[n] for n in ns],
        "gewichtet": [weighted[n] for n in ns],
    }
    n = settings.n
    at_n = {
        "unabhaengig": A.majority_independent(n, q), "signal": A.majority_common_signal(n, q, rho), "schwierigkeit": A.majority_difficulty(n, q, sd),
        "gemischt": simple[n], "gewichtet": weighted[n],
    }
    limits = {
        "unabhaengig": A.limit_independent(q), "signal": A.limit_common_signal(q, rho), "schwierigkeit": A.limit_difficulty(q, sd),
        "gemischt": A.limit_independent(round(mean_competence(q, settings.deltaf), 9)), "gewichtet": 1.0 if any(abs(x - 0.5) > 1e-12 for x in qs) else 0.5,
    }
    needed = {
        "unabhaengig": A.needed_voters(TARGET, lambda m: A.majority_independent(m, q), limits["unabhaengig"]),
        "signal": A.needed_voters(TARGET, lambda m: A.majority_common_signal(m, q, rho), limits["signal"]),
        "schwierigkeit": A.needed_voters(TARGET, lambda m: A.majority_difficulty(m, q, sd), limits["schwierigkeit"]),
        "gemischt": _needed_pool(settings, simple_target=True),
        "gewichtet": _needed_pool(settings, simple_target=False),
    }
    return Analysis(settings=settings, ns=ns, curves=curves, at_n=at_n, limits=limits, needed=needed, qs=qs)


def _needed_pool(settings: Settings, simple_target: bool):
    """Kleinste ungerade Gutachterzahl bis 201, bei der der Pool (verschieden gute Gutachter) 95 % erreicht; None, wenn bis 201 nicht erreicht (kein Rückschluss auf größere Zahlen)."""
    qs = pool(settings, C.PLOT_N[-1])
    curve = A.poisson_binomial_curve(qs) if simple_target else A.weighted_curve(qs, A.integer_weights(qs))
    return next((n for n in C.PLOT_N if curve[n] >= TARGET), None)


def mechanism_rows(a: Analysis) -> list[dict]:
    """Zeilen für st.table: je Mechanismus die Wahrscheinlichkeit bei n, der Grenzwert und die Gutachterzahl für 95 %."""
    rows = []
    for key in C.MECHANISMS:
        capped = key in ("gemischt", "gewichtet")
        need = a.needed[key]
        rows.append({
            "Mechanismus": C.MECHANISMS[key], f"Mehrheit richtig bei n = {a.settings.n}": pct(a.at_n[key]), "Grenzwert (n → ∞)": pct(a.limits[key]),
            "Gutachter für 95 %": "nicht bis 201" if (need is None and capped) else count(need),
        })
    return rows


def verdict_state(a: Analysis) -> tuple[str, str]:
    """Verdikt: was die Mehrheit bei n Gutachtern leistet, wo die Abhängigkeiten sie begrenzen und was Gewichten bringt."""
    s = a.settings
    t = f"Bei {s.n} Gutachtern mit {s.q} % Trefferquote liegt die Mehrheit bei unabhängigen Gutachtern in {pct(a.at_n['unabhaengig'])} richtig (Grenzwert {pct(a.limits['unabhaengig'], 0)}). "
    if s.rho > 0:
        t += f"Mit gemeinsamem Hinweis (ρ = {s.rho} %) sind es {pct(a.at_n['signal'])} (Grenzwert {pct(a.limits['signal'])}). "
    if s.sd > 0:
        t += f"Bei schwierigen Fällen (Streuung {s.sd} Punkte) sind es {pct(a.at_n['schwierigkeit'])} (Grenzwert {pct(a.limits['schwierigkeit'])}). "
    if s.rho == 0 and s.sd == 0:
        t += "Ohne gemeinsamen Hinweis und ohne Fallschwierigkeit ist jeder dieser Mechanismen der unabhängige Fall. "
    if s.delta > 0:
        t += f"Bei verschieden guten Gutachtern (Spanne ±{s.delta} Punkte) zählt die einfache Mehrheit {pct(a.at_n['gemischt'])}, die gewichtete {pct(a.at_n['gewichtet'])}. "
    if s.q < 50:
        t += "Die Gutachter sind schlechter als der Zufall: mehr von ihnen machen die Mehrheit schlechter, nicht besser. "
    t += f"Für 95 % brauchen unabhängige Gutachter {count(a.needed['unabhaengig'])}, bei gemeinsamem Hinweis {count(a.needed['signal'])}, bei schwierigen Fällen {count(a.needed['schwierigkeit'])}."
    capped = s.q < 50 or a.limits["signal"] < 0.99 or a.limits["schwierigkeit"] < 0.99
    return ("warning" if capped else "info"), t


# --- feste Reihen (exakt) --------------------------------------------------------------------------------------------------------------------

def series_needed() -> list[dict]:
    """Reihe 1: wie viele (ungerade) Gutachter für 90, 95 und 99 %, je Trefferquote; unabhängig, mit gemeinsamem Hinweis (ρ = 10 %) und bei schwieriger Fallverteilung (Streuung 5 Punkte)."""
    rows = []
    for qp in C.SERIES_QS:
        q = qp / 100
        for target in C.SERIES_TARGETS:
            rows.append({
                "q": qp, "target": target,
                "unabhaengig": A.needed_voters(target, lambda m: A.majority_independent(m, q), A.limit_independent(q)),
                "signal": A.needed_voters(target, lambda m: A.majority_common_signal(m, q, 0.10), A.limit_common_signal(q, 0.10)),
                "schwierigkeit": A.needed_voters(target, lambda m: A.majority_difficulty(m, q, 0.05), A.limit_difficulty(q, 0.05)),
            })
    return rows


def series_limits() -> list[dict]:
    """Reihe 2: Grenzwert und Werte bei 11, 101 und 1001 Gutachtern je Stärke der Abhängigkeit (q = 60 %)."""
    q = C.SERIES_Q_FOR_LIMITS / 100
    rows = []
    for rho in C.SERIES_RHOS:
        rows.append({"mechanism": "signal", "x": rho, "limit": A.limit_common_signal(q, rho / 100), **{f"n{n}": A.majority_common_signal(n, q, rho / 100) for n in (11, 101, 1001)}})
    for sd in C.SERIES_SDS:
        rows.append({"mechanism": "schwierigkeit", "x": sd, "limit": A.limit_difficulty(q, sd / 100), **{f"n{n}": A.majority_difficulty(n, q, sd / 100) for n in (11, 101, 1001)}})
    return rows


def series_weighted() -> list[dict]:
    """Reihe 3: einfache und gewichtete Mehrheit bei verschieden guten Gutachtern (q = 60 %), je Spanne und Gutachterzahl."""
    q = C.SERIES_Q_FOR_LIMITS / 100
    rows = []
    for dp in C.SERIES_DELTAS:
        qs = list(competences(q, dp / 100, max(C.SERIES_NS_WEIGHTED)))
        simple = A.poisson_binomial_curve(qs)
        weighted = A.weighted_curve(qs, A.integer_weights(qs))
        for n in C.SERIES_NS_WEIGHTED:
            rows.append({"delta": dp, "n": n, "simple": simple[n], "weighted": weighted[n]})
    return rows


def needed_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({"Trefferquote": f"{r['q']} %", "Ziel": f"{round(100 * r['target'])} %", "Unabhängig": count(r["unabhaengig"]), "Gemeinsamer Hinweis (ρ = 10 %)": count(r["signal"]),
                    "Schwierige Fälle (Streuung 5 Punkte)": count(r["schwierigkeit"])})
    return out


def limit_rows(rows: list[dict], mechanism: str) -> list[dict]:
    label = "ρ (%)" if mechanism == "signal" else "Streuung (Punkte)"
    return [{label: r["x"], "n = 11": pct(r["n11"]), "n = 101": pct(r["n101"]), "n = 1001": pct(r["n1001"]), "Grenzwert": pct(r["limit"])} for r in rows if r["mechanism"] == mechanism]


def weighted_rows(rows: list[dict]) -> list[dict]:
    out = []
    for dp in dict.fromkeys(r["delta"] for r in rows):
        row = {"Spanne (Punkte)": dp}
        for r in rows:
            if r["delta"] == dp:
                row[f"n = {r['n']}: einfach"] = pct(r["simple"])
                row[f"n = {r['n']}: gewichtet"] = pct(r["weighted"])
        out.append(row)
    return out


def verdict_needed(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 1: wie viele Gutachter bei knapper Trefferquote nötig sind und wo ein gemeinsamer Hinweis das Ziel unerreichbar macht."""
    f = lambda q, t: next(r for r in rows if r["q"] == q and r["target"] == t)
    lo, hi = min(C.SERIES_QS), max(C.SERIES_QS)
    return "info", (f"Für 95 % brauchen unabhängige Gutachter bei {lo} % Trefferquote {count(f(lo, 0.95)['unabhaengig'])}, bei {hi} % nur {count(f(hi, 0.95)['unabhaengig'])}. "
                    f"Für 99 % und {hi} % Trefferquote: {count(f(hi, 0.99)['unabhaengig'])} unabhängig, {count(f(hi, 0.99)['signal'])} mit gemeinsamem Hinweis von 10 %, {count(f(hi, 0.99)['schwierigkeit'])} bei schwierigen Fällen (Streuung 5 Punkte).")


def verdict_limits(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 2: bei der stärksten Abhängigkeit, wo die Mehrheit stehen bleibt."""
    sig = [r for r in rows if r["mechanism"] == "signal"]
    dif = [r for r in rows if r["mechanism"] == "schwierigkeit"]
    s, d = sig[-1], dif[-1]
    return "info", (f"Bei q = {C.SERIES_Q_FOR_LIMITS} % bleibt die Mehrheit mit gemeinsamem Hinweis von ρ = {s['x']} % bei {pct(s['limit'])} stehen (bei 1001 Gutachtern {pct(s['n1001'])}) "
                    f"und mit Fallschwierigkeit bei Streuung {d['x']} Punkten bei {pct(d['limit'])} (bei 1001: {pct(d['n1001'])}); unabhängig wäre es {pct(sig[0]['limit'], 0)}.")


def verdict_weighted(rows: list[dict]) -> tuple[str, str]:
    """Verdikt der Reihe 3: was Gewichten bei der größten Spanne und kleinstem n bringt, und dass es ohne Spanne nichts ändert."""
    lo_n = min(C.SERIES_NS_WEIGHTED)
    hi_d = max(C.SERIES_DELTAS)
    g = lambda dp, n: next(r for r in rows if r["delta"] == dp and r["n"] == n)
    return "info", (f"Bei {lo_n} Gutachtern und einer Spanne von ±{hi_d} Punkten liegt die einfache Mehrheit in {pct(g(hi_d, lo_n)['simple'])} richtig, die gewichtete in {pct(g(hi_d, lo_n)['weighted'])}. "
                    f"Ohne Spanne sind beide gleich ({pct(g(0, lo_n)['simple'])}). Die Gewichte setzen bekannte Trefferquoten voraus.")
