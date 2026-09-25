# Module « Déduction » (grilles logiques 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif — la famille des *logic grids* classiques, ici appliquée à un **placement spatial**. Une grille N×N contient N figures et N couleurs, et **chaque figure colorée** (« carré bleu », « cercle rouge »…) apparaît **une seule fois**.

Cette unicité n'est pas un détail : c'est ce qui rend chaque phrase **non ambiguë** et permet des indices à **deux informations** (« le carré vert est juste en dessous du cercle bleu »).

## La garantie qui compte : résoluble par déduction, jamais à deviner

Un puzzle peut être *techniquement* unique et rester infaisable si sa reconstruction exige des hypothèses. Le thème ne laisse rien à l'intuition :

- un **solveur de déduction** (`tools/deduction_commun.py`) raisonne comme la personne : chaque case part avec toutes les figures colorées possibles, le moteur retire ce qui devient impossible (règles du jeu + chaque indice), et recommence jusqu'à point fixe ;
- la génération est **constructive** : on part de la solution et on **ajoute les indices un par un, jusqu'à ce que le solveur termine** — toutes les cases déterminées par propagation, sans aucune hypothèse ;
- un puzzle que le solveur ne résout pas n'est **jamais livré** : le générateur l'écarte, le validateur le refuse, et un test rejoue le solveur sur chaque grille du dépôt.

C'est la réponse à la question « assez de phrases pour reconstruire la grille ? » — la question n'est plus jugée à l'instinct : **le solveur est le juge**.

## Taxonomie des indices (les catégories classiques)

| Catégorie | Types | Exemple |
|---|---|---|
| Direct (vrai/faux) | `case` | « Le carré bleu est en haut à gauche. » |
| Position dans une ligne/colonne | `ligne`, `colonne` | « Le cercle rouge est dans la colonne de gauche. » |
| Relationnel | `voisin-gauche/droite/dessus/dessous`, `comparaison`, `autre-ligne`, `autre-colonne` | « Le carré vert est juste en dessous du cercle bleu. » |
| Négatif (élimination) | `pas-coin`, `pas-bord`, `ni-ni` | « Le cercle bleu n'est ni dans un coin ni sur le bord. » |
| Conditionnel | `si-alors` | « Si le cercle vert est dans un coin, alors le cercle bleu est sur le bord. » |

**Aucun indice redondant ni trivial** : chaque phrase lève une ambiguïté réelle (le générateur ne complète pas avec des phrases décoratives). Le nombre d'indices varie de **5 à 7 pour les grilles 3×3** et de **11 à 14 pour les 4×4** — c'est ce que la déductibilité exige, pas un chiffre arbitraire. La règle générale est rappelée dans la **consigne**, pas répétée comme un indice.

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

**20 grilles par palier, soit 80 grilles** (auparavant 16), et 3 indices de secours par grille (bouton « Un indice »).

## Stock long terme (3 mois)

- l'univers des solutions est **fini** : 72 grilles 3×3, 6 912 grilles 4×4 ;
- une même **solution** n'est jamais resservie dans tout le thème : 60 des 72 solutions 3×3 sont utilisées, 20 des 6 912 solutions 4×4 ;
- à la cadence du programme (environ **une séance de déduction par semaine**, 1 à 2 grilles par séance), le stock couvre **plus de trois mois sans jamais revoir la même grille** ;
- pour prolonger au-delà : le générateur accepte `--par-palier` (jusqu'à 24 par palier en 3×3, l'univers restant), et l'ajout d'une **5ᵉ figure / 5ᵉ couleur** ouvrirait un univers 5×5 bien plus grand — changement à faire d'un seul tenant (consigne, interface, générateur, validateur).

## Garanties vérifiées

- la solution est un couple de carrés latins **orthogonaux** : chaque figure colorée exactement une fois ;
- chaque indice est **vrai** pour la solution ;
- les indices déterminent la solution de façon **unique** ;
- **la grille se reconstruit entièrement par déduction** (propagation, aucune hypothèse) — contrôlé à la génération, au moment du dépôt, et par un test rejoué sur chaque grille.

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », « Un indice », validation, correction cases justes/fausses. La solution ne fuit jamais avant validation.

## Génération

`tools/generer_deduction.py` — déterministe (graine fixe), piloté par le solveur de déduction, unicité des solutions sur tout le thème. Relecture orthophoniste à faire.
