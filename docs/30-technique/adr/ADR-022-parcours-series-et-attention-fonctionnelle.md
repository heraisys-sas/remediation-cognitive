# ADR-022 — Parcours de séries et tâches fonctionnelles

Date : 2026-10-01. Mise en œuvre autorisée après fusion de l’état antérieur dans main (`8a75404`).

## Contexte

POC de laboratoire, adultes de niveau intellectuel antérieur élevé, en complément de séances accompagnées. Les noms précédents confondaient entraînement et évaluation. Les familles de « Concentration » étaient essentiellement numériques. Une liste auditive n'est pas un palier plus difficile d'une liste lue. Le projet de profilage diagnostique lexical est écarté.

## Décision

- L’accueil parle d’**exercices ciblés**. Catégorie API `cible`, quota de pratique de trois séances par jour, dérogation conservée. Aucun thème actuel n’est présenté comme une mesure standardisée. Le code de catégorie historique `evaluation` est conservé pour compatibilité, sans thème associé.
- Une carte « Mémoriser des séries », deux parcours : `rappel-series` (lu) et `series-entendues` (entendu). Identifiants, cartes FSRS, maîtrise et compteurs distincts. L'historique visuel reste dans son dossier ; nouvelles cartes `rs2-*` pour le rythme modifié. Listes auditives distinctes `rse1-*`, charges équivalentes mais pas de calibration psychométrique entre modalités.
- Lu : **2 s visible + 2 s blanc** ; frontière de série : **3 s** ; pause de 2 s après le dernier mot. Entendu : fichiers préparés avec la voix française du système (Thomas), 48 mots mutualisés en AAC mono 32 kbit/s, aucun mot écrit, pause de 2 s **après la fin du fichier**, 3 s entre séries. Les chemins versionnés bénéficient du cache navigateur immuable ; les scripts restent sans cache. La synthèse des consignes est conservée. Pas de simultané audio/visuel. Arrêt des callbacks et de la voix à la clôture/changement d’item. Échec vocal explicite, possibilité de recommencer ; aucune bascule visuelle silencieuse. Ce réglage n’est pas une norme clinique ; les durées auditives correspondent aux fichiers préparés. Le moteur Web Speech du navigateur intégré ne signalait pas sa fin lors de l’essai réel ; les fichiers audio évitent cette dépendance.
- Séances de séries limitées à quatre items pour tenir compte du ralentissement. Les deux portées du palier 4 sont intercalées, afin qu’une séance courte rencontre chacune.
- **Actualiser une consigne** : production libre structurée après messages successivement masqués, lecture au rythme choisi ; 2 éléments/1 changement, puis 3 éléments/2 changements, puis corrections successives et distracteur. La correction ne juge pas la vitesse.
- **Comparer deux documents** : documents consultables, jugement par champ conforme/écart ; 2, 4 puis 6 points, ordre modifié, valeurs proches et cas entièrement conformes.
- **Repérer l’essentiel** : but et critères visibles, messages successifs au rythme choisi, sélection/non-sélection ; critères de plus en plus larges, distracteurs proches. Omissions et sélections inutiles séparées dans le retour.
- Chaque nouveau thème comprend 12 situations, 4 par palier. Nouveaux types et réponses objet réutilisant les séances et le stockage existants. Retour API additionnel `detail_fonctionnel` (lignes corrigées et explications ; pour le filtrage, omissions/fausses sélections). Aucune réponse ni explication corrective avant soumission.
- Après examen de leur valeur ajoutée, l’utilisateur demande le retrait complet de « Calculs en chaîne et suites » : contenu, compatibilité API et historique local supprimés. Aucune fusion ni modification de Calcul mental, aucun exercice de remplacement.
- Descriptions corrigées : mémoire, mots/contexte, Garder le cap. Le discriminant technique SFA/PCA ne doit plus être affiché comme méthode. « N-back » et « double tâche » ne décrivent pas fidèlement les tâches historiques : descriptions de famille reformulées, types techniques conservés.
- Programme de huit semaines synchronisé : cinq paliers de déduction et nouveaux thèmes. Aucun changement dans le moteur `engine/`.

## Fondement et limites

[INCOG 2.0, attention (2023)](https://research.monash.edu/en/publications/incog-20-guidelines-for-cognitive-rehabilitation-following-trauma-5/) privilégie les stratégies appliquées aux activités quotidiennes et souligne le manque de généralisation des exercices informatisés décontextualisés. Cela motive le choix de tâches fonctionnelles ; **cela ne valide pas ces nouveaux exercices**, ni leur efficacité propre dans le syndrome post-commotionnel d'une personne à haut niveau antérieur. Les situations écrites restent des simulations à articuler avec les activités réelles en séance.

[Strangman et al., apprentissage verbal après TBI](https://pubmed.ncbi.nlm.nih.gov/19047359/) : étude d’imagerie de 25 personnes avec TBI chronique (> 1 an) et 20 témoins, apprentissage avec/sans stratégie de regroupement. Le [protocole publié](https://journals.sagepub.com/doi/pdf/10.1177/1545968308324225) présente les mots deux secondes chacun. Il ne démontre pas qu'une pause supplémentaire de deux secondes est optimale. Le réglage **2 + 2** est donc un choix de confort demandé pour ce POC, à éprouver avec l’utilisateur et l’orthophoniste.

Les listes, seuils et trois paliers des nouveaux exercices ne sont pas étalonnés. Les productions libres sont comparées sur leur forme normalisée (accents, horaires…), pas par compréhension générale du sens. Des formulations équivalentes non prévues peuvent encore nécessiter une extension explicite. Les situations répétées entre paliers facilitent l’apprentissage mais excluent l’interprétation diagnostique d’un gain. Le bilan de séance existant conserve la réussite globale ; les détails par champ sont retournés à l’interface, sans créer de dossier clinique ou de profil.

La reprise **effectivement interrompue** reste à développer ultérieurement, comme convenu. Les anciens items « Garder le cap » restent des décisions sur situations décrites.
