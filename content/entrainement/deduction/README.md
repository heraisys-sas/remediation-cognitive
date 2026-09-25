# Module « Déduction » (logigramme 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif. Une grille N×N, N figures et N couleurs, et **une seule règle** : chaque figure colorée (« carré bleu », « cercle rouge »…) se pose une fois, dans une case, et une case ne contient qu'une figure.

Tout le reste doit venir des **phrases**. Aucune règle cachée, aucun tirage implicite : si une phrase n'est pas écrite, elle ne sert pas.

## Les phrases sont des chaînes

Une phrase part d'un **repère** sur une figure, puis **suit les relations** d'une figure à la suivante. Elle porte donc trois informations ou plus, ce qui **raccourcit l'exercice** — surtout au début :

> « Le carré rouge est sur la ligne du bas, **est juste à droite du cercle vert, qui est juste au-dessus du cercle rouge**. »

Trois informations, trois figures situées les unes par rapport aux autres : la résolution se fait en suivant la chaîne, puis en croisant les chaînes entre elles (la même figure apparaît dans plusieurs phrases).

## Paliers

| Palier | Grille | Phrases |
|---|---|---|
| 1 | 3×3 | chaînes longues : un repère sûr, puis deux relations de voisinage |
| 2 | 3×3 | repères sûrs et relations variées (voisinage, à droite de, plus haut que) |
| 3 | 3×3 | repères **négatifs** (« n'est pas dans un coin ») et relations lâches : éliminer pour déduire |
| 4 | 4×4 | 4 figures × 4 couleurs |

**20 grilles par palier, soit 80 grilles**, et 3 phrases de secours par grille (bouton « Un indice »), qui n'apparaissent que si on les demande.

Dosage mesuré : **4 phrases** au palier 1 (12 informations), 8 aux paliers 2 et 3 (16 informations), 15 en 4×4 (30 informations).

## La garantie : le solveur est le juge

`tools/deduction_commun.py` raisonne comme la personne, **avec la seule règle énoncée** :

- chaque case part avec toutes les figures colorées possibles ;
- chaque phrase retire ce qui devient impossible (positions, relations entre figures) ;
- une case déterminée fixe sa figure ; une figure qui n'a plus qu'une case possible s'y place ;
- le moteur recommence jusqu'à ce que plus rien ne bouge.

Si toutes les cases sont déterminées, la grille est **déductible des seules phrases** — sans hypothèse, sans règle ajoutée. La génération est constructive : on ajoute les phrases qui **déterminent le plus de cases**, jusqu'à ce que le solveur termine.

Le contrôle est triple : à la génération, au dépôt (le validateur refuse une grille non déductible ou une phrase à une seule information), et par un test rejoué sur chaque grille du dépôt.

## Stock long terme

- l'univers des placements est **immense** : 9! = 362 880 placements en 3×3, plus de 2×10¹³ en 4×4 ;
- une même **solution** n'est jamais resservie dans le thème ;
- à la cadence du programme (environ une séance de déduction par semaine), le stock couvre **plus de trois mois sans jamais revoir la même grille** ;
- pour prolonger : `--par-palier` au générateur, ou une cinquième figure et une cinquième couleur.

## Tableau de déduction (brouillon cliquable)

Sous la grille, un tableau dépliable : **une ligne par figure colorée, une colonne par case**. Un clic marque une case ✗ (impossible) ou ✓ (certain) : c'est le brouillon papier du logigramme, en version numérique — la mémoire de travail est externalisée.

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », « Un indice », validation, correction cases justes/fausses, tableau de déduction. Un jeton déjà posé est **grisé et non sélectionnable** ; il redevient disponible dès qu'on le retire de sa case. La solution ne fuit jamais avant validation.

## Génération

    python3 tools/generer_deduction.py --par-palier 20

Déterministe (graine fixe), piloté par le solveur, placements tous distincts. Relecture orthophoniste à faire.
