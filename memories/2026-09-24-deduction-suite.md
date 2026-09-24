# 2026-09-24 — Déduction : suite (4×4, secours, nouveaux types)

## Demande

« Implémente la suite » de la grille de déduction : grilles 4×4 pour les paliers supérieurs, davantage de types d'indices, et une aide progressive quand on bloque.

## Livré

- **4×4** — palier 4 : 4 figures × 4 couleurs, carré latin d'ordre 4, 12 indices. Le solveur d'unicité est passé **par dimension** (figures et couleurs sont indépendantes : un indice ne relie jamais figure et couleur), donc on énumère 576 carrés au lieu de 576² — rapide et exact.
- **Indices de secours** — 3 par grille (`contenu.indices`), révélés par « Un indice ».
- **Nouveaux types** — coin et bord (figure/couleur), implémentés et validés ; l'injection par palier a fait apparaître ligne/colonne au palier 2 et les négatifs au palier 3.

## Leçons

- **Le nombre d'indices croît avec la grille** : 3×3 se détermine en ~3 indices par dimension (6 au total), 4×4 en ~6 par dimension (12 au total) — mesuré empiriquement sur le solveur avant de figer les budgets.
- **« Un indice de plus » ≠ « montrer la réponse »** : le secours est un indice vrai de plus, pas une fuite. Cohérent avec le principe errorless (aider, pas punir).
- **L'injection de saveur doit préserver l'unicité** : remplacer un indice direct par un indice faible (coin/bord) casse souvent l'unicité — d'où un injecteur qui vérifie et renonce si besoin.

## Reste à faire

- Passage visuel 4×4 + « Un indice » dans le navigateur.
- Relecture orthophoniste.
- Éventuel 5×5 (mais le nombre d'indices deviendrait lourd : à réserver à une variante « expert »).
