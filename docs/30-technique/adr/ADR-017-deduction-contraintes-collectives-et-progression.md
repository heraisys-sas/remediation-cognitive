# ADR-017 — Déduction : indices collectifs explicites et progression

Date : 2026-09-29 — branche d'essai `amelioration-deduction-20260927`.

## Contexte

Le matériel papier fourni par Olivier combine exclusions par couleur, répartition d'une forme, entre-deux avec références partielles, chaînes et opposition. Le corpus informatique reposait surtout sur des chaînes binaires, parfois redondantes. La distribution des formes par ligne est un **indice de la grille**, jamais une règle générale. Olivier demande quatre paliers 3×3 puis un cinquième 4×4 et autorise l'implémentation directe après les échecs AutoClaw.

## Décision

Trois types structurés autonomes : `compte-categorie`, `diversite`, `entre`. Leurs paramètres et le texte réellement affiché portent toutes les restrictions. Une référence partielle désigne un des pions existants ; l'entre-deux est existentiel sur deux pions distincts, alignés, pas nécessairement voisins ni équidistants. Une diagonale désigne une droite à 45°. Une répartition `numero=chaque` doit être compatible avec l'effectif total de la catégorie.

La propagation utilise consistance d'arc, cardinalités explicites, supports des triples et unicité des cases/pions. Elle ne fait pas de branchement. Aucun carré latin n'est présupposé. L'unicité est contre-vérifiée par une recherche MRV séparée, avec budget et arrêt explicite en cas de dépassement. Cette recherche n'est pas présentée comme la méthode de résolution attendue de la personne.

Les phrases peuvent avoir une seule information. Le générateur retire toute information dispensable pour sa preuve par propagation ; il vérifie la présence utile des familles requises. Les paliers 2–5 conservent le contrôle exact des phrases fixant seules une position. L'entre-deux diagonal 3×3 est donc écarté (centre connu par cette seule phrase), celui du 4×4 est utilisé.

100 grilles : 20 par palier, chacune classée dans une des trois étapes. P1 réduit les chaînes guidées ; P2 retire les repères positifs ; P3 introduit les références partielles puis retire l'adjacence immédiate ; P4/P5 retirent les repères individuels de ligne/colonne en dernière étape. La nouveauté suivante ne peut pas être indéfiniment masquée par les révisions faciles. Au plus la moitié des places leur est réservée en présence de nouveautés ; les révisions avancées passent d'abord.

Pour les contenus comportant des étapes, seules les séances où un item de l'étape finale a reçu une réponse alimentent l'historique de maîtrise. Le critère existant (trois séances à 90 %) et le non-recul du palier sont conservés. Les anciens taux sont conservés ; un champ local `historique_etapes` suit séparément les séances éligibles afin qu'un ancien taux parfait ne valide pas les nouvelles étapes. L'historique de maîtrise des autres thèmes n'est pas modifié. Aucun changement du format externe des endpoints ; champ de contenu additionnel `etape_progression`.

## Conséquences et limites

Le corpus est remplacé sous de nouveaux identifiants calculés depuis le contenu ; les anciennes cartes FSRS restent sans réaffectation. Le palier courant conservé n'est pas une mesure clinique : un ancien utilisateur de P4 obtient désormais du 3×3 avancé, et peut choisir P5 manuellement. Le générateur isole ses graines par palier pour éviter les cascades aléatoires lors d'un enrichissement d'un autre palier.

Les indicateurs (types, absence de raccourci, support propagé, informations nécessaires) décrivent la structure logique, pas une difficulté étalonnée, un minimum de raisonnement humain ou une efficacité après traumatisme crânien. Le matériel papier inspire les familles d'indices ; il n'est ni reproduit ni déclaré cliniquement équivalent. Relecture du nouveau contenu : `a_revoir`.
