# ADR-025 — Transactions de séance et vérification complète de P1

Date : 2026-10-05

## Contexte

L'incrément atomique introduit pour l'issue #1 n'était pas appelé par le service.
Verrouiller chaque fichier séparément ne protégeait pas les cycles lecture,
modification, écriture de la maîtrise, des cartes FSRS et des temps de référence.
La CI P1 ne lançait pas les tests backend et ne détectait donc pas la disparition
de `capacites.synthese_disponible`.

## Décision

Une transaction de thème (verrou de threads puis verrou fichier interprocessus)
englobe le démarrage, y compris vérification du quota et incrément atomique, et la
clôture complète. Le verrou est commun aux parcours d'un même thème. Les verrous
individuels restent distincts du verrou de transaction, sans acquisition imbriquée
du même fichier. Les outils qui modifient plusieurs états du thème doivent employer
`transaction_theme`, sans imbriquer deux transactions.

La CI exécute aussi les tests backend/interface et les validateurs du contenu.
`pytest` découvre désormais les tests P0 et P1. Des tests de synthèse simulent les
sous-processus macOS/Linux/Windows : passage exact du texte, réception des octets,
absence d'interpolation Windows et gestion d'un délai dépassé. Ils ne prouvent pas
la qualité de la voix ni le fonctionnement des exécutables réels sur chaque OS.
La disponibilité annoncée dépend à nouveau des exécutables détectés.

## Référence de temps (issue #9)

La calibration existe déjà : médiane des 100 derniers temps corrects sans aide,
utilisée à partir de cinq valeurs, repli à 1000 ms avant cela. Des tests ajoutés
vérifient le repli, la médiane et la fenêtre. Aucune nouvelle règle clinique ni
changement des seuils ; cette référence demeure une heuristique par parcours.

## Conséquences et limites

Les séances concurrentes conservent les mises à jour de stockage ; cela n'apporte
pas de transaction avec rollback après crash entre plusieurs fichiers. Le registre
des séances reste en mémoire dans chaque processus : le déploiement reste à un
worker, sauf routage garantissant qu'une séance retrouve son processus. Les tests
interprocessus existants vérifient les primitives sur POSIX ; Windows reste à
vérifier sur une machine Windows. Aucun changement des exercices ni des historiques.
