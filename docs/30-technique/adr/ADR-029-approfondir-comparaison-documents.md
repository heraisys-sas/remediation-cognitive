# ADR-029 — Approfondir la comparaison de documents avec le modèle local

## Contexte

Issue #13 : après repérage des écarts, solliciter une justification et une réflexion
sur la conséquence ou la vérification à effectuer. Les questions génériques du
prototype PQRST ne suffisent pas à cet objectif.

## Décision

« Approfondir » ouvre un échange facultatif après correction de Comparer deux
documents. Justification libre (800 caractères) et deux relances maximum. Le second
appel reçoit le premier échange pour ne pas le répéter. Le score initial est figé.
Les documents restent consultables. Aucun changement de corpus ni d'identifiants.

POST `/api/capacites/accompagnement-documents` reçoit `item_id`, `reponses`,
`justification`, `echanges` (zéro ou un échange). Le serveur récupère les documents
et la correction de l'item dans le corpus autoritatif. Le client ne fournit pas le
corrigé. Retour : `disponible`, `relance` ou `raison` d'indisponibilité.

Le modèle Apple embarqué choisit un critère et un angle de réflexion. Le logiciel
compose une question française contextualisée avec les valeurs exactes du corpus.
Pas d'outil, de fournisseur réseau ni de repli cloud. Entrées bornées, sortie bornée,
expiration et affichage par textContent. Les conversations ne sont pas persistées.
Une réponse obsolète après changement d'exercice n'est pas affichée.

## Conséquences

Les essais de formulation libre ont attribué à tort des valeurs à la personne.
Le rendu est donc contrôlé : choix du point et de l’angle par le modèle, citations
du corpus par le logiciel. Ce cadre ne garantit pas la pertinence pédagogique.
La relance n'est jamais un nouveau verdict sur la réponse. Il faut notamment relire
les réponses correctes, partielles, contradictoires et paraphrases, ainsi que les
items entièrement conformes. L'intérêt clinique supplémentaire reste à évaluer.
L'absence du SDK, une erreur ou un délai n'empêchent pas de poursuivre la séance.
