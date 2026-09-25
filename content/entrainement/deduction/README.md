# Module « Déduction » (logigramme 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif — la famille des *logigrammes*, appliquée à un **placement spatial**. Une grille N×N contient N figures et N couleurs, et chaque figure colorée (« carré bleu », « cercle rouge »…) apparaît une seule fois.

## Les règles, énoncées dans la consigne

Elles sont écrites noir sur blanc au début de chaque grille, parce qu'elles sont **nécessaires pour reconstruire le tableau** :

1. chaque ligne contient chaque figure une seule fois et chaque couleur une seule fois ;
2. chaque colonne aussi ;
3. donc chaque figure colorée n'apparaît qu'une seule fois dans la grille.

Sans ces trois règles, les dernières cases resteraient ambiguës : la personne ne pourrait pas terminer l'exercice. Elles sont rappelées avant chaque grille, pas seulement la première fois.

## Une phrase = deux informations qui se croisent

C'est le cœur du logigramme, et la correction principale du module : **aucune phrase ne donne un placement à recopier**.

| Forme | Exemple | Ce que ça oblige à faire |
|---|---|---|
| Deux contraintes sur la même figure | « Le carré vert est sur la ligne du bas, **mais** pas dans la colonne du milieu. » | croiser les deux informations pour situer la figure |
| Relation entre deux figures | « Le cercle bleu est juste en dessous du triangle rouge. » | reporter une certitude d'une figure sur l'autre |
| Comparaison faible | « Le losange jaune est plus à droite que le carré bleu. » | combiner avec les autres phrases pour trancher |
| Négation | « Le triangle bleu n'est ni dans un coin ni sur le bord. » | éliminer |
| Conditionnel | « Si le cercle vert est dans un coin, alors le cercle bleu est sur le bord. » | raisonner par cas |

La **méthode** enseignée dans la consigne est celle du logigramme : noter ce qui est **certain**, barrer ce qui devient **impossible**, puis **recouper** les phrases qui relient deux figures.

## Le tableau de déduction (brouillon cliquable)

Sous la grille, un tableau dépliable : **une ligne par figure colorée, une colonne par case**. Un clic marque une case ✗ (impossible) ou ✓ (certain). C'est le brouillon papier de l'orthophoniste, en version numérique : la mémoire de travail est externalisée, la personne n'a plus à « tenir » toutes les hypothèses de tête.

## Paliers

| Palier | Grille | Phrases |
|---|---|---|
| 1 | 3×3 | croisements ligne × colonne (aucun placement direct) |
| 2 | 3×3 | + relations entre figures (voisinage, à droite de, pas sur la même ligne) |
| 3 | 3×3 | + négations et conditionnel |
| 4 | 4×4 | 4 figures × 4 couleurs, phrases variées, **3 ancres de départ** |

**20 grilles par palier, soit 80 grilles** — et 3 phrases de secours par grille (bouton « Un indice »), qui n'apparaissent que si on les demande.

La grille 4×4 reçoit trois ancres (placement direct) : sans point de départ, elle ne se referme pas par déduction pure. Les paliers 1 à 3 n'en contiennent **aucune**.

## La garantie : le solveur est le juge

Un puzzle peut être unique et rester infaisable si sa reconstruction exige des hypothèses. Le thème ne laisse rien à l'intuition :

- un **solveur de déduction** (`tools/deduction_commun.py`) raisonne comme la personne : chaque case part avec toutes les figures colorées possibles, le moteur retire ce qui devient impossible (règles du jeu + chaque phrase), et recommence jusqu'à point fixe ;
- la génération est **constructive** : on part de la solution et on ajoute des phrases **jusqu'à ce que le solveur termine** — toutes les cases déterminées par propagation, sans aucune hypothèse ;
- un puzzle que le solveur ne résout pas n'est **jamais livré** : le générateur l'écarte, le validateur le refuse, et un test rejoue le solveur sur chaque grille du dépôt ;
- le validateur verrouille aussi la **pédagogie** : aucun placement direct au palier 1, minimum de phrases composées par palier.

## Stock long terme (3 mois)

- l'univers des solutions est **fini** : 72 grilles 3×3, 6 912 grilles 4×4 ;
- une même **solution** n'est jamais resservie dans le thème : toutes les grilles ont une solution différente ;
- à la cadence du programme (environ une séance de déduction par semaine), le stock couvre **plus de trois mois sans jamais revoir la même grille** ;
- pour prolonger : `--par-palier` au générateur (jusqu'à 24 en 3×3), ou l'ajout d'une cinquième figure et d'une cinquième couleur (univers 5×5) — changement à faire d'un seul tenant (consigne, interface, générateur, validateur).

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », « Un indice », validation, correction cases justes/fausses, et le tableau de déduction. La solution ne fuit jamais avant validation.

Un jeton déjà posé est **grisé et non sélectionnable** : il redevient disponible dès qu'on le retire de sa case (clic sur la case occupée, ou « Vider la grille »). Poser un jeton sur une case occupée remplace l'ancien et libère le premier. Après chaque pose, la sélection se vide — impossible de placer deux fois la même figure colorée.

## Génération

`tools/generer_deduction.py` — déterministe (graine fixe), piloté par le solveur de déduction, solutions uniques sur tout le thème :

    python3 tools/generer_deduction.py --par-palier 20

Relecture orthophoniste à faire.
