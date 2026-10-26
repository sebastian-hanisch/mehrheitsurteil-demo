"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mhu_constants as C

DASHES = {"unabhaengig": "solid", "signal": "dash", "schwierigkeit": "dot", "gemischt": "dashdot", "gewichtet": "longdash"}


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.28), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_curves(a):
    """Wie oft die Mehrheit richtig liegt, über der Gutachterzahl (logarithmische Achse), je Mechanismus eine Linie; senkrechte Linie bei der gewählten Gutachterzahl."""
    fig = go.Figure()
    for key in C.MECHANISMS:
        fig.add_trace(go.Scatter(x=list(a.ns), y=a.curves[key], mode="lines", name=C.MECHANISMS[key], line=dict(color=C.MECHANISM_COLORS[key], width=2.5, dash=DASHES[key]),
                                 hovertemplate="%{x} Gutachter: %{y:.1%}<extra>" + C.MECHANISMS[key] + "</extra>"))
    fig.add_hline(y=0.5, line_color="rgba(128,128,128,0.6)", line_dash="dot", annotation_text="Zufall", annotation_position="bottom right")
    fig.add_vline(x=a.settings.n, line_color=C.COLOR_ALERT, line_dash="dash", annotation_text=f"n = {a.settings.n}", annotation_position="top left")
    fig.update_xaxes(type="log", title_text="Zahl der Gutachter (ungerade)")
    fig.update_yaxes(title_text="Mehrheit liegt richtig", range=[0, 1.02], tickformat=".0%")
    return _base(fig, height=420)


def build_needed(rows, target=0.95):
    """Gutachter für das Ziel je Trefferquote (logarithmische Achse); „nie“ erscheint als Lücke."""
    fig = go.Figure()
    sel = [r for r in rows if r["target"] == target]
    for key, name, color in (("unabhaengig", "Unabhängig", C.MECHANISM_COLORS["unabhaengig"]), ("signal", "Gemeinsamer Hinweis (ρ = 10 %)", C.MECHANISM_COLORS["signal"]),
                             ("schwierigkeit", "Schwierige Fälle (Streuung 5 Punkte)", C.MECHANISM_COLORS["schwierigkeit"])):
        ys = [r[key] if r[key] not in (None, float("inf")) else None for r in sel]
        fig.add_trace(go.Bar(x=[f"{r['q']} %" for r in sel], y=ys, name=name, marker_color=color, hovertemplate="%{x}: %{y:,} Gutachter<extra>" + name + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(type="log", title_text=f"Gutachter für {round(100 * target)} %")
    fig.update_xaxes(title_text="Trefferquote eines Gutachters")
    return _base(fig, height=360)


def build_limits(rows, mechanism):
    """Mehrheit richtig bei 11, 101 und 1001 Gutachtern und der Grenzwert (gestrichelt) über der Stärke der Abhängigkeit."""
    sel = [r for r in rows if r["mechanism"] == mechanism]
    fig = go.Figure()
    for key, name, dash in (("n11", "11 Gutachter", "solid"), ("n101", "101 Gutachter", "solid"), ("n1001", "1001 Gutachter", "solid"), ("limit", "Grenzwert", "dash")):
        fig.add_trace(go.Scatter(x=[r["x"] for r in sel], y=[r[key] for r in sel], mode="lines+markers", name=name, line=dict(dash=dash, width=2),
                                 hovertemplate="%{x}: %{y:.1%}<extra>" + name + "</extra>"))
    fig.update_xaxes(title_text="ρ in %" if mechanism == "signal" else "Streuung der Fallschwierigkeit in Punkten", type="category")
    fig.update_yaxes(title_text="Mehrheit liegt richtig", range=[0.5, 1.02], tickformat=".0%")
    return _base(fig, height=340)


def build_weighted(rows):
    """Einfache und gewichtete Mehrheit über der Spanne der Gutachterqualität, je Gutachterzahl ein Paar von Linien."""
    fig = go.Figure()
    for n in dict.fromkeys(r["n"] for r in rows):
        sel = [r for r in rows if r["n"] == n]
        fig.add_trace(go.Scatter(x=[r["delta"] for r in sel], y=[r["simple"] for r in sel], mode="lines+markers", name=f"einfach, n = {n}", line=dict(dash="dash"), hovertemplate="±%{x} Punkte: %{y:.1%}<extra>einfach, n = " + str(n) + "</extra>"))
        fig.add_trace(go.Scatter(x=[r["delta"] for r in sel], y=[r["weighted"] for r in sel], mode="lines+markers", name=f"gewichtet, n = {n}", hovertemplate="±%{x} Punkte: %{y:.1%}<extra>gewichtet, n = " + str(n) + "</extra>"))
    fig.update_xaxes(title_text="Spanne der Trefferquoten (± Punkte)", type="category")
    fig.update_yaxes(title_text="Mehrheit liegt richtig", range=[0.5, 1.02], tickformat=".0%")
    return _base(fig, height=360)
