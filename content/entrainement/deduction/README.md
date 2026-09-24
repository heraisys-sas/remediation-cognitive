# Module « Déduction » (grilles logiques 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif visuel. Une grille N×N contient N figures et N couleurs, et **chaque figure colorée** (« carré bleu », « cercle rouge »…) apparaît **une seule fois** dans la grille. Cette unicité est ce qui rend les indices **non ambigus** : « le carré vert est juste en dessous du cercle bleu » désigne une seule case possible.

## Les indices portent deux informations

Chaque phrase nomme une figure colorée **et** indique soit sa place, soit sa relation à une autre figure colorée :

| Type d'indice | Exemple |
|---|---|
| `case` | « Le carré bleu est en haut à gauche. » |
| `ligne` / `colonne` | « Le cercle rouge est dans la colonne de gauche. » |
| `voisin-*` | « Le carré vert est juste en dessous du cercle bleu. » |
| `pas-coin` / `pas-bord` | « Le cercle vert n'est pas dans un coin. » |
| `regle` | « Chaque figure colorée apparaît une seule fois dans la grille. » |

Aucun indice ne suffit seul : il faut les **recouper** (et souvent éliminer) pour reconstituer toute la grille.

## Paliers

| Palier | Grille | Mécanisme |
|---|---|---|
| 1 | 3×3 | indices de position |
| 2 | 3×3 | + indices de ligne et de colonne |
| 3 | 3×3 | + indices de voisinage et négatifs |
| 4 | 4×4 | 4 figures × 4 couleurs, davantage d'indices |

4 grilles par palier, soit **16 grilles**, et 3 indices de secours par grille (bouton « Un indice »).

## Garanties

- La solution est un couple de carrés latins **orthogonaux** : chaque figure colorée exactement une fois ;
- chaque indice est **vrai** pour la solution (contrôle du validateur) ;
- les indices déterminent la solution de façon **unique** (le générateur embarque un solveur et échoue s'il y a ambiguïté).

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », bouton « Un indice » (aide progressive), validation, correction qui distingue les cases justes et fausses. La solution ne fuit jamais avant validation.

## Génération

`tools/generer_deduction.py` — déterministe, avec solveur d'unicité intégré. Relecture orthophoniste à faire.
