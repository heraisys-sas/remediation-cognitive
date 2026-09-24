# 2026-09-24 — Déduction : indices à deux informations (retour d'usage)

## Le retour

« Les phrases doivent contenir 2 informations, et chacune des figures colorées ne peut être présente qu'une seule fois dans la grille. »

## Ce que ça change (et pourquoi c'est juste)

Le retour corrige une faiblesse de ma première version. Avec deux carrés latins indépendants, une figure apparaissait trois fois : « le carré est sur la même ligne que le bleu » était donc **ambigu** (trois carrés). J'avais contourné le problème en supprimant ce type d'indice — au lieu de corriger la cause.

La correction : rendre la grille **orthogonale** — chaque **figure colorée** (carré bleu, cercle rouge…) apparaît **exactement une fois**. Dès lors, une figure colorée est un objet unique, et une phrase peut porter **deux informations** sans ambiguïté :

- « Le carré bleu est en haut à gauche. » (figure colorée + place)
- « Le carré vert est juste en dessous du cercle bleu. » (deux figures colorées + relation)
- « Le cercle vert n'est pas dans un coin. » (figure colorée + élimination)

C'est exactement l'usage des puzzles de logique classiques, et ça rend la déduction plus riche : chaque indice apporte deux contraintes.

## Vérifications de faisabilité avant de coder

Compté les grilles valides avant de générer : **72 grilles 3×3** et **6 912 grilles 4×4** satisfont l'orthogonalité. Le générateur énumère donc ces grilles (et non plus 144 / 331 776 paires quelconques), ce qui rend la recherche d'unicité rapide et exacte.

## Détails

- Nouveaux types d'indices : `case`, `ligne`, `colonne`, `voisin-gauche/droite/dessus/dessous`, `pas-coin`, `pas-bord` — tous référencent une figure colorée.
- Validateur : contrôle d'unicité des figures colorées + véracité des nouveaux indices.
- Interface : libellés accentués (« carré », « losange ») car les identifiants de contenu sont sans accent.
- 3 indices de secours par grille conservés (« Un indice »).

## Leçon

Un indice ambigu n'est pas un défaut de rédaction, c'est un défaut de **structure** du puzzle. Rendre les entités uniques (ici, les figures colorées) est ce qui autorise des phrases à deux informations. Corriger la cause plutôt que retirer l'indice.
