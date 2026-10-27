"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

MECHANISMS = {
    "unabhaengig": "Unabhängige Gutachter",
    "signal": "Gemeinsames Signal",
    "schwierigkeit": "Schwierige Fälle",
    "gemischt": "Verschieden gute Gutachter",
    "gewichtet": "Verschieden gute, gewichtet",
}
MECHANISM_TEXT = {
    "unabhaengig": "Jeder Gutachter liegt mit derselben Wahrscheinlichkeit q richtig, unabhängig von den anderen; die einfache Mehrheit entscheidet.",
    "signal": "Mit Wahrscheinlichkeit ρ folgen alle demselben gemeinsamen Hinweis (der mit Wahrscheinlichkeit q stimmt), sonst urteilen sie unabhängig.",
    "schwierigkeit": "Die Trefferquote hängt vom Fall ab: leichte Fälle löst jeder, schwere kaum jemand (im Mittel q, Streuung s zwischen den Fällen); innerhalb eines Falls urteilen die Gutachter unabhängig.",
    "gemischt": "Die Gutachter sind verschieden gut (gleichmäßig verteilt um q mit Spanne δ); einfache Mehrheit.",
    "gewichtet": "Wie zuvor, aber jede Stimme zählt mit dem Gewicht ln(q/(1−q)), auf Hundertstel gerundet (die bekannte Gewichtung für bekannte Trefferquoten; Gleichstand zählt halb).",
}
MECHANISM_COLORS = {"unabhaengig": "#2F6B65", "signal": "#b04a3a", "schwierigkeit": "#e8a838", "gemischt": "#4c78a8", "gewichtet": "#7b6fa8"}

N_MIN, N_MAX, DEFAULT_N = 1, 201, 11          # Zahl der Gutachter (ungerade, damit es kein Unentschieden gibt)
Q_MIN, Q_MAX, DEFAULT_Q = 40, 80, 55          # Trefferquote eines Gutachters in Prozent
RHO_MIN, RHO_MAX, DEFAULT_RHO = 0, 60, 20     # Anteil der Fälle mit gemeinsamem Hinweis in Prozent
SD_MIN, SD_MAX, DEFAULT_SD = 0, 25, 10        # Streuung der Fallschwierigkeit in Prozentpunkten
DELTA_MIN, DELTA_MAX, DEFAULT_DELTA = 0, 30, 10   # Spanne der Gutachterqualität in Prozentpunkten (q − δ bis q + δ)
PLOT_N = tuple(range(1, 202, 2))              # Gutachterzahlen der Kurven
WEIGHT_SCALE = 100                            # Gewichte = round(100 · ln(q / (1 − q)))
Q_FLOOR, Q_CEIL = 0.01, 0.99                  # Trefferquoten werden in diese Grenzen gelegt (kein Gutachter ist sicher)

# Feste Reihen (exakt gerechnet, keine Stichproben)
SERIES_QS = (51, 52, 55, 60, 65, 70)          # Reihe 1: Trefferquoten
SERIES_TARGETS = (0.90, 0.95, 0.99)
SERIES_RHOS = (0, 10, 20, 30, 40, 50)         # Reihe 2: gemeinsamer Hinweis (q = 60 %)
SERIES_SDS = (0, 5, 10, 15, 20)               # Reihe 2: Fallschwierigkeit (q = 60 %)
SERIES_Q_FOR_LIMITS = 60
SERIES_DELTAS = (0, 5, 10, 15, 20, 25, 30)    # Reihe 3: Spanne der Gutachterqualität (q = 60 %)
SERIES_NS_WEIGHTED = (11, 51, 101)
SEARCH_CAP = 2_000_001                        # größte Gutachterzahl bei der Suche „wie viele braucht man“

COLOR_ALERT = "#c0392b"

PRESETS = {
    "Elf Gutachter": {"n": 11, "q": 55, "rho": 20, "sd": 10, "delta": 10},
    "Weisheit der Menge": {"n": 101, "q": 55, "rho": 0, "sd": 0, "delta": 0},
    "Schlechter als der Zufall": {"n": 101, "q": 45, "rho": 0, "sd": 0, "delta": 0},
    "Gemeinsamer Hinweis": {"n": 101, "q": 60, "rho": 30, "sd": 0, "delta": 0},
    "Schwierige Fälle": {"n": 101, "q": 60, "rho": 0, "sd": 15, "delta": 0},
    "Verschieden gute Gutachter": {"n": 11, "q": 60, "rho": 0, "sd": 0, "delta": 30},
}
PRESET_HELP = {
    "Elf Gutachter": "Voreinstellung: elf Gutachter mit 55 % Trefferquote; alle fünf Mechanismen mit mittleren Werten (gemeinsamer Hinweis 20 %, Streuung der Fälle 10 Punkte, Spanne der Gutachter ±10 Punkte).",
    "Weisheit der Menge": "101 unabhängige Gutachter, jeder nur knapp besser als der Zufall (55 %): die Mehrheit liegt in 84,4 % richtig. Das ist der Geschworenensatz von Condorcet.",
    "Schlechter als der Zufall": "101 unabhängige Gutachter mit 45 % Trefferquote: die Mehrheit liegt nur noch in 15,6 % richtig; mehr Gutachter machen es schlechter.",
    "Gemeinsamer Hinweis": "Folgen in 30 % der Fälle alle demselben Hinweis (60 % Trefferquote), kommt die Mehrheit nie über 88 % hinaus, egal wie viele Gutachter es sind; bei 101 sind es 86,5 %.",
    "Schwierige Fälle": "Leichte Fälle löst jeder, schwere kaum einer: bei 15 Punkten Streuung liegt die Mehrheit bei 101 Gutachtern in 73,4 % richtig, mehr als 74,3 % erreicht sie in diesem Modell nie.",
    "Verschieden gute Gutachter": "Elf Gutachter mit Trefferquoten zwischen 30 und 90 %: die einfache Mehrheit liegt in 73,4 % richtig, die nach Trefferquote gewichtete in 90,7 %.",
}
