# ADR-020 — Méthodes de calcul et Garder le cap

Date : 2026-09-30. Statut : adopté sur la branche d’essai.

## Décision

`contenu.methode`, texte facultatif, prend priorité sur la consigne dans le panneau. Le titre devient « Une méthode possible » ; les trois questions génériques sont masquées. Le panneau est fermé à chaque nouvel item. L’ancien comportement est rétabli pour les items sans méthode. Aucun nouveau résultat intermédiaire ou solution n’est affiché par l’aide.

Les 212 items de calcul reçoivent une stratégie par famille et opération réelle, plus une vérification pertinente. Le champ `aide` est retiré pour éviter le doublon « Coup de pouce ». Opérations, énoncés et réponses conservés ; nouveaux identifiants `cm3-…` pour distinguer ces conditions d’aide. Les résultats intermédiaires restent à produire et maintenir mentalement. La consultation de ce texte ne vaut pas révélation de solution ; elle n’est pas comptée comme une réponse assistée. Aucun score d’autonomie sans aide n’est donc inféré de la réussite.

Une carte « Garder le cap » complète l’accueil : reprise après interruption, adaptation aux changements, vérification finale. Douze situations, trois familles ; type à choix `but-etapes`, second essai existant, quatre items par séance. Source de contenu et catégorie enregistrées côté serveur, libellés centralisés. Le programme de huit semaines n’est pas modifié automatiquement.

## Sources et portée

Voir le README du thème Garder le cap pour les sources primaires vérifiées, les populations, la matrice de conception et les limites. Il s’agit d’une adaptation pédagogique de stratégies métacognitives, pas d’une validation de ces items comme traitement ni d’une reproduction du GMT complet.

## Vérification

Couverture de toutes les familles calculatoires, contrôles des cas argent/durées/proportions et petits nombres, conservation des opérations/réponses, tests du panneau JS et de son retour au mode générique, exposition API de la nouvelle carte et séances sur les trois paliers, deuxième essai et correction, validation générale.

## Précision du public

Après clarification utilisateur, les douze situations ont été rédigées pour un public de niveau antérieur élevé : alternatives proches, contraintes concurrentes et suivi des versions/états, sans jargon spécialisé. Références mTBI VA/DoD et GOALS ajoutées au README, avec limites de population. Le public visé ne constitue pas une efficacité démontrée ni une norme de difficulté.
