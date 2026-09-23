# Module « Déduction » (grille logique 3×3 — hors MDR)

**Principe** : un puzzle de raisonnement déductif visuel. Une grille 3×3 doit contenir les **trois figures** (cercle ●, carré ■, triangle ▲) et les **trois couleurs** (rouge, bleu, vert) — chaque figure et chaque couleur apparaissant **une fois par ligne et une fois par colonne** (carré latin). **Six indices** permettent de reconstruire la solution ; ils doivent être **recoupés** (aucun ne suffit seul, et il faut souvent éliminer pour déduire).

Sollicite le raisonnement logique, la mémoire de travail (tenir six contraintes en tête pendant qu'on place) et les fonctions exécutives.

## Garanties

- Chaque indice est **vrai** pour la solution (contrôle du validateur) ;
- les six indices déterminent la solution de façon **unique** (le générateur embarque un solveur et échoue s'il y a ambiguïté — un puzzle ambigu serait cassé).

## Paliers

| Palier | Indices | Mécanisme |
|---|---|---|
| 1 | directs (la case X est …) + règle | apprendre le mécanisme |
| 2 | directs + indices de ligne / colonne | recouper deux contraintes |
| 3 | directs + indices **négatifs** (« n'est pas… ») | éliminer pour déduire |

4 grilles par palier, soit **12 grilles**.

## Interaction

L'utilisateur choisit un jeton dans la palette (figure × couleur), le place sur la grille, puis valide. La correction compare la grille complète à la solution et affiche les cases justes et fausses.

## Génération

`tools/generer_deduction.py` — déterministe, avec solveur de vérification de l'unicité intégré. Relecture orthophoniste à faire.
