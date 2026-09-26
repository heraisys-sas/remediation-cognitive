# ADR-010 — Dosage : la durée maximale est une proposition

**Statut** : accepté (2026-09-26)

## Contexte

La durée maximale de séance (dix minutes) avait été codée comme une **clôture automatique** : au-delà de la limite, la séance se fermait et les réponses suivantes étaient refusées (409). Deux problèmes constatés en usage réel :

1. la limite tombait **au milieu d'un exercice** : la personne voyait son travail refusé (« la séance n'est plus disponible ») — corrigé d'abord en conservant la réponse, puis en proposant l'arrêt ;
2. une grille de déduction dure plusieurs minutes : fermer la séance d'office au milieu d'un raisonnement est brutal.

Le cadre clinique est pourtant explicite (`docs/10-clinique/protocoles.md`) : **la fatigue et l'arrêt sont proposés, jamais imposés**. La durée était la seule règle qui imposait.

## Décision

**1. La durée maximale est une proposition, pour tous les thèmes.** Au-delà de la limite, la séance envoie `arret_propose: true` avec `motif_arret: "duree"`, **une seule fois**, puis reste ouverte : la personne continue ou termine (« Terminer la séance »).

**2. La réponse en cours est toujours conservée.** Aucune limite de temps ne fait perdre un travail déjà fait — elle ne peut, au pire, que proposer de s'arrêter.

**3. Le garde-fou de sur-sollicitation reste ailleurs** : limite de **séances par jour** (3 en entraînement, 1 en évaluation) et **nombre d'exercices par séance** (12 ; 6 pour la déduction, dont chaque item est long). C'est là que se joue le dosage, pas dans un couperet horaire.

**4. Le code de clôture ferme subsiste**, prêt pour un thème qui demanderait explicitement une limite dure (paramètre `duree_proposee` par thème).

## Conséquences

- (+) La règle est cohérente avec le cadre clinique : l'arrêt est proposé, jamais imposé — l'utilisateur garde la main, y compris quand il veut continuer.
- (+) Plus de séance cassée en pleine réponse, et plus de 409 déroutant : l'interface affiche une phrase claire (« La séance dure depuis dix minutes… ») et le bouton d'arrêt reste à portée.
- (+) Le dosage devient lisible : des **séances** comptées, des **exercices** comptés, pas un minuteur.
- (−) Le temps n'est plus une contrainte technique : c'est à l'interface et au contenu de rendre la séance naturellement courte (six grilles pour la déduction, douze items courts ailleurs).
- (−) Une personne qui insiste peut dépasser les dix minutes : c'est accepté explicitement (principe « proposition, jamais imposition ») — la limite de séances du jour reste, elle, ferme.
