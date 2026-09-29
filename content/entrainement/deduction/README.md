# Module « Déduction » (logigramme 3×3 et 4×4 — hors MDR)

**Principe** : un puzzle de raisonnement déductif. Une grille N×N, N figures et N couleurs, et **une seule règle** : chaque figure colorée (« carré bleu », « cercle rouge »…) se pose une fois, dans une case, et une case ne contient qu'une figure.

Tout le reste doit venir des **phrases**. Aucune règle cachée : si une phrase n'est pas écrite, elle ne sert pas.

## Les phrases sont des chaînes

Une phrase part d'un **repère** sur une figure, puis **suit les relations** d'une figure à la suivante. Elle porte deux ou trois informations, ce qui **raccourcit l'exercice** — surtout au début ; quand deux chaînes portent chacune deux informations, c'est leur croisement qui tranche :

> « Le carré rouge est sur la ligne du bas, **est juste à droite du cercle vert, qui est juste au-dessus du cercle rouge**. »

## Le vocabulaire

| Famille | Formes | Exemple |
|---|---|---|
| Repères | `ligne`, `colonne`, `coin` | « Le cercle vert est dans un coin. » |
| Diagonales | `diagonale` (descendante), `diagonale-inverse` (montante) | « Le triangle rouge est sur la diagonale descendante. » |
| Voisinage | juste à gauche / à droite / au-dessus / en dessous, `voisin-diagonale` | « … touche le cercle rouge en diagonale. » |
| Opposé | `oppose` | « Le losange jaune est à l'opposé du cercle rouge, de l'autre côté du centre. » |
| Comparaisons | `comparaison`, plus à droite / à gauche / plus haut / plus bas | « Le triangle bleu est plus haut que le carré rouge. » |
| Éliminations | `pas-ligne`, `pas-colonne`, `pas-coin`, `pas-bord`, `ni-ni`, `pas-diagonale`, `pas-diagonale-inverse`, `autre-ligne`, `autre-colonne` | « Le carré bleu n'est ni dans un coin ni sur le bord. » |

« À l'opposé de » désigne la case **symétrique par rapport au centre** (en 3×3 : haut gauche ↔ bas droite).

## Paliers

| Palier | Grille | Phrases |
|---|---|---|
| 1 | 3×3 | chaînes longues : un repère (ligne, colonne ou coin), puis deux relations de voisinage |
| 2 | 3×3 | repères négatifs et éliminations (« pas sur la colonne », « pas juste à gauche de ») : déduire par ce qui est exclu |
| 3 | 3×3 | relations relatives (« plus à droite que », « à l'opposé de ») : aucune phrase ne suffit seule, c'est le croisement qui tranche |
| 4 | 4×4 | tout le vocabulaire, chaînes courtes, nombreuses phrases |

**20 grilles par palier, soit 80 grilles**, et 3 phrases de secours par grille (bouton « Un indice »), qui n'apparaissent que si on les demande.

Dosage (moyennes mesurées) : **4 phrases** au palier 1 et au palier 3, **11** au palier 2, **15 à 16** en 4×4. L'ordre de présentation des phrases est **tiré au sort** à chaque grille — il ne porte aucune information.

**Séance** : **six grilles** au maximum — chaque grille demande une chaîne de raisonnement complète, douze ne tiendraient pas dans une séance courte. Au bout de **dix minutes**, la séance ne se ferme pas d'elle-même : elle **propose** de s'arrêter (« tu peux t'arrêter là ou continuer — c'est toi qui vois »). Le vocabulaire demandé (diagonales, coins, « à l'opposé ») est garanti présent dans chaque palier concerné.

## Aucune phrase redondante

Une phrase que l'on peut retirer **sans perdre la solution** est supprimée automatiquement : inutile de situer une figure déjà située par les autres phrases. Les phrases qui portent le vocabulaire demandé sont protégées de ce nettoyage. Le nettoyage a ses limites assumées : le plancher de quatre phrases et la protection du vocabulaire retiennent parfois une phrase de plus — elle reste visible dans la mesure publiée (`tools/mesurer_difficulte.py`). Dernière passe (29/09/2026) : les 13 grilles du palier 3 qui contenaient une phrase **fixant seule** une position ont été scindées en deux chaînes de deux informations (mêmes solutions ; identifiants `df-3-XX` → `dc-3-XX`).

## La garantie : le solveur est le juge

`tools/deduction_commun.py` raisonne comme la personne, **avec la seule règle énoncée** : chaque case part avec toutes les figures colorées possibles, chaque phrase retire ce qui devient impossible, une case déterminée fixe sa figure, une figure qui n'a plus qu'une case possible s'y place, et l'on recommence jusqu'à ce que rien ne bouge.

Génération constructive : on ajoute les phrases qui **déterminent le plus de cases**, jusqu'à ce que le solveur termine. Contrôle triple : à la génération, au dépôt, et par un test rejoué sur chaque grille du dépôt.

**Le « fixe seule » est prouvé exactement.** Aux paliers 2 à 4, aucune phrase ne fixe une position à elle seule (placement direct déguisé) : on énumère **tous** les placements injectifs compatibles avec les seules figures citées par la phrase — cache et budget bornés, erreur explicite si dépassé, jamais de faux « zéro solo ». Les indicateurs publics restent structurels : le **rang de lecture** suit l'ordre affiché (ce n'est pas un minimum logique) et le **support propagé** est une borne supérieure — aucune calibration clinique n'est revendiquée.

Deux contrôles indépendants du solveur :

- le **sens des phrases** est relu selon le français (« juste au-dessus » = une ligne en moins) : une paire dessus/dessous inversée a déjà rendu des grilles insolubles, ce contrôle l'aurait dit ;
- l'**interface** doit écrire chaque type de relation comme il s'annonce (`voisin-dessus` ne peut pas produire « en dessous »).

## Stock long terme

- l'univers des placements est **immense** : 9! = 362 880 en 3×3, plus de 2×10¹³ en 4×4 ;
- une même **solution** n'est jamais resservie dans le thème ;
- à la cadence du programme (environ une séance par semaine), le stock couvre **plus de trois mois sans revoir la même grille**.

## Tableau de déduction (brouillon cliquable)

Sous la grille, un tableau dépliable : **une ligne par figure colorée, une colonne par case**. Un clic marque une case ✗ (impossible) ou ✓ (certain) — le brouillon papier du logigramme, en version numérique.

## Interaction

Palette de jetons (figure × couleur), placement par clic, « Vider la grille », « Un indice », validation, correction cases justes/fausses, tableau de déduction. Un jeton déjà posé est **grisé et non sélectionnable** ; il redevient disponible dès qu'on le retire. La solution ne fuit jamais avant validation.

## Génération

    python3 tools/generer_deduction.py --par-palier 20

Déterministe (graine fixe), piloté par le solveur, placements tous distincts. Les identifiants sont **dérivés du contenu** (empreinte du contenu pédagogique) : une re-génération identique garde les mêmes identifiants, tout contenu modifié en reçoit de nouveaux — impossible de réutiliser l'identifiant d'un contenu déjà livré. Relecture orthophoniste à faire.
