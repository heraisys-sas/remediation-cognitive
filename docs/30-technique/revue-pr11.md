# Revue critique et extraction de la PR #11

Référence examinée : `c82bb7bd6e629fe293b3bc1f4c587d71680c960f`.
Base d'intégration : `acf74b5` (main), comparée également au travail local de dictée du 7 octobre 2026. Aucun contenu d'exercice remplacé.

| Sujet | Décision et justification |
|---|---|
| Stockage, compteur et transactions de séance | Repris : le temporaire fixe et les cycles lecture/écriture sans verrou peuvent perdre des mises à jour. Verrous de fichier et transaction de thème couvrent démarrage et clôture. Octet de verrou Windows initialisé. |
| Résolution de racine par recherche ascendante / variable d'environnement | Non repris : le constructeur accepte déjà une racine explicite ; la recherche heuristique ajoute une ambiguïté sans besoin d'installation démontré. |
| Extraction complète de la synthèse vocale | Non reprise : préserver le code courant, la seconde tentative et les voix natives déjà ajoutées. Repris seulement le texte Windows transporté hors du script et la vérification des deux exécutables macOS. Le code précédent utilisait déjà des arguments sans shell : ne pas présenter tout le module comme une faille corrigée. |
| Découpage similarité / détection des capacités / façade | Non repris : déplacement de code sans défaut fonctionnel corrigé ; préserver les points d'intégration et les tests actuels. |
| Fatigue partagée | Non repris : modifie le seuil du domaine de `>` à `>=` et le comportement sans temps de réponse. La centralisation mérite un changement distinct si l'alignement comportemental est décidé ; aucune nouvelle règle clinique introduite ici. |
| Normalisation UTC | Reprise seule : comportement identique, une fonction partagée avec réexports compatibles. Renommage `_card` / `_carte`, réécritures de commentaires et autres changements cosmétiques écartés. |
| Tests concurrence | Repris et adaptés : processus `spawn` au lieu de `fork` (évite d'hériter de verrous de threads), délais et terminaison des processus ; intégration démarrage/clôture avec fichiers temporaires. Aucun test sur les données utilisateur. |
| Tests sélection et dates | Repris dans les répertoires déjà collectés par pytest, sans sous-arborescences P0/P1 supplémentaires. |
| Tests du découpage et tests structurels de P0 | Non repris lorsqu'ils vérifient un découpage rejeté, une existence de symbole ou une écriture séquentielle déjà couverte ; tests fonctionnels ciblés à la place. |
| Deux workflows CI | Remplacés par un workflow : suite complète, validateurs de contenu/réponses/interface, rendu des indices, syntaxe JS/Python. Ni tests moteur non bloquants ni référence de branche historique codée en dur. Aucun déploiement automatique nécessaire pour le POC local. |
| Dépendances « figées » | Le fichier de la PR utilisait seulement des bornes minimales et autorisait FSRS 1. Corrigé : plages majeures compatibles, FSRS 6, uniquement dépendances utilisées ; explicitement pas un lock transitif. |
| Documentation d'économie de contexte | Non reprise : instructions spécifiques à d'autres outils/modèles, sans lien avec le fonctionnement de l'application. |

## Limites conservées

Les sessions en cours restent en mémoire : les verrous protègent les fichiers partagés, ils ne rendent pas le serveur compatible avec une répartition arbitraire des requêtes d'une même session entre plusieurs workers. Les fichiers sont remplacés atomiquement un par un : une transaction de thème garantit la sérialisation, pas un rollback multi-fichiers après panne machine. Le verrou Python global est acceptable pour ce POC local ; aucune promesse de montée en charge.

Le test Windows de voix vérifie les arguments transmis, pas une synthèse réelle sous Windows. La CI Linux ne certifie pas l'audio Apple réel. Les ajouts locaux non committés (dictée, cartes, interface) restent dans leur checkout et ne sont pas inclus ni écrasés.

## Processus simple

Une branche courte par lot depuis main à jour, une PR vers main, contrôles bloquants de fait avant fusion, suppression automatique après fusion. Aucun besoin de branches permanentes P0/P1 ou d'intégration. La PR #11 sera fermée sans fusion après publication de cette extraction.
