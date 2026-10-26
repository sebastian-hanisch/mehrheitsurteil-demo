"""Mehrheitsurteil: wann hilft die Menge? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück der Linie „Abstimmen und Fair Teilen“ (Geschworenensatz von Condorcet): n Gutachter urteilen über einen Fall, jeder liegt mit der Trefferquote q richtig, die Mehrheit entscheidet. Fünf Mechanismen werden
EXAKT gerechnet (Binomial-, Beta-Binomialverteilung, Faltung): unabhängig, gemeinsamer Hinweis, schwierige Fälle, verschieden gute Gutachter einfach und gewichtet. Der Kern liegt in mhu_algorithm.py.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import mhu_constants as C
import mhu_evaluation as ev
from mhu_evaluation import Settings, analyse, limit_rows, mechanism_rows, needed_rows, num, verdict_limits, verdict_needed, verdict_state, verdict_weighted, weighted_rows
from mhu_layout import dunkles_design, kopf_css
from mhu_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from mhu_visualization import build_curves, build_limits, build_needed, build_weighted

st.set_page_config(page_title="Mehrheitsurteil – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _series_needed():
    return ev.series_needed()


@st.cache_data(show_spinner=False)
def _series_limits():
    return ev.series_limits()


@st.cache_data(show_spinner=False)
def _series_weighted():
    return ev.series_weighted()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mhu_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗳️ Mehrheitsurteil: wann hilft die Menge?")
st.markdown(
    """
Ein Betrieb lässt **n Gutachter** über einen Fall urteilen (Los annehmen oder ablehnen, Störung melden oder nicht). Jeder Gutachter liegt mit der **Trefferquote q** richtig, die **Mehrheit** entscheidet. Der **Geschworenensatz von Condorcet** sagt: ist jeder Gutachter besser als der Zufall (q über 50 %) und urteilen sie **unabhängig**, liegt die Mehrheit mit wachsendem n **fast sicher** richtig; ist jeder schlechter als der Zufall, fast sicher falsch.
Die Demo rechnet das **exakt** (keine Simulation) und zeigt, **wo die „Weisheit der Menge“ endet**: wenn die Gutachter **demselben Hinweis folgen** (gemeinsames Signal), wenn manche Fälle **schwer** sind (die Trefferquote hängt vom Fall ab) und wie viel es bringt, wenn die Gutachter **verschieden gut** sind und man ihre Stimmen **gewichtet**.
Verwandt: `meinungsbildung-demo` (wer in einem Netz den Wert bestimmt), `forecast-combination-demo` (Prognosen mitteln), `wahlregeln-demo` (Mehrheit unter mehreren Kandidaten).

