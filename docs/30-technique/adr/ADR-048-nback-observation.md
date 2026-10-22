# ADR-048 — N-back distinct dans Exercices ciblés

10 octobre 2026 — accepté, autorisation utilisateur explicite.

## Contexte

L’ancien type interne n-back correspond à un rappel de position sérielle. Une comparaison à chaque nouvelle position demande un protocole et des données différents. Les candidats d’observation sont destinés à Exercices ciblés, conformément au cadre cognitif récent et à l’instruction utilisateur.

## Décision

Ajouter une API et un journal distincts, un 1-back visuel à rythme libre et sans feedback avant fin, 16 présentations dont 15 décisions et cinq correspondances. Version et séquence originales conservées. Payload public limité à la position courante ; validation serveur et UUID idempotents. Pause/masquage interrompt, sans attribuer d’erreurs aux positions futures. Premier symbole et exemple exclus des résultats.

## Conséquences

Aucun changement de FSRS, des anciens exercices ou de leurs historiques. Observation descriptive sans diagnostic, score global ou transfert promis. Pas d’adaptation automatique ni 2-back dans cette version. Contrat exact dans [nback.md](../../20-specs/nback.md).

## Extension V2 — couverture de trois mois

Autorisation du10octobre : quantité et progression sur trois mois, cinq séances/semaine au total. Choix1/2/3-back persistant et volontaire ; n+15formes, ninitialisationsnoncotées,15décisions/cinqcibles pourtous. Pas d’adaptation calendaire ni nouvelle cadence. Anti-doublon canonique durable, archivesV1 incluses ;65créations uniques testéespar n. Tracer leurres/coïncidences voisins séparément, invisibles avantfin. Les résultatsV1restentinchangés. Cetteextension est une capacité de contenu, pas un programme thérapeutique de trois mois.
