# 2026-10-09 — nouvelles spécifications cognitives

## Demande et périmètre

Rédaction des spécifications à partir du référentiel v1.3, de la revue des exercices existants et des quatorze sources de la recherche préparatoire. Travail documentaire uniquement ; tous les changements préexistants conservés. Aucune suppression d’exercice, aucun changement de code/contenu, aucun commit/push.

## Livrables

- [Cadre](../docs/20-specs/cadre-exercices-cognitifs.md) : entraînement, Exercices ciblés et double usage, données minimales, comparabilité, confort et critères transverses.
- [Corrections existantes](../docs/20-specs/corrections-exercices-existants.md) : fidélité PQRST, classement du pseudo-n-back, contexte à deux passes, application des stratégies et conservation des trois exercices prioritaires.
- [Mémoires immédiates](../docs/20-specs/memoires-immediates.md) : EX-MI-001 à 004 détaillés ; EX-MI-005 à 007 toujours écartés.
- [Candidats](../docs/20-specs/candidats-cognitifs.md) : onze fiches, toutes propositions à arbitrer ; aucune priorité documentaire convertie en décision de livraison.
- [ADR-042](../docs/30-technique/adr/ADR-042-cadre-cognitif-et-autoevaluation.md), liens du référentiel v1.4 et de la feuille de route ; annotations de portée sur ADR-038, prototypes et ancienne proposition PQRST.

## Décisions et pièges

Les tâches d’observation peuvent aller dans Exercices ciblés selon décision récente de l’utilisateur. Cette précision prime sur les exclusions évaluatives des documents plus anciens. Non validé comme traitement ne veut pas dire incapable d’entraîner la tâche ; aucun effet clinique ou transfert général promis.

PQRST : la proposition historique fixait un résumé après la reformulation. Défaut conservé : modèle montré après S, retiré avant T ; T est donc un rappel après feedback, pas un premier rappel autonome. Déplacer le résumé après T reste un arbitrage explicite. Cinq étapes et seuil éditorial 4/5 conservés.

Contexte : question après chaque photo, seconde passe sans photo, révélation de la photo après erreur, deux résultats séparés à développer. Photos légères et chargement vérifié avant exposition.

Objet–position : tirer la réserve indépendamment du modèle, sans imposer systématiquement une permutation sans point fixe qui donnerait un indice avec deux objets. Les associations finales ne sont pas indépendantes lorsque le dernier emplacement se déduit des autres.

Une pause pendant un maintien ou un flux interrompt l’essai ; ne pas soustraire la pause pour fabriquer un protocole continu. Couleurs et modalités alternatives changent parfois la tâche ; ne pas ajouter des noms de couleur qui donnent la réponse pour simuler une accessibilité équivalente.

Les prototypes restent nécessaires pour comptage vocal/couleurs, file de corrections et manipulation des figures. Le tableau d’articulation du cadre indique les sections conservées/remplacées ; pas de suppression prématurée.

## Arbitrages et vérifications

Sélection et destination des candidats, usages initiaux des quatre mémoires, paramètres proposés et moment du retour PQRST restent explicites. Relecture professionnelle et essais d’usage à réaliser ; aucun dosage clinique déduit des exemples.

Validation documentaire réussie : treize documents vérifiés, 111 liens locaux et leurs ancres contrôlés, aucun lien manquant ni espace final ; `git diff --check` passe. Les quatre spécifications totalisent 644 lignes. Aucun test applicatif pour ce lot sans code. Les sources existantes ont été réutilisées ; aucune nouvelle conclusion scientifique ou recherche Consensus ajoutée.
