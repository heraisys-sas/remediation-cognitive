# Module « Déduction » (grilles logiques 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif visuel. Une grille N×N contient N figures et N couleurs, chaque figure et chaque couleur apparaissant **une fois par ligne et une fois par colonne** (carré latin). Des indices, à **recouper**, guident le placement — aucun ne suffit seul, il faut souvent éliminer pour déduire.

Sollicite le raisonnement logique, la mémoire de travail (tenir les indices en tête pendant qu'on place) et les fonctions exécutives.

## Paliers

| Palier | Grille | Indices | Mécanisme |
|---|---|---|---|
| 1 | 3×3 | 6 | directs (« la case X est … ») + règle |
| 2 | 3×3 | 6 | directs + indices de ligne / colonne |
| 3 | 3×3 | 6 | indices **négatifs** (« n'est pas… ») : éliminer |
| 4 | 4×4 | 12 | 4 figures × 4 couleurs, plus d'indices à recouper |

4 grilles par palier, soit **16 grilles**. Les types d'indices incluent aussi « dans un coin » et « sur le bord » (utilisés quand ils apportent de l'information).

## Garanties

- Chaque indice est **vrai** pour la solution (contrôle du validateur) ;
- les indices déterminent la solution de façon **unique** (le générateur embarque un solveur par dimension et échoue s'il y a ambiguïté) ;
- chaque grille porte **3 indices de secours** (`contenu.indices`), révélés un par un par le bouton « Un indice » — de l'aide progressive, pas une punition.

## Interaction

Palette de jetons (figure × couleur), placement par clic, bouton « Vider la grille », « Un indice » pour l'aide de secours, validation, correction qui distingue cases justes et fausses. La solution ne fuit jamais avant validation.

## Génération

`tools/generer_deduction.py` — déterministe, avec solveur de vérification de l'unicité intégré (par dimension, ce qui rend la 4×4 rapide). Relecture orthophoniste à faire.
