# ADR-044 — Observations distinctes et durables pour Contextes

Date : 9 octobre 2026. Statut : adopté dans le lot autorisé EX-REV-003.

## Contexte

La séance Contextes répond deux fois aux mêmes items : après photo, puis sans photo. Le stockage historique garde un booléen par item et ne permet pas de décrire ces passes séparément. La révélation de photo après erreur survient après correction. PQRST exige également une trace du protocole distincte de sa notation (ADR-043).

## Décision

Ajouter un journal `observations/<session_uuid>.json` dans le stockage local d’entraînement, écrit atomiquement sous verrou dès chaque réponse documentée, indépendamment du runner, des cartes et des historiques de maîtrise. Il contient les passes Contextes et les observations PQRST. Les séances actives restent en mémoire ; ce journal ne les rend pas reprenables après redémarrage.

`POST …/reponses` accepte `observation_contextes` optionnel : passe, ordre réel, horodatages de présentation/exposition et incident photo. L’item doit être de type rappel-source. Les métadonnées sont bornées ; la réponse initiale, sa justesse, son aide et son temps viennent du traitement serveur et sont conservés une seule fois par item/passe. Le rappel documenté exige une première réponse de découverte déjà enregistrée. Les clients anciens sans métadonnées conservent leur comportement.

`POST …/fin` accepte un corps optionnel `observations_contextes`, tableaux `decouverte` et `rappel`. Seuls les faits de présentation, exposition, révélation et incident sont fusionnés ; aucune justesse cliente ne remplace une correction. Une révélation après erreur exige une première réponse de rappel erronée. Les IDs inconnus, les doublons et les ordres incompatibles sont refusés avant toute écriture. La clôture retourne les observations pour Contextes seulement.

`POST …/observations` accepte un checkpoint PQRST normalisé et borné par le helper de l’ADR-043, sans correction ni enregistrement dans le runner. Une observation complète corrigée ne peut pas être remplacée par un checkpoint partiel. Le stockage est relisible par `StockageJSON.lire_observations(session_uuid)` après redémarrage ; aucun écran de consultation historique ni endpoint de lecture n’est introduit.

## Conséquences

Conformément à ADR-039 (rappel final), la découverte utilise `memorisation: true` et n’alimente ni FSRS, ni maîtrise, ni temps de référence. Le journal conserve cette passe sans notation moteur. Seule la première réponse du rappel final alimente la progression ; les anciens historiques ne sont pas réinterprétés. Les deux passes disposent de résultats distincts et ne sont jamais additionnées en score de mémoire dans le résumé affiché. Les horodatages de présentation sont des faits déclarés par le navigateur ; ceux de validation viennent de l’horloge serveur. Le journal ne copie aucune photo. Les anciens historiques ne reçoivent aucune condition supposée.
