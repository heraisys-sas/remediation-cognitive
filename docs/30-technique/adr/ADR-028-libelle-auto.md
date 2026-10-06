# ADR-028 — Distinguer départ initial et progression Auto

## Contexte

« Auto — départ 2 » pouvait être pris pour le niveau actuel d'une progression
existante. Le niveau de première séance de Calcul mental n'était pas exposé.

## Décision

GET /api/entrainement/themes ajoute `palier_depart` à chaque thème, issu de la
même configuration que le démarrage effectif. Pour un parcours, sa définition
prime (défaut 1). L'interface affiche « Auto — suivre ma progression » et explique
séparément le départ initial. Un parcours à palier unique est identifié comme tel.

## Conséquences

Le niveau actuel n'est pas prétendu connu côté navigateur. La progression réelle,
les historiques et les parcours sélectionnés ne changent pas. Champ API additif.
