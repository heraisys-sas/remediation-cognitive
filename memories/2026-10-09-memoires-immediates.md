# Quatre mémoires immédiates — 9 octobre 2026

Branche `memoires-immediates`, base `origin/dev` 71b3df4. Aucun commit ni push de ce lot. Le serveur habituel de remediation-dev sur 8000 reste inchangé.

Implémentation de Retenir un code (visuel ou voix française locale du navigateur), Refaire le chemin, Qu’est-ce qui a changé ? (forme, couleur ou association), Quel objet était où ?. Trois sous-agents ont produit API/protocoles, séquences et visuels ; orchestration, intégration, revue et recette finale réalisées par le parent. Code et chemins distincts des anciens corpus. Quatre essais par bloc, exemples facultatifs hors résultats, pratique guidée seule. Première réponse immuable, aide séparée, interruption sans score. Réglages avancés persistants mais appliqués uniquement en mode dérogatoire. Pas de FSRS, normes ou score global.

Validation : suite Python 438 réussites, 1 test Apple optionnel ignoré ; 23 tests Node (6 séquences, 8 visuels, 9 orchestration). Ruff et contrôles des corpus existants réussis. CI étendue aux nouveaux tests Node. Recette navigateur réelle des quatre parcours : code initial zéro et interruption aidée, chemin au clavier et distinction ordre/éléments, changement association avec exemple et fausse alerte, objets avec annulation d’occupation et validation partielle. Les blocs manuels ont été terminés partiellement ; les blocs complets de quatre essais sont couverts par les tests backend pour les six configurations. Mobile 375 × 812 : aucune largeur excédentaire (375/375), paramètres de viewport rétablis ensuite.

Serveur de démonstration isolé sur http://127.0.0.1:8091/ui/, données /private/tmp/orthogone-mi-recette. Quatrième bloc ouvert avec dérogation à la limite, dans cette origine de test uniquement. Captures /private/tmp/orthogone-mi-chemin.jpg et /private/tmp/orthogone-mi-objets-mobile.jpg.

Documents actualisés : spécification, référentiel, plan, feuille de route, contrat API, ADR-045, README et changelog. Limites V1 : stockage sous verrou local au processus, pas de reprise après rechargement ni interface d’historique, mesures de durée déclarées par le navigateur. L’audio requiert une voix locale française disponible et ne bascule pas silencieusement en visuel. Prochaine étape : intégration du lot dans dev puis synchronisation du checkout exécuté, avec autorisation de commit/push.

## Ajustement demandé : cases sans texte

Suppression des libellés visibles des emplacements dans la réponse objets ; noms accessibles conservés via aria-label. Padding des boutons supprimé dans les cases, SVG centré et dimensionné relativement à la case ; largeur calculée selon le nombre d’objets, également dans les comparaisons. Les 23 tests Node passent après adaptation des sélecteurs accessibles.

Consigne objets : lecture automatique unique au démarrage, durée effective annoncée, bouton audio partagé avec les autres exercices (haut-parleur barré pour arrêter). Aucune lecture ni bouton audio dans la suite visuelle. Test de non-répétition ajouté : 24 tests Node au total ; deux tests de chargement de l’interface réussis.

Voix de consigne : même CAPACITES.lire et même préférence que les autres exercices ; attente explicite du chargement des voix natives avant ouverture du bloc pour éviter un repli navigateur prématuré. Test d’ordre chargement → session → consigne réussi (25 tests Node au total). Les préférences restent propres à chaque origine web, notamment 8000 et 8091.

Interaction objets simplifiée sur demande : réserve grisée et désactivée pour les objets placés ; clic sur une case occupée retire son objet, annulation restaure le placement. Bouton de retrait supprimé, spécification actualisée, tests retrait/réserve/annulation réussis.

Parcours chemin harmonisé : consigne initiale lue une fois avec durée du signal, disposition audio/actions commune, suite visuelle silencieuse, aucun bouton pause/absence. Clic sur une case choisie la retire et renumérote ; « Vider les cases » remet le trajet à zéro. Réponse incomplète ou vide acceptée après confirmation, sans réexposer le stimulus. Tests dédiés réussis ; 26 tests Node au total.

10 octobre : les quatre parcours partagent maintenant la consigne audio unique, disposition d’accueil et compte à rebours de 3 s entre exercices, avec pause/reprise pendant cette attente. Code : vider la saisie, confirmation de réponse vide (absence explicite) ou de longueur différente, conservation des zéros initiaux, aucun bouton « Je ne sais pas ». Changement : intervalle neutre 1,5 s, positions fixes, localisation partielle confirmable, boutons de sélection sans textes visibles. Chemin : traits SVG entre choix, retrait par clic, vide sauvegardable (correctif serveur testé). Progression « Exercice », bouton « Suivant ».

Code auditif : lecture par CAPACITES.lire avec la voix choisie, micro local automatique après stimulus. Dès qu’une transcription partielle contient le nombre attendu de chiffres, la capture est arrêtée pour finalisation ; seule la transcription définitive complète est validée automatiquement. Réponses vocales incomplètes ou ambiguës restent corrigeables, retours tardifs ignorés. Tests conversion zéro, arrêt/validation unique et voix commune réussis.
