# 2026-09-24 — Déduction : méthode des logic grids (recherche + correctifs)

## La demande

« Renseigne-toi sur cet exercice et cette méthode pour bien l'implémenter. »

## Ce que dit la documentation

Deux principes reviennent dans les guides de construction de puzzles de logique :

1. **Chaque combinaison est unique** (« each combination should be unique ») — c'est la règle que l'utilisateur avait identifiée, et c'est elle qui rend les phrases non ambiguës.
2. **Aucune référence n'est répétée inutilement** dans un indice — pas d'indice décoratif, chaque phrase doit apporter une contrainte.

Et la taxonomie classique des indices : *true/false* (direct), *multi-elimination*, *neither/nor*, *either/or*, *greater/lesser*.

## Ce que ça a changé dans le code

- **Taxonomie complète implémentée** : `case` (direct), `ligne`/`colonne`, `voisin-gauche/droite/dessus/dessous` (voisinage), `comparaison` (à gauche de, même ligne), `autre-ligne`/`autre-colonne` (pas la même ligne/colonne), `pas-coin`, `pas-bord`, `ni-ni` (élimination), `si-alors` (**conditionnel**). Tous à deux informations.
- **Plus aucun indice décoratif** : mon générateur complétait jusqu'ici avec des « règles » répétées pour atteindre 6 indices — exactement le défaut que la documentation proscrit. Les indices sont maintenant **nécessaires** (4 à 9 selon la grille), et la règle générale est passée dans la **consigne**.
- **Méthode de résolution enseignée explicitement** : noter les certitudes → barrer les impossibilités → recouper les indices reliant deux figures. C'est la stratégie des logigrammes, et elle est écrite dans la consigne (cohérent avec le fil « méthodes » du logiciel).

## Bug attrapé au passage (et pourquoi il compte)

Les indices `voisin-gauche` et `voisin-droite` étaient **inversés** : la construction les créait avec une sémantique et le test les évaluait avec la sémantique opposée. Pire : le solveur acceptait un ensemble d'indices dès qu'il ne restait **qu'une seule** solution possible, **sans vérifier que c'était la bonne** — un indice faux pour la solution visée pouvait donc être retenu, et le puzzle stocké devenir incohérent.

Corrigé deux fois : la sémantique des voisinages est cohérente, et le solveur vérifie désormais que la solution survivante **est bien celle visée**. C'est le genre de garde-fou qui évite un puzzle insoluble livré à l'utilisateur.

## Reste à faire

- Passage visuel (grille, indices conditionnels, bouton « Un indice »).
- Relecture orthophoniste.
- Piste : une **grille de possibilités** (marquer les cases encore possibles) comme aide de résolution, à l'image du tableau qu'on utilise sur papier.


## 2026-09-25 — déductibilité garantie + stock 3 mois

Suite au retour « pas assez de phrases pour reconstruire la grille » :

- la **déductibilité** (résoluble par propagation, sans hypothèse) remplace la simple unicité comme critère de livraison. Solveur : `tools/deduction_commun.py` (domaines par case + règles + AC sur les indices binaires). Génération constructive : on ajoute des indices jusqu'à ce que le solveur termine ; le validateur refuse un puzzle non déductible ; un test rejoue le solveur sur tout le thème.
- stock étendu 16 → **80 grilles** (20/palier), **solutions toutes distinctes** (60/72 de l'univers 3×3, 20/6912 en 4×4). Le générateur prend `--par-palier` et échoue proprement si l'univers est épuisé.
- le solveur est *sound* mais incomplet : un `False` invite à ajouter des indices (prudent), un `True` prouve la déductibilité. C'est la marge de sécurité voulue.
- leçon : l'**unicité** ne suffit pas pour l'entraînement — un puzzle unique peut exiger des hypothèses (essayage) et devenir infaisable en rééducation. Toujours valider par un solveur qui raisonne comme la personne.
