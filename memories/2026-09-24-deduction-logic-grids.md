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
