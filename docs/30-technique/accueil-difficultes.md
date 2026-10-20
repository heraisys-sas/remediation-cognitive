# Accueil personnalisé par difficultés

Décision du 20 octobre 2026 — issue #25, adaptée après la demande utilisateur de privilégier les difficultés rencontrées après un traumatisme crânien.

## Choix éditorial

Le réglage « Ce que tu souhaites travailler » présente des difficultés reconnaissables, sans attribuer de diagnostic. La sévérité initiale du TCC n’est pas un profil de sélection : une commotion relève du TCC léger, mais ses effets peuvent être importants. Les TCC modérés et sévères sont des situations distinctes ; aucune prescription de carte ou de difficulté n’est déduite de leur gravité.

La revue de conception par un sous-agent adoptant une perspective d’orthophonie neurologique n’est pas une validation clinique par un professionnel. Les correspondances ci-dessous décrivent les tâches du logiciel et non leur efficacité thérapeutique.

| Choix | Cartes associées et parcours pertinents |
|---|---|
| Concentration et attention | Repérer l’essentiel ; Comparer deux documents ; Garder le cap (reprise après interruption) ; Méthodes (chercher dans un document). |
| Mémoire immédiate | Mémoires immédiates (quatre parcours) ; Retenir et manipuler (rappel direct) ; Mémoriser des séries (rappel immédiat, lu/entendu). |
| Manipuler des informations en tête | Actualiser une consigne ; Retenir et manipuler (ordre inverse et position dans une séquence) ; N-back, si disponible. |
| Retrouver une information mémorisée | Mémoriser des séries (différé) ; Retrouver des mots et leur contexte (contexte) ; Méthodes (PQRST) ; Application des stratégies (message), si disponible. |
| Trouver ses mots | Retrouver des mots et leur contexte (accès lexical, SFA, PCA). |
| S’organiser et penser à agir | Au quotidien ; Méthodes ; Application des stratégies, si disponible. |
| S’adapter et vérifier ses actions | Garder le cap ; Actualiser une consigne ; Comparer deux documents ; Application des stratégies, si disponible. |
| Raisonner et calculer | Déduction ; Calcul mental. |
| Autres apprentissages | Anglais ; Python, dans la rubrique Extra. Ce choix n’est pas une difficulté post-commotionnelle. |

Les cartes sont filtrées entières, sans retirer de parcours. Les listes « Cartes : … » sont générées à partir des cartes effectivement rendues et reprennent leurs titres. Une carte associée à plusieurs choix n’est jamais dupliquée. Les mots lus et entendus restent regroupés dans la carte Mémoriser des séries. Une activité future non classée apparaît sous « Autres activités disponibles » plutôt que disparaître du réglage par défaut.

Le contexte peut être travaillé avec les scènes de la version web ; la reconnaissance du contexte sans photo n’est pas assimilée à un rappel libre. Les QCM de stratégie restent des choix/reconnaissances, les documents visibles ne sont pas présentés comme des tests de mémoire. La position dans une séquence et le véritable n-back sont distincts. La fatigue, la sensibilité sensorielle et le ralentissement ne reçoivent pas de carte prétendant les traiter spécifiquement. Les réglages de confort restent transversaux.

## Fonctionnement

- Réglages depuis l’en-tête → Ce que tu souhaites travailler. Cases natives, descriptions associées, commandes au clavier et cibles de 44 px minimum.
- Aucune préférence : toutes les cartes sont affichées. Préférence vide explicite : aucune carte, avec accès direct aux réglages.
- Persistance locale sous `orthogone.accueil.difficultes.v1`, sans bouton de validation. Une erreur de stockage restaure les cases et le dernier choix appliqué, avec un message lisible.
- Une préférence illisible revient à l’affichage complet sans réécrire le stockage.
- Les changements ne font que masquer/afficher les articles déjà rendus et leurs rubriques. Aucune requête de séance, modification des résultats, réinitialisation ou interruption de séance. Les distinctions entraînement/exercices ciblés/Extra et les ressources restent inchangées.
- Le catalogue n’est publié dans les réglages qu’une fois les cartes rendues ; les changements rapides ne recréent pas leurs commandes.

## Sources et portée

- [Living Concussion Guidelines — Cognitive Difficulties](https://concussionsontario.org/concussion/guideline-section/cognitive-difficulties) : attention/concentration, vitesse de traitement, apprentissage/mémoire et fonctions exécutives ; facteurs associés et stratégies compensatoires. Ces domaines motivent les regroupements, sans valider les exercices du logiciel.
- [CDC — About Mild TBI and Concussion](https://www.cdc.gov/traumatic-brain-injury/about/index.html) : distinction entre l’appellation de TCC léger et la possibilité d’effets importants.
- [INCOG 2.0 — Attention](https://doi.org/10.1097/HTR.0000000000000839), [fonctions exécutives](https://doi.org/10.1097/HTR.0000000000000834), [mémoire](https://doi.org/10.1097/HTR.0000000000000837) : références complémentaires sur les stratégies fonctionnelles et compensatoires après TCC, principalement modéré/sévère ; pas d’extrapolation d’efficacité à nos implémentations.

## Vérification

`node --test tools/test_accueil_difficultes.cjs`, également exécuté depuis pytest : catalogue complet, préférence vide et rechargement, recouvrements, sélection exacte, changements rapides sans recréation, stockage refusé, préférence corrompue, catalogue incomplet/nouveau, commandes Tout afficher/Tout masquer. Stockage synthétique uniquement dans les tests automatisés.
