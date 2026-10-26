"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, keiner auf einem Rand von Gutachterzahl und Trefferquote, keiner durch eine einzelne Regleränderung vom Standard."""

import mhu_constants as C
import mhu_evaluation as ev
import mhu_presets as P

FIRST = "Elf Gutachter"
BOUNDS = {"n": (C.N_MIN, C.N_MAX), "q": (C.Q_MIN, C.Q_MAX), "rho": (C.RHO_MIN, C.RHO_MAX), "sd": (C.SD_MIN, C.SD_MAX), "delta": (C.DELTA_MIN, C.DELTA_MAX)}


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds_and_n_is_odd():
    for name, p in C.PRESETS.items():
        for key, (lo, hi) in BOUNDS.items():
            assert lo <= p[key] <= hi, (name, key)
        assert p["n"] % 2 == 1, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[FIRST]) == ev.Settings()
    assert C.DEFAULT_N % 2 == 1 and C.N_MIN % 2 == 1 and C.N_MAX % 2 == 1


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_preset_sits_on_a_bound_of_n_or_q():
    for name, preset in C.PRESETS.items():
        for key in ("n", "q"):
            lo, hi = BOUNDS[key]
            assert preset[key] not in (lo, hi), (name, key)


def test_no_single_change_of_the_default_produces_another_preset():
    default = C.PRESETS[FIRST]
    for name, p in C.PRESETS.items():
        if name != FIRST:
            assert sum(1 for k in p if p[k] != default[k]) >= 2, name


def test_presets_are_pairwise_different():
    values = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(values)) == len(values)


def test_every_preset_has_a_valid_beta_for_its_difficulty():
    for name, p in C.PRESETS.items():
        assert (p["sd"] / 100) ** 2 < (p["q"] / 100) * (1 - p["q"] / 100), name
