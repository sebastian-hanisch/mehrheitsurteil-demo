# Mehrheitsurteil: wann hilft die Menge? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-mehrheitsurteil-demo.streamlit.app/)** -->

Stück der Linie **Abstimmen und Fair Teilen** (Konzepte-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“). Verwandt: [wahlregeln-demo](https://github.com/sebastian-hanisch/wahlregeln-demo) (die Mehrheit unter mehreren Kandidaten), [taktisch-waehlen-demo](https://github.com/sebastian-hanisch/taktisch-waehlen-demo) (wer ehrlich urteilt), `meinungsbildung-demo` (wer in einem Netz den Wert bestimmt) und `forecast-combination-demo` (Prognosen mitteln).
Die Demo fragt: **Ein Betrieb lässt n Gutachter über einen Fall urteilen (richtig oder falsch, Los annehmen oder ablehnen); jeder liegt mit der Trefferquote q richtig, die Mehrheit entscheidet – wie oft liegt die Mehrheit richtig, wie viele Gutachter braucht man, und wo hilft mehr nichts mehr?** Der **Geschworenensatz von Condorcet** sagt: bei Trefferquoten über 50 % und unabhängigen Urteilen liegt die Mehrheit mit wachsendem n fast sicher richtig. Die Demo rechnet das **exakt** (keine Simulation) und fügt vier Dinge hinzu, an denen der Satz in der Praxis hängt: **einen gemeinsamen Hinweis**, dem alle folgen, **schwierige Fälle** (die Trefferquote hängt vom Fall ab), **verschieden gute Gutachter** und **gewichtete Stimmen**.

Der Kern ist eigener Code (`numpy`, `scipy` für Binomial-, Beta-Binomial- und Beta-Verteilung): fünf exakte Rechnungen, die Suche nach der kleinsten Gutachterzahl für ein Ziel und die Faltung für verschieden gute Gutachter. Ein unabhängiges Orakel in den Tests zählt **alle 2<sup>n</sup> Urteilsmuster** mit exakten Brüchen auf und rechnet die Beta-Binomialverteilung aus Fakultäten nach; Stichproben der beschriebenen Entstehung der Urteile prüfen die Modelle gegen ihre Erzählung.

## Warum dieses Problem

Die Zahl kommt oft ohne Zusatz daher: „viele Köpfe sind besser als einer“. Die Demo zeigt, **wie schnell** das stimmt, wenn die Voraussetzungen erfüllt sind (11 Gutachter mit 60 % Trefferquote: 75,3 %; 101: 97,9 %; 1001: 100,0 %), **wie wenig** es stimmt, wenn der Vorsprung klein ist (bei 51 % Trefferquote braucht man **6 763** Gutachter für 95 %), und vor allem **wo es aufhört**: folgen in 30 % der Fälle alle demselben Hinweis, **bleibt die Mehrheit bei 88,0 % stehen, egal wie viele Gutachter es sind**. Schwierige Fälle wirken ähnlich: bei 15 Punkten Streuung der Fallschwierigkeit erreicht die Mehrheit nie mehr als 74,3 %.
Dazu kommt der Hinweis, den die Lehrbuchdarstellung oft auslässt: **unter 50 % kippt der Satz** (101 Gutachter mit 45 %: 15,6 %), und wer die Trefferquoten der Gutachter kennt, kann das nutzen: **gewichtete Stimmen** heben die Mehrheit bei einer Spanne von ±30 Punkten und elf Gutachtern von 73,4 auf 90,7 %.

## Modell

**Fall.** Zwei Möglichkeiten, die erste ist richtig. n Gutachter, **n ungerade** (kein Unentschieden). Ein Gutachter urteilt mit Wahrscheinlichkeit q richtig.
**Fünf Mechanismen.** *Unabhängig:* die Zahl der Richtigen ist Bin(n, q), die Mehrheit ist richtig bei mehr als n/2. *Gemeinsames Signal:* mit Wahrscheinlichkeit ρ folgen alle demselben Hinweis (richtig mit Wahrscheinlichkeit q), sonst unabhängig; P = ρ·q + (1 − ρ)·P<sub>unabhängig</sub>. *Schwierige Fälle:* die Trefferquote des Falls ist Beta-verteilt mit Mittel q und der eingestellten Standardabweichung, innerhalb eines Falls urteilen alle unabhängig (Beta-Binomial); Grenzwert = P(Trefferquote des Falls > 50 %). *Verschieden gute Gutachter:* die Trefferquoten liegen gleichmäßig zwischen q − δ und q + δ (deterministisch über die Van-der-Corput-Folge, damit jede Anfangsstrecke gleichmäßig ist); exakte Faltung. *Gewichtet:* Stimme mal round(100 · ln(q/(1 − q))); Gleichstand der gewichteten Summen zählt halb; ein Gutachter unter 50 % bekommt ein negatives Gewicht (seine Stimme wird umgedreht).
**Wie viele Gutachter?** Die kleinste ungerade Zahl mit Wahrscheinlichkeit ≥ Ziel (Verdoppeln, dann Halbieren); „nie“, wenn der Grenzwert unter dem Ziel liegt.
Formeln und Lesehilfe stehen im 📐-Expander der App.

## Methodik

- **Kern** (`mhu_algorithm.py`): die fünf exakten Wahrscheinlichkeiten und ihre Grenzwerte, die Faltungen (`poisson_binomial_curve`, `weighted_curve`), `needed_voters`.
- **Szenario und Auswertung** (`mhu_scenario.py`, `mhu_evaluation.py`): Trefferquoten der Gutachter, Kurven über der Gutachterzahl (ungerade 1 bis 201), Tabelle je Mechanismus, drei feste Reihen, alle Verdikte als reine Funktionen.
- **Oberfläche** (`app.py`): sechs Schnellstart-Szenarien, fünf Regler (Gutachterzahl, Trefferquote, gemeinsamer Hinweis, Streuung der Fallschwierigkeit, Spanne der Gutachter), Kurven über der Gutachterzahl, Tabelle, Kernfrage mit Verdikt, drei Reiter mit exakten Reihen, Annahmen und Formeln.

## Befunde (gemessen, keine Behauptungen)

Alle Werte sind **exakt gerechnet**, keine Stichproben; die Tests prüfen deshalb die gerundeten Anzeigewerte und die Gutachterzahlen ohne Bänder.

| Frage | Befund | Test |
|---|---|---|
| Stimmt der Kern? | Alle fünf Wahrscheinlichkeiten gleich der **Aufzählung aller 2<sup>n</sup> Urteilsmuster** mit Brüchen (n bis 11; die Faltungen mit den gerundeten Gewichten auch); die Beta-Binomialverteilung gleich der Rechnung aus Fakultäten (ganze Beta-Parameter) und der Grenzwert gleich der Binomialsumme; **Stichproben** (je 200 000 Fälle, Zufalls-Seed fest) bestätigen jede Erzählung innerhalb von ±0,6 Punkten; Handrechnungen mit Rechnung im Kommentar. | `test_oracle_mehrheitsurteil.py`, `test_algorithm.py` |
| Der Satz von Condorcet (unabhängig) | Mit 11 / 101 / 1001 Gutachtern: **55 %**: 63,3 / 84,4 / 99,9 %; **60 %**: 75,3 / 97,9 / 100,0 %; **70 %**: 92,2 / 100,0 / 100,0 %; **51 %**: 52,7 / 58,0 / 73,7 %. **Unter 50 % kippt er:** bei 45 % 36,7 / 15,6 / 0,1 %. | `test_claims.py::test_independent_majority_table` |
| Wie viele Gutachter braucht man? | Für 95 % bei unabhängigen Urteilen: **6 763** (51 %), 1 691 (52 %), **269** (55 %), **67** (60 %), 29 (65 %), 17 (70 %); für 99 % bei 70 %: 31. | `test_claims.py::test_series_needed_table` |
| Was macht ein gemeinsamer Hinweis? | Die Mehrheit bleibt bei ρ·q + (1 − ρ) stehen: bei q = 60 % und ρ = 10, 20, 30, 40, 50 % bei **96, 92, 88, 84, 80 %**; schon bei 1001 Gutachtern sind die Grenzwerte erreicht (96,0 … 80,0 %). Bei ρ = 10 % ist **99 % für keine Trefferquote bis 70 %** erreichbar, und 95 % braucht bei 60 % 129 statt 67 Gutachter. | `test_claims.py::test_series_limits_signal`, `…::test_a_common_hint_of_ten_percent_makes_99_percent_unreachable_up_to_a_hit_rate_of_70` |
| Und schwierige Fälle? | Grenzwert bei q = 60 % und Streuung 0, 5, 10, 15, 20 Punkten: **100,0, 97,5, 83,7, 74,3, 68,75 %** (der letzte Wert ist genau 11/16 und wird auf einer Stelle je nach Plattform als 68,7 oder 68,8 gerundet) (mit 1001 Gutachtern 100,0, 97,0, 83,4, 74,2, 68,7 %). Bei 5 Punkten Streuung und q ≤ 55 % ist 90 % **nie** erreichbar (Grenzwert 57,9 % bei 51 %). | `test_claims.py::test_series_limits_difficulty`, `…::test_case_difficulty_of_five_points_makes_it_unreachable_at_low_hit_rates` |
| Hilft Gewichten? | Bei elf Gutachtern, q = 60 % und der Spanne 0, 10, 20, 30 Punkte: einfach **75,3 / 74,5 / 73,8 / 73,4 %**, gewichtet **75,3 / 77,3 / 83,7 / 90,7 %**; bei 51 Gutachtern und ±30 Punkten 92,6 gegen **99,9 %**. Die einfache Mehrheit merkt die Spanne kaum (73,4 bis 75,3 %); die gewichtete war in keiner Zelle schlechter. Das setzt **bekannte** Trefferquoten voraus. | `test_claims.py::test_series_weighted_table`, `…::test_weighting_never_loses_and_gains_more_with_a_wider_spread` |
| Schlechter als der Zufall | Bei 45 % und 101 unabhängigen Gutachtern liegt die Mehrheit in 15,6 % richtig; die **gewichtete** (negative Gewichte drehen jede Stimme um) in **84,4 %**. | `test_claims.py::test_presets_tell_their_stories` |
| Schnellstart-Szenarien | „Elf Gutachter“ (alle fünf Mechanismen bei 11 Gutachtern: 63,3 / 61,6 / 61,3 / 62,2 / 68,2 %, für 95 % brauchen die unabhängigen 269, mit gemeinsamem Hinweis oder schwierigen Fällen nie, die gewichteten 117); Weisheit der Menge (84,4 %); schlechter als der Zufall (15,6 %); gemeinsamer Hinweis (86,5 %, Grenzwert 88 %); schwierige Fälle (73,4 %, Grenzwert 74,3 %); verschieden gute Gutachter (73,4 gegen 90,7 %). | `test_claims.py::test_presets_tell_their_stories`, `…::test_the_help_texts_name_the_numbers` |
| Vormessung | Die Werte der Vormessung (57,5 / 63,3 / 84,4 / 99,9 % bei q = 0,55; 88,0 % bei ρ = 0,3 und q = 0,6; 0,1 % bei q = 0,45 und n = 1001) stimmen mit den hier gerechneten überein. | `test_claims.py::test_independent_majority_table`, `…::test_series_limits_signal` |

## Ehrliche Grenzen

- **Zwei Möglichkeiten, eine ist richtig.** Bei mehr Ergebnissen gilt der Satz in anderer Form, die Demo behandelt nur richtig oder falsch. Gerade Gutachterzahlen sind ausgeschlossen (Unentschieden).
- **Die Trefferquote ist bekannt (für die Gewichte) und wird als gegeben angenommen.** In der Praxis kennt man q nicht, und es hängt vom Fall ab (Mechanismus „schwierige Fälle“); mit geschätzten Trefferquoten fällt der Gewinn des Gewichtens kleiner aus, mit falschen kann er negativ werden. Die Gewichte sind **auf Hundertstel gerundete** ln(q/(1 − q)); die bekannte Optimalität gilt für die ungerundeten Gewichte (aus dem Gedächtnis).
- **Zwei Abhängigkeitsmodelle, nicht alle.** Gemeinsamer Hinweis und Fallschwierigkeit sind zwei einfache Mechanismen; echte Abhängigkeit (Nachahmung, Netze, gemeinsame Ausbildung) kann anders aussehen. Ihre Grenzwerte hängen an den Parametern der Modelle, nicht an Messungen echter Gremien.
- **Der Pool „verschieden gut“ ist deterministisch** (Van-der-Corput-Folge), keine Zufallsziehung; die Kurven nehmen dieselben Gutachter nacheinander dazu. „Nicht bis 201“ heißt: bis zur größten Gutachterzahl der Kurven nicht erreicht, kein Schluss auf größere Zahlen.
- **Ehrliche Urteile:** jeder gibt sein bestes Urteil ab; taktisches Urteilen ist ein eigenes Thema.
- **Literatur** (aus dem Gedächtnis, nicht im Original geprüft): Condorcet (1785); Ladha (1992) zur Abhängigkeit; Nitzan und Paroush (1982) zu optimalen Gewichten; Dietrich und Spiekermann (2013) zu fallabhängigen Trefferquoten.

## Befunde und Korrekturen gegenüber dem Plan

- **Port:** 9195 (9170 bis 9194 sind vergeben).
- **Plan:** „exakte Binomialsumme; Simulation; Handfälle (n = 3)“. Umgesetzt: exakte Rechnung, **Aufzählung** mit Brüchen statt nur Simulation (die Stichproben bleiben als Gegenprobe der Erzählung), Handfälle mit n = 3.
- **Neu gegenüber dem Plan:** die **Fallschwierigkeit** (Beta-Binomial) als zweiter Abhängigkeitsmechanismus, **verschieden gute Gutachter** mit einfacher und gewichteter Mehrheit und die Frage **„wie viele Gutachter?“** mit der Unterscheidung „nie“ (Grenzwert unter dem Ziel) und „nicht bis 201“.
- **Vormessung:** „ρ = Anteil der Fälle, in denen alle dem gemeinsamen Signal folgen“ ist hier derselbe Mechanismus („Gemeinsames Signal“); die Zahlen stimmen überein (siehe Tabelle).
- **Reglerspanne:** Gutachter 1 bis 201 (ungerade), Trefferquote 40 bis 80 %, ρ 0 bis 60 %, Streuung 0 bis 25 Punkte, Spanne 0 bis 30 Punkte.

## Verifikation

- **Kern:** jede Einheit an Mini-Fällen von Hand (Binomialmehrheit für n = 1, 3, 5, die Mischung des gemeinsamen Signals, die Beta-Binomialrechnung mit Beta(2, 1), die Faltungen, die Gewichte und der Gleichstand, die Suche nach der kleinsten Gutachterzahl).
- **Orakel:** Aufzählung aller 2<sup>n</sup> Urteilsmuster mit Brüchen (alle fünf Mechanismen), Beta-Binomial aus Fakultäten, Stichproben der Erzählung, Spiegelung q ↔ 1 − q, Monotonie in n, Annäherung an die Grenzwerte, Prüfung gegen einen linearen Durchlauf bei der Suche, Prüfung, dass die Vergleiche nicht leer laufen (Gewichten ändert etwas, Abhängigkeit senkt die Mehrheit).
- **Verdikte:** reine Funktionen, jeder Zweig und jede Zahl im Text an handgesetzten Werten (`tests/test_verdicts.py`), Randfälle an den Reglergrenzen und eine gerade Gutachterzahl aus der Adresszeile (`tests/test_edge_cases.py`).
- **Presets, Layout, Oberfläche:** wie in allen Demos (Presets vollständig und im Regelbereich, keines auf einem Rand von Gutachterzahl und Trefferquote, kein Preset entsteht durch Änderung eines einzigen Reglers, Schnellstart oben, aktives Preset hervorgehoben, AppTest jeder Button und jeder Regler an den Rändern, Footer, Laufzeit-Importe).
- **Mutationsprüfung** (`tools/mutate_demo.py`): 122 Stellen im Kern `mhu_algorithm.py`, **106 gefangen** (2 davon über wortgleiche Zeilen in Nachbar-Demos), **11 als äquivalent festgehalten**, **5 Mutanten mit Zeitüberschreitung** (Endlosschleifen der Halbierungssuche in `needed_voters`; sie zählen nicht als gefangen). Der erste Lauf ließ 14 überleben: zehn in der Suche nach der Gutachterzahl, **darunter eine tote Absicherung** (`mid >= hi` war nie erreichbar), weshalb die Suche über den Index k der ungeraden Zahlen 2k + 1 neu geschrieben wurde; echte Lücken waren der Fall „Grenzwert gleich Ziel“, „Ziel genau getroffen“ und eine Beta-Verteilung mit Parametern unter 1 (`test_needed_voters_at_the_edges_of_the_search`, `test_beta_parameters_below_one`). Die 11 äquivalenten: die Klammer der Halbierung (jede Klammer um die Lösung liefert dieselbe Zahl), die Obergrenze der Verdopplung (wird nie genau getroffen), eine überzählige Prüfung von n < 1 neben der Prüfung auf gerade Zahlen und die Größe des Feldes der Gewichtssummen.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `mhu_algorithm.py` | Kern: exakte Wahrscheinlichkeiten, Faltungen, Suche |
| `mhu_constants.py` | Regler-Grenzen, feste Reihen, Farben, Presets |
| `mhu_evaluation.py` | Kurven, Tabelle, Reihen, Verdikte |
| `mhu_layout.py` | Fester Kopf (Stylesheet) |
| `mhu_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `mhu_scenario.py` | Trefferquoten verschieden guter Gutachter (Van-der-Corput-Folge) |
| `mhu_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `messen.py` | Einmalige Messung der Zahlen in dieser README (nicht Teil der App) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Kern, Orakel mit Aufzählung und Stichproben, Verdikte, Randfälle, Presets, Abbildungen, Layout, AppTest, Footer, Laufzeit-Importe, Claims |

## Bewusst nicht umgesetzt

- **Mehr als zwei Ergebnisse** (Mehrheit unter mehreren Möglichkeiten, Pluralität): ein anderes Problem mit eigenen Sätzen.
- **Abhängigkeit über ein Netz** (wer beeinflusst wen): dafür steht die Netzwerkanalyse; hier genügen zwei einfache Mechanismen.
- **Die Trefferquoten schätzen** (aus früheren Urteilen lernen, wem man trauen darf) und **Stimmenthaltung**: die Demo setzt bekannte Quoten voraus.
- **Unterschiedlicher Aufwand oder Kosten** je Gutachter und die Frage, wie viele sich lohnen: ein Entscheidungsproblem für sich.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
