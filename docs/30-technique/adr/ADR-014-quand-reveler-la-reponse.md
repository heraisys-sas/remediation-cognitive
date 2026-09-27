# ADR-014 — Quand révéler la réponse après une erreur

**Statut** : accepté (2026-09-27)

## Contexte

Deux questions posées en usage réel :

1. après une erreur, faut-il donner la réponse **tout de suite**, ou attendre un **nouvel essai** ;
2. les exercices de « Méthodes » semblent solliciter **la mémoire plus que la stratégie** — faut-il indiquer une stratégie de mémorisation ?

La littérature ne dit pas la même chose selon ce que l'exercice demande :

- **errorless learning** (Baddeley & Wilson ; revue de Middleton & Schwartz, 2012) — donner la réponse **immédiatement** après l'erreur, pour ne pas la laisser ré-encoder. Indiqué quand la personne ne peut pas se corriger seule (trouble mnésique, accès lexical ; Ptak et al. : l'avantage est maximal « là où la personne ne peut pas détecter ses erreurs »).
- **pratique de récupération / effet de test** (Roediger & Karpicke) et **hypothèse de guidage** (Schmidt, 1991 ; Winstein & Schmidt, 1990 : « réduire la fréquence du retour améliore l'apprentissage ») — c'est **l'essai** qui apprend ; un retour fréquent et immédiat améliore la performance **pendant** la séance mais **dégrade la rétention**. Indiqué quand la réponse se **raisonne**.

## Décision

**1. Jamais de réponse avant un essai.** Aucun exercice ne donne la réponse sans que la personne ait tenté — c'est le principe qui protège l'effet de test.

**2. Récupération → correction immédiate.** Quand l'exercice demande de **retrouver** une information (mémoire, compréhension d'un document, prise de message, mot à retrouver), la réponse s'affiche **tout de suite** après l'erreur : errorless learning (ADR-008 pour la forme, ADR-013 pour la reprise).

**3. Raisonnement → un second essai avant la réponse.** Quand l'exercice demande de **raisonner** — choisir un plan, formuler une auto-instruction, vérifier un plan (`but-etapes`, `auto-instruction`, `plan-a-verifier`) — la première erreur ne révèle **rien** : elle dit « reprends » et laisse les indices disponibles. C'est le **second** essai qui compte comme réponse de l'exercice (pour la maîtrise, la révision espacée et la reprise de fin de séance).

**4. La méthode se travaille avec sa méthode sous les yeux.** Le nom et les étapes de la méthode en cours (PQRST, GMT, auto-instruction, plan à vérifier, stratégie de lecture) s'affichent dans le panneau « Méthode » **pendant** l'exercice — et non seulement dans une consigne lue une fois par séance. Réponse à la seconde question : **oui, il faut indiquer la stratégie**, et elle doit rester visible pour être utilisable.

## Conséquences

- (+) Chaque exercice applique la pratique qui lui correspond : l'erreur n'est jamais ré-encodée là où elle le serait, et l'effort de récupération n'est jamais court-circuité là où il fait apprendre.
- (+) « Méthodes » cesse d'être une simple épreuve de mémoire : ses exercices de stratégie exigent un raisonnement, avec la méthode affichée.
- (+) Le premier essai raté d'un exercice de stratégie ne pèse plus comme un échec : c'est le second qui est évalué (maîtrise, FSRS, reprise).
- (−) Un exercice de stratégie demande **deux** tentatives : la séance peut être un peu plus longue sur ces paliers (compensé par le plafond de reprises, ADR-013).
- (−) Le **palier 1 de « Méthodes » (PQRST) reste, lui, un exercice de mémoire** : le texte est masqué avant les questions. C'est cohérent (PQRST est une méthode de mémorisation, et l'exercice en teste le résultat), mais **la méthode n'est pas mise en œuvre par la personne** — elle est seulement nommée. Pour aller plus loin, il faudrait des exercices qui demandent de **produire** une étape (poser sa question, reformuler) : cela suppose de nouveaux items à choisir, décision de contenu laissée à l'orthophoniste.
- (−) Les types à second essai sont énumérés dans le code (`domain/feedback.py`) : ajouter un type d'exercice de stratégie demande de l'y inscrire explicitement.
