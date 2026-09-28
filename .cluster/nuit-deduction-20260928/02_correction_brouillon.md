# 02 — Correction (voie 2) : défaut C + génération — nuit 2026-09-28

Sous-agent « Génération Déduction ». Dépôt : remediation-cognitive, branche `amelioration-deduction-20260927`. Aucun push, aucune fusion main.

## État : EN COURS

## 1. Commit préalable — modification locale conservée

- `git diff tools/generer_deduction.py` confirmé : palier 3, ajout de 4 négations relatives (`pas-a-droite-de`, `pas-a-gauche-de`, `pas-au-dessus-de`, `pas-en-dessous-de`) à `RELATIONS_PAR_PALIER[3]`. Palier 4 non touché.
- Décision : conservée (mixage anti-grammaire-pure dans le palier relatif ; les critères C bloquent de toute façon toute phrase qui fixerait seule une position).
- Commit : _(à remplir)_

## 2. Défaut C — critères de recoupement

Implémentation (à remplir) :
- Critère 1 (aucune phrase seule ne fixe une position) : …
- Critère 2 (première certitude ≥ 2 phrases, ordre présenté) : …
- Périmètre : bloquant paliers 2/3/4 ; palier 1 mesuré sans bloquer (décision coordinateur : palier 1 = initiation séquentielle, phrases-solo tolérées ; constaté : old stock palier 1 propre sur les redondances, conservé).
- Contrôles validateurs (refus du dépôt) : …
- Tests négatifs : …

## 3. Choix grammaire / vocabulaire requis

- `VOCABULAIRE_REQUIS[2]` : … (aligné requis ∩ réalisable, choix documenté)
- `VOCABULAIRE_REQUIS[3]` : …
- Garde-fou ajouté : …

## 4. Échantillon (3 grilles/palier)

- Palier 1 : … / Palier 2 : … / Palier 3 : … / Palier 4 : …
- Contrôles : validate_items / verifier_reponses / verifier_phrases / pytest / critères C : …

## 5. Stock complet

- Palier 1 : conservé (IDs de-1-*) — motif : conforme, propre sur redondances.
- Paliers 2/3/4 : régénérés, IDs df-*, GRAINE 20260928, date_creation 2026-09-28.
- Commit contenu : _(à remplir)_

## 6. Mesures avant/après

_(tableau comparatif à remplir depuis mesures_avant.csv / mesures_apres.csv)_

## 7. Tests finaux

_(liste des commandes passées, à remplir)_
