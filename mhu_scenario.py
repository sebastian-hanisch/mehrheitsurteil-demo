"""Szenario: die Trefferquoten der Gutachter."""

import numpy as np

import mhu_constants as C


def van_der_corput(j: int, base: int = 2) -> float:
    """j-te Zahl der Van-der-Corput-Folge in [0, 1): gleichmäßig verteilt für jede Länge, deterministisch."""
    x, denom = 0.0, 1.0
    while j > 0:
        j, digit = divmod(j, base)
        denom *= base
        x += digit / denom
    return x


def competences(q: float, delta: float, n: int) -> np.ndarray:
    """Trefferquoten von n Gutachtern: q + δ · u_j mit u_j aus der Van-der-Corput-Folge auf [−1, 1) (der erste hat genau q), in [Q_FLOOR, Q_CEIL] gelegt.

    Die Folge macht jede Anfangsstrecke gleichmäßig; die Kurven über der Gutachterzahl nehmen deshalb dieselben Gutachter nacheinander dazu."""
    u = np.array([2 * van_der_corput(j) - 1 for j in range(1, n + 1)])
    return np.clip(q + delta * u, C.Q_FLOOR, C.Q_CEIL)


def mean_competence(q: float, delta: float) -> float:
    """Mittel der Trefferquoten im Modell „verschieden gut“ für unendlich viele Gutachter: der Mittelwert von q + δ · u mit u gleichverteilt auf [−1, 1), in [Q_FLOOR, Q_CEIL] gelegt (stückweise Integration).
    Die ersten n Werte der Van-der-Corput-Folge haben für endliches n ein Mittel, das knapp daneben liegt (bei q = 50 % knapp unter 50 %) und den Grenzwert bei q = 50 % kippen würde."""
    if delta == 0:
        return float(min(max(q, C.Q_FLOOR), C.Q_CEIL))
    a, b = q - delta, q + delta
    lo, hi = C.Q_FLOOR, C.Q_CEIL
    total = 0.0
    if a < lo:
        total += lo * (min(b, lo) - a)
    left, right = max(a, lo), min(b, hi)
    if left < right:
        total += (right * right - left * left) / 2
    if b > hi:
        total += hi * (b - max(a, hi))
    return total / (b - a)
