# Correction déduction — 2026-09-29

Traçabilité de la correction « preuve exacte du fixe seule » (défaut C).

- `scinder_phrases_solo.py` — réparation du palier 3 : scission des phrases solo en deux chaînes de deux informations (IDs df-3-XX → dc-3-XX). Rejouable sur la base `895efdf` : `python3 .cluster/correction-deduction-20260929/scinder_phrases_solo.py`.
- `auditer_reparation.py` — audit des 13 grilles réparées (solo, détermination, rang, redondances).
- `verifier_enumeration.py` — énumération brute avant/après pour df-3-03.
- `verifier_unicite_13.py` — énumération brute des 13 grilles réparées : 1 solution unique chacune, égale à la stockée.
- `verifier_generateur.py` — conformité du générateur en essai borné (32 grilles, 0 erreur).
- `contenu_avant/` + `mesures_avant_exacte.csv` — état avant correction, mesuré avec l'outil exact.
- `mesures_apres.csv` / `mesures_apres.md` — état après correction.

**Le rapport de la nuit du 28 (`895efdf`, dossier `.cluster/nuit-deduction-20260928/`) est dépassé sur le critère C** : ses conclusions « zéro phrase solo au palier 3 » reposaient sur une détection incomplète (propagation à sens unique). La mesure du 29/09 ci-dessus et l'ADR-016 font foi ; l'historique est conservé tel quel.
