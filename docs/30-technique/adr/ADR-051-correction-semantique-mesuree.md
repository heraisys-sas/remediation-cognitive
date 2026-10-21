# ADR-051 — Mesurer les réponses libres et borner les approximations

**Statut : accepté, correctif partiel — 21 octobre 2026. Issue #6 maintenue ouverte.**

## Contexte

Le score de proximité n'est pas une preuve d'équivalence. Le cas synthétique
« Paul appelle Marie pour confirmer le rendez-vous » / « Marie appelle Paul pour
confirmer le rendez-vous » vaut 0,8667 en lexical et 0,9913 avec Apple sur le poste
de mesure. Ce n'est pas un item du catalogue. Les rôles sont pourtant inversés.

Les prises de message réelles révèlent aussi des substitutions acceptées par Apple :
« chez la voisine » pour « chez la gardienne » (0,8831), alors que la formulation
acceptable « la cave » pour « la porte de la cave » vaut 0,8952. Choisir un seuil
entre ces exemples serait un surajustement, pas une validation.

Enfin, le contrôle de négation du filet sémantique pouvait être contourné par
la branche de réponse contenue dans une phrase (« pas chez la gardienne »).

## Décision

- Conserver le seuil historique 0,78 ; ne pas prétendre calibrer deux fournisseurs
  différents avec un petit échantillon de travail.
- Appliquer la même exclusion des négations aux réponses contenues dans une phrase.
  La ponctuation ne doit pas masquer un marqueur négatif.
- Refuser dans le filet approximatif une permutation des mêmes mots. Même inventaire
  de mots et score élevé ne prouvent pas des rôles identiques. Ce garde-fou est
  conservateur, sans analyse syntaxique ni nouvelle dépendance.
- Versionner le corpus et des mesures séparées lexical/Apple, avec origine des cas.
  Une mesure demandée à Apple échoue si le fournisseur manque ; aucun résultat
  lexical ne doit être présenté comme une mesure Apple.
- Ne modifier ni contenu historique, ni moteur adaptatif, ni contrat d'API.

## Conséquences et limites

Les quatre fausses acceptations visées sont supprimées dans les deux fournisseurs.
Le corpus reste petit, construit à la main, sans validation clinique indépendante.
Des permutations légitimes peuvent maintenant être refusées : ce compromis est
préféré à l'acceptation d'une inversion de rôles. Les synonymes absents du contenu,
les référents et relations spatiales restent à traiter explicitement.

L'issue #6 n'est pas clôturable : trois mauvaises substitutions restent acceptées
par Apple ; le lexical refuse encore une reformulation légitime. Le prochain lot
doit choisir des variantes/critères déterministes par item, étendre le corpus
indépendamment des règles puis mesurer séparément la généralisation. Une relecture
par IA n'est pas une validation d'orthophoniste.

Voir [la procédure et les résultats](../calibration-correction.md).
