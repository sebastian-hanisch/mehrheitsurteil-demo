"""Einmalige Messung der README-Zahlen (nicht Teil der App): feste Pläne, Ausgabe auf stdout. Alle Werte sind exakt gerechnet."""

import sys
import time

sys.path.insert(0, ".")
import mhu_constants as C
import mhu_evaluation as ev

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

t0 = time.time()
print("PRESETS")
for name, p in C.PRESETS.items():
    a = ev.analyse(ev.Settings(**p))
    print(name, p)
    for r in ev.mechanism_rows(a):
        print("   ", r)
    print("   ", ev.verdict_state(a))

rows = ev.series_needed()
print("REIHE 1 (Gutachter für das Ziel)")
for r in ev.needed_rows(rows):
    print("   ", r)
print("   ", ev.verdict_needed(rows))
rows = ev.series_limits()
print("REIHE 2 (Grenzwerte, q = 60 %)")
for mech in ("signal", "schwierigkeit"):
    for r in ev.limit_rows(rows, mech):
        print("   ", mech, r)
print("   ", ev.verdict_limits(rows))
rows = ev.series_weighted()
print("REIHE 3 (einfach gegen gewichtet, q = 60 %)")
for r in ev.weighted_rows(rows):
    print("   ", r)
print("   ", ev.verdict_weighted(rows))
print("sec", round(time.time() - t0, 1))
