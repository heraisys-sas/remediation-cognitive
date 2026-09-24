# Module « Déduction » (grilles logiques 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif — la famille des *logic grids* classiques, ici appliquée à un **placement spatial**. Une grille N×N contient N figures et N couleurs, et **chaque figure colorée** (« carré bleu », « cercle rouge »…) apparaît **une seule fois**.

Cette unicité n'est pas un détail : c'est ce qui rend chaque phrase **non ambiguë** et permet des indices à **deux informations** (« le carré vert est juste en dessous du cercle bleu »).

## Taxonomie des indices (les catégories classiques)

| Catégorie | Types | Exemple |
|---|---|---|
| Direct (vrai/faux) | `case` | « Le carré bleu est en haut à gauche. » |
| Position dans une ligne/colonne | `ligne`, `colonne` | « Le cercle rouge est dans la colonne de gauche. » |
| Relationnel | `voisin-gauche/droite/dessus/dessous`, `comparaison`, `autre-ligne`, `autre-colonne` | « Le carré vert est juste en dessous du cercle bleu. » |
| Négatif (élimination) | `pas-coin`, `pas-bord`, `ni-ni` | « Le cercle bleu n'est ni dans un coin ni sur le bord. » |
| Conditionnel | `si-alors` | « Si le cercle vert est dans un coin, alors le cercle bleu est sur le bord. » |

**Aucun indice redondant ni trivial** : chaque phrase lève une ambiguïté réelle (le générateur ne complète pas avec des phrases décoratives). Le nombre d'indices varie donc de 4 à 9 selon la grille — c'est voulu. La règle générale est rappelée dans la **consigne**, pas répétée comme un indice.

## La méthode enseignée

La consigne porte la stratégie de résolution, la même qu'en logigramme :

1. noter ce qui est **certain** ;
2. barrer ce qui devient **impossible** ;
3. **recouper** les indices qui relient deux figures colorées.

## Paliers

| Palier | Grille | Indices |
|---|---|---|
| 1 | 3×3 | position (case, ligne, colonne) |
| 2 | 3×3 | + relationnels (voisinage, à gauche de, pas sur la même ligne) |
| 3 | 3×3 | + négatifs et conditionnels (`si-alors`) |
| 4 | 4×4 | 4 figures × 4 couleurs, taxonomie complète |

4 grilles par palier, soit **16 grilles**, et 3 indices de secours par grille (bouton « Un indice »).

## Garanties vérifiées

- la solution est un couple de carrés latins **orthogonaux** : chaque figure colorée exactement une fois ;
- chaque indice est **vrai** pour la solution ;
- les indices déterminent la solution de façon **unique** — et le solveur vérifie que la solution survivante est bien celle visée.

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », « Un indice », validation, correction cases justes/fausses. La solution ne fuit jamais avant validation.

## Génération

`tools/generer_deduction.py` — déterministe, solveur d'unicité intégré. Relecture orthophoniste à faire.
