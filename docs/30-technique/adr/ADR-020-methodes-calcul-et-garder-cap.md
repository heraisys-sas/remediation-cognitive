# ADR-020 — Méthodes de calcul et Garder le cap

Date : 2026-09-30. Statut : adopté sur la branche d’essai.

## Décision

`contenu.methode`, texte facultatif, prend priorité sur la consigne dans le panneau. Le titre devient « Une méthode possible » ; les trois questions génériques sont masquées. Le panneau est fermé à chaque nouvel item. L’ancien comportement est rétabli pour les items sans méthode. Aucun nouveau résultat intermédiaire ou solution n’est affiché par l’aide.

Les 212 items de calcul reçoivent une stratégie par famille et opération réelle, plus une vérification pertinente. Le champ `aide` est retiré pour éviter le doublon « Coup de pouce ». Opérations, énoncés et réponses conservés ; nouveaux identifiants `cm3-…` pour distinguer ces conditions d’aide. Les résultats intermédiaires restent à produire et maintenir mentalement. La consultation de ce texte ne vaut pas révélation de solution ; elle n’est pas comptée comme une réponse assistée. Aucun score d’autonomie sans aide n’est donc inféré de la réussite.

Une carte « Garder le cap » complète l’accueil : reprise après interruption, adaptation aux changements, vérification finale. La livraison initiale comptait douze vignettes à choix `but-etapes`, avec second essai et quatre items par séance. Source de contenu et catégorie sont enregistrées côté serveur, libellés centralisés. Le programme de huit semaines n’est pas modifié automatiquement.

Extension du 2 octobre 2026 : les quatre vignettes du parcours Reprendre sont remplacées par douze tâches de type `reprise-interrompue`. La personne commence un contrôle en quatre points ; après un, deux ou trois points, un message sans rapport masque le dossier et exige un choix. Le dossier reste masqué pendant la question « où reprendre ? », puis revient pour achever le contrôle. Le détour est volontairement non noté : il sert d’interruption, sans ajouter une mesure parasite. La réussite porte sur le point de reprise et les quatre décisions du contrôle. Les deux autres parcours restent inchangés. Nouveaux identifiants `cap-2-reprise-…` afin de ne pas attribuer l’historique des anciennes vignettes à la nouvelle tâche.

## Sources et portée

Voir le README du thème Garder le cap pour les sources primaires vérifiées, les populations, la matrice de conception et les limites. Il s’agit d’une adaptation pédagogique de stratégies métacognitives, pas d’une validation de ces items comme traitement ni d’une reproduction du GMT complet.

## Vérification

Couverture de toutes les familles calculatoires, contrôles des cas argent/durées/proportions et petits nombres, conservation des opérations/réponses, tests du panneau JS et de son retour au mode générique, exposition API de la nouvelle carte et séances sur les trois parcours, deuxième essai des QCM et correction, validation générale. L’extension vérifie en plus le masquage réel du dossier, la variation du moment d’interruption, la reprise au point suivant, le double clic et le retour détaillé par point.

## Précision du public

Après clarification utilisateur, les douze situations ont été rédigées pour un public de niveau antérieur élevé : alternatives proches, contraintes concurrentes et suivi des versions/états, sans jargon spécialisé. Références mTBI VA/DoD et GOALS ajoutées au README, avec limites de population. Le public visé ne constitue pas une efficacité démontrée ni une norme de difficulté.
