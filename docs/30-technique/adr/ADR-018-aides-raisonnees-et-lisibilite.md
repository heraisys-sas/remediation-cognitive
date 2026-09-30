# ADR-018 — Aides raisonnées et lisibilité de P2

Date : 2026-09-30. Demande d’Olivier : aides progressives, entrée moins abrupte, regroupements avec « et » pour un seul pion ; appliquer les aides communes aux autres paliers sans uniformiser leurs spécificités.

## Décision

`tools/deduction_accompagnement.py` transforme de façon déterministe le contenu généré, avant calcul de l’identifiant. Pour P2, décomposer les chaînes puis regrouper deux contraintes unaires du même pion, uniquement si la phrase composée ne fixe aucune case seule. La sélection gloutonne des informations réduit la charge de lecture : 6–8 phrases, moyenne 7,25. Les comparaisons relatives négatives de l’ancienne étape 3 sont remplacées par des exclusions et voisinages simples ; cette étape n’a plus de repères individuels. Les sept grilles intermédiaires comportent chacune un regroupement réel.

Un repère visible peut être ajouté à l’entrée de P2 s’il permet, avec une autre phrase, un premier placement certain. Le champ `repere_accompagnement` identifie sa position dans la liste. Le noyau sans ce repère reste résoluble et ses informations restent nécessaires à sa preuve par propagation. La redondance est ici volontaire et pédagogique, pas une erreur de contenu.

Pour les cinq paliers, remplacer les coordonnées de secours par `aide_raisonnement`. Étape 1 : attirer l’attention sur des phrases et un pion. Étape 2 : noter les possibilités sans annoncer une position certaine. Étape 3, sur un nouveau clic explicite : montrer l’intersection ou la démonstration des éliminations qui aboutit au placement. Les phrases sont numérotées dans l’interface. Le bouton conserve un repli pour les anciens items en mémoire.

Le mode intersection compare les domaines obtenus par chaque phrase séparément. Le mode croisement applique successivement chaque phrase aux possibilités déjà établies, avec l’unicité des pions/cases ; il conserve toutes les réductions nécessaires pour expliquer le chemin suivi. Le validateur rejoue chaque étape et contrôle la conclusion. Il n’y a aucun ajout caché d’information depuis la réponse.

## Conséquences

Les 100 identifiants changent puisque les aides changent. P1/P3/P4/P5 conservent leurs solutions et énoncés ; la conception de leur difficulté n’est pas revue dans cette passe. P2 est régénéré. La résolution et l’unicité sont vérifiées sans les aides ; le repère pédagogique reste un énoncé visible. Les démonstrations complexes peuvent être longues au P5 ; leur adaptation pédagogique spécifique reste à examiner en usage, sans calibration clinique revendiquée.
