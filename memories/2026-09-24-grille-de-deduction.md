# 2026-09-24 — Grille de déduction 3×3 (figures × couleurs)

## Demande

Un exercice « qui ressemble au morpion mais avec 3 figures et 3 couleurs », avec 6 énoncés donnant des indices, à recouper pour reconstruire la solution.

## Ce qui a été livré

- **Thème « Déduction »** : grille 3×3, 3 figures (cercle, carré, triangle) × 3 couleurs (rouge, bleu, vert), contrainte de carré latin (chaque figure et chaque couleur une fois par ligne et par colonne), 6 indices structurés (pas du texte libre) à recouper. 12 grilles, 3 paliers (directs → ligne/colonne → négatifs).
- **Garantie d'unicité** : le générateur énumère les 12×12 carrés latins et ne retient que les ensembles de 6 indices qui déterminent une solution unique — sinon il échoue. Un puzzle ambigu serait cassé.
- **Interface** : palette de 9 jetons, placement par clic, « Vider la grille », validation, correction qui distingue cases justes et fausses.

## Difficultés rencontrées et leçons

- **Indices relationnels ambigus** : avec 3 occurrences de chaque figure, « le carré est sur la même ligne que le bleu » est ambigu (il y a 3 carrés). Retiré au profit d'indices « ligne / colonne » bien définis. Leçon : en logique, la sémantique de chaque type d'indice doit être vérifiée contre la structure de la grille, pas seulement codée.
- **Unicité vs difficulté** : retirer les indices relationnels a affaibli le pool au point que l'unicité n'était plus atteinte en 6 indices. Redressé en « glouton pour l'unicité + injection d'un indice de saveur vérifiée ».
- La progression de difficulté n'est pas dans « moins d'indices » mais dans le **type d'indices** (directs → relationnels → négatifs), l'unicité restant garantie.

## Reste à faire

- Passage visuel de l'interaction de placement dans le navigateur.
- Relecture orthophoniste.
- Éventuellement des grilles 4×4 pour les paliers supérieurs.