Weiter unten: der Abschnitt **🔬 Exakte Reihen**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So wird gerechnet", expanded=True):
    st.markdown(
        """
1. **Unabhängig:** die Zahl der richtigen Urteile ist binomialverteilt (n, q); die Mehrheit liegt richtig, wenn mehr als n/2 richtig liegen. n ist ungerade, damit es kein Unentschieden gibt.
2. **Gemeinsames Signal:** mit Wahrscheinlichkeit ρ folgen alle demselben Hinweis, der mit Wahrscheinlichkeit q stimmt; sonst urteilen sie unabhängig. Die Wahrscheinlichkeit ist ρ·q + (1 − ρ)·(unabhängiger Wert).
3. **Schwierige Fälle:** die Trefferquote p des Falls ist Beta-verteilt mit Mittel q und der eingestellten Streuung; innerhalb eines Falls urteilen alle unabhängig (Beta-Binomial). Der Grenzwert ist die Wahrscheinlichkeit, dass p über 50 % liegt.
4. **Verschieden gute Gutachter:** die Trefferquoten liegen gleichmäßig zwischen q − δ und q + δ (deterministisch verteilt), die Zahl der Richtigen ist Poisson-Binomial-verteilt (exakte Faltung). **Gewichtet:** Stimme mal ln(q/(1−q)), gerundet auf Hundertstel; ein Gutachter unter 50 % bekommt ein negatives Gewicht, seine Stimme wird umgedreht.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()
if st.session_state["n_slider"] % 2 == 0:                      # die Gutachterzahl ist ungerade; ein gerader Wert aus der Adresszeile rückt eins nach oben
    st.session_state["n_slider"] = min(C.N_MAX, st.session_state["n_slider"] + 1)

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    n = st.slider("Gutachter (ungerade)", *bounds("n_slider"), step=2, key="n_slider", help="Zahl der Gutachter; ungerade, damit es kein Unentschieden gibt.")
    q = st.slider("Trefferquote q (%)", *bounds("q_slider"), key="q_slider", help="Wie oft ein Gutachter richtig liegt. Unter 50 % ist er schlechter als der Zufall.")
    rho = st.slider("Gemeinsamer Hinweis ρ (%)", *bounds("rho_slider"), key="rho_slider", help="In diesem Anteil der Fälle folgen alle Gutachter demselben Hinweis, der mit Wahrscheinlichkeit q stimmt. 0 = unabhängig.")
    sd = st.slider("Streuung der Fallschwierigkeit (Punkte)", *bounds("sd_slider"), key="sd_slider", help="Standardabweichung der Trefferquote zwischen den Fällen. 0 = alle Fälle gleich schwer.")
    delta = st.slider("Spanne der Gutachter ± (Punkte)", *bounds("delta_slider"), key="delta_slider", help="Die Trefferquoten der Gutachter liegen gleichmäßig zwischen q − δ und q + δ. 0 = alle gleich gut.")

sync_query_params({"n_slider": int(n), "q_slider": int(q), "rho_slider": int(rho), "sd_slider": int(sd), "delta_slider": int(delta)})

settings = Settings(n=int(n), q=int(q), rho=int(rho), sd=int(sd), delta=int(delta))
with st.spinner("Rechne die Wahrscheinlichkeiten …"):
    a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
m1.metric("Gutachter · Trefferquote", f"{settings.n} · {settings.q} %", delta="schlechter als der Zufall" if settings.q < 50 else ("genau Zufall" if settings.q == 50 else "besser als der Zufall"), delta_color="off")
m2.metric("Mehrheit richtig (unabhängig)", ev.pct(a.at_n["unabhaengig"]), delta=f"Grenzwert {ev.pct(a.limits['unabhaengig'], 0)}", delta_color="off")
m3.metric("Mehrheit richtig (gemeinsamer Hinweis)", ev.pct(a.at_n["signal"]), delta=f"Grenzwert {ev.pct(a.limits['signal'])}", delta_color="off")
st.table(mechanism_rows(a))
st.plotly_chart(build_curves(a), width="stretch", key="curves_chart")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viele Gutachter braucht man, und wo hilft mehr nichts mehr?")
kind, text = verdict_state(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Reihen --------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Exakte Reihen")
st.caption("Feste Programme, unabhängig von den Reglern. Alle Werte sind exakt gerechnet (keine Stichprobe); jede Reihe rechnet auf Klick in weniger als einer Sekunde bis wenigen Sekunden.")
tab1, tab2, tab3 = st.tabs(["Wie viele Gutachter?", "Wo bleibt die Mehrheit stehen?", "Was bringt Gewichten?"])
with tab1:
    st.markdown("**Kleinste ungerade Gutachterzahl** für 90, 95 und 99 % je Trefferquote: unabhängig, mit gemeinsamem Hinweis (ρ = 10 %) und bei schwierigen Fällen (Streuung 5 Punkte). „nie“: der Grenzwert liegt unter dem Ziel.")
    if st.button("Reihe rechnen", key="needed_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_needed()
        st.session_state["needed_done"] = time.perf_counter() - t0
    if "needed_done" in st.session_state:
        rows = _series_needed()
        st.plotly_chart(build_needed(rows), width="stretch", key="needed_chart")
        st.table(needed_rows(rows))
        kind, text = verdict_needed(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['needed_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab2:
    st.markdown(f"**Wie weit kommt die Mehrheit mit wachsender Gutachterzahl?** Trefferquote {C.SERIES_Q_FOR_LIMITS} %; Werte bei 11, 101 und 1001 Gutachtern und der Grenzwert.")
    if st.button("Reihe rechnen", key="limits_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_limits()
        st.session_state["limits_done"] = time.perf_counter() - t0
    if "limits_done" in st.session_state:
        rows = _series_limits()
        st.markdown("*Gemeinsamer Hinweis*")
        st.plotly_chart(build_limits(rows, "signal"), width="stretch", key="limits_signal_chart")
        st.table(limit_rows(rows, "signal"))
        st.markdown("*Schwierige Fälle*")
        st.plotly_chart(build_limits(rows, "schwierigkeit"), width="stretch", key="limits_difficulty_chart")
        st.table(limit_rows(rows, "schwierigkeit"))
        kind, text = verdict_limits(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['limits_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")
with tab3:
    st.markdown(f"**Verschieden gute Gutachter, einfache und gewichtete Mehrheit.** Trefferquote im Mittel {C.SERIES_Q_FOR_LIMITS} %, Spanne wächst; die Gewichte setzen bekannte Trefferquoten voraus.")
    if st.button("Reihe rechnen", key="weighted_button"):
        t0 = time.perf_counter()
        with st.spinner("Rechne die Reihe …"):
            _series_weighted()
        st.session_state["weighted_done"] = time.perf_counter() - t0
    if "weighted_done" in st.session_state:
        rows = _series_weighted()
        st.plotly_chart(build_weighted(rows), width="stretch", key="weighted_chart")
        st.table(weighted_rows(rows))
        kind, text = verdict_weighted(rows)
        getattr(st, kind)(text)
        st.caption(f"Rechenzeit dieser Sitzung: {num(st.session_state['weighted_done'], 1)} s (beim ersten Mal; danach liegt das Ergebnis im Zwischenspeicher).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Zwei Möglichkeiten, eine ist richtig** | Bei mehr als zwei Ergebnissen gilt der Satz in anderer Form (die Mehrheit ist schwerer zu definieren); die Demo behandelt nur den Fall richtig oder falsch. | diese Demo |
| **Die Trefferquote ist bekannt und für alle Fälle gleich** | In der Praxis kennt man q nicht, und sie hängt vom Fall ab (Mechanismus „schwierige Fälle“). | diese Demo (dritter Mechanismus) |
| **Unabhängige Gutachter** | Gemeinsame Quellen, Absprachen und Nachahmung begrenzen die Mehrheit auf einen Grenzwert (Mechanismen „gemeinsamer Hinweis“ und „schwierige Fälle“); mehr Gutachter helfen dann nicht mehr. | diese Demo |
| **Ehrliche Urteile** | Wer weiß, wie abgestimmt wird, kann taktisch urteilen; hier gibt jeder sein bestes Urteil ab. | `taktisch-waehlen-demo` |
| **Gewichte aus bekannten Trefferquoten** | Das gewichtete Votum braucht die Trefferquoten der Gutachter vorab; mit geschätzten Werten fällt der Gewinn kleiner aus, mit falschen kann er negativ werden. | diese Demo (letzter Mechanismus) |
| **Modell, kein Befund über Gremien** | Die Zahlen sagen, was die Rechnung unter den Annahmen liefert, nicht, wie gut echte Gremien urteilen. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Unabhängig.** $X \sim \text{Bin}(n, q)$ zählt die richtigen Urteile; die Mehrheit ist richtig mit $P(X > n/2)$ für ungerades $n$.

**Gemeinsames Signal.** Mit Wahrscheinlichkeit $\rho$ folgen alle einem gemeinsamen Hinweis, der mit Wahrscheinlichkeit $q$ stimmt: $P = \rho\, q + (1-\rho)\, P_{\text{unabhängig}}(n, q)$. Für $n \to \infty$ und $q > 1/2$: $P \to \rho\, q + (1 - \rho)$.

**Schwierige Fälle.** Die Trefferquote $p$ des Falls ist $\text{Beta}(a, b)$-verteilt mit Mittel $q$ und Standardabweichung $s$: $\kappa = q(1-q)/s^2 - 1$, $a = q\kappa$, $b = (1-q)\kappa$. Die Zahl der Richtigen ist beta-binomial, $P(X > n/2)$; für $n \to \infty$ gilt $P \to P(p > 1/2) = 1 - I_{1/2}(a, b)$.

**Verschieden gute Gutachter.** Gutachter $j$ hat Trefferquote $q_j$; die Zahl der Richtigen ist Poisson-Binomial-verteilt, ihre Verteilung folgt durch Faltung. **Gewichtet:** $w_j = \text{round}(100 \ln \frac{q_j}{1-q_j})$, die Mehrheit ist richtig, wenn $\sum_j w_j x_j > 0$ mit $x_j = +1$ bei richtigem Urteil und $-1$ sonst (Summe 0 zählt halb). Diese Gewichte maximieren die Wahrscheinlichkeit für bekannte Trefferquoten (Nitzan und Paroush 1982, aus dem Gedächtnis; hier auf Hundertstel gerundet).

**Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Condorcet (1785) zum Geschworenensatz; Ladha (1992) zur Abhängigkeit zwischen Wählern; Nitzan und Paroush (1982) zu optimalen Gewichten; Dietrich und Spiekermann (2013) zu unabhängigen und fallabhängigen Trefferquoten.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
