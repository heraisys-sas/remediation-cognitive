# Plan de développement cognitif

9 octobre 2026 — GO utilisateur reçu. Travail par lots ; aucune sélection implicite des nouveaux candidats. Sources : [cadre](cadre-exercices-cognitifs.md), [corrections](corrections-exercices-existants.md), [mémoires](memoires-immediates.md), [candidats](candidats-cognitifs.md).

## Lots et sorties vérifiables

| Lot | Livrable | Condition de sortie | État |
|---|---|---|---|
| 0 | Plan, responsabilités, sauvegarde de progression et reprise à 17 h 10 | Plan écrit ; automatisation attachée à la conversation ; aucun doublon lors de reprise | Terminé — reprise exécutée sans doublon |
| 1A | PQRST séquencé, texte masqué au rappel, retour S avant T conservé | Parcours complet, absence/aides distinguées, tests de masquage et transitions, journal additif persistant | Validé — 9 octobre 2026 |
| 1B | Résultats des deux passes de contexte | Photo sur Afficher, rappel sans photo puis photo après erreur ; résultats séparés, première réponse conservée et persistance testée | Validé — 9 octobre 2026 |
| 1C | Libellés fidèles, intégration API/persistance et validation commune | Aucun n-back continu annoncé pour la position sérielle ; compatibilité ancienne API/historiques, seul rappel final pris en compte par FSRS (ADR-039) | Validé — intégration et contrôles communs |
| 2 | Retenir un code, puis Refaire le chemin | Essai complet clavier/souris, masquage, aides, sortie et données de condition fiables | Après lot 1 |
| 3 | Qu’est-ce qui a changé ?, puis Quel objet était où ? | Couleurs pertinentes, vrais essais identiques, association et ordre distincts, correction sans fuite | Après lot 2 |
| 4 | Application des stratégies existantes | Plan exécuté/modifié, rappel externe utilisé, prise de message et estimation ; une action observable par tâche | À organiser après les mémoires |
| 5 | Nouveaux candidats | Sélection explicite avant livraison ; destination entraînement ou Exercices ciblés et paramètres fixés | En attente de sélection |

Par défaut de conception, les mémoires retenues démarrent par une pratique simple ; une version d’autoévaluation utilise un protocole et des résultats séparés. Ce défaut reste présenté comme proposition avant son implémentation. Aucun nouveau candidat est ajouté à l’accueil par le présent GO. Les trois exercices protégés restent disponibles. Les contenus servis et historiques restent intacts ; changement de stimulus/protocole tracé.

## Coordination et qualité

Sous-agents sur des fichiers distincts, parent responsable de l’intégration et des contrats partagés. Ownership PQRST : sequence.js et correcteur séquence ; ownership contexte : session.js, state.js, résumé/feedback contexte et présentation des scènes. API, service, stockage et contrat intégrés par resultats_contextes après coordination ; parent : revue, plan et validation finale. Signaler tout fichier partagé avant modification. Code précis et concis, fonctions et contrats explicites ; commentaires pour invariants seulement, aucune architecture générique préalable imposée.

Tests ciblés sur comportements (masquage, correction, premières réponses, doublons et persistance). Puis contrôles CI adaptés : Ruff, pytest, contenu/réponses/interface et syntaxe JS. Inspection UI du lot avant le suivant : une étape active, commandes accessibles, arrêt/audio, fond et lisibilité. Aucun commit/push ou fusion automatique dans ce lot.

## Reprise

Automatisation de conversation `reprise-orthogone-17-h-10`, exécution unique le 9 octobre 2026 à 17 h 10 Europe/Paris. Lire ce plan et le dernier journal, inspecter agents/changements/tests ; reprendre le travail interrompu sans doublon. Si déjà en cours ou terminé, rester silencieux. L’exécution reste soumise à la disponibilité du quota ; la programmation ne contourne pas une limite de service.

Avant interruption, consigner fichiers touchés, dernier contrôle, échecs et prochaine action dans memories. Actualiser les états de ce tableau à chaque lot livré. Ne pas considérer un simple message de sous-agent comme une intégration validée.

## Validation finale du lot 1 — 9 octobre 2026

417 tests pytest réussis, 1 ignoré (inférence Apple locale réservée à une exécution explicite) ; 7 tests Contextes et 2 tests checkpoints Node réussis. Ruff 0.16.10, validation des 98 JSON/1334 items, réponses, interface, phrases, compilation Python, syntaxe JavaScript et `git diff --check` réussis. Exécution locale Python 3.13 / Node 24 ; la CI configurée en Python 3.12 / Node 22 n’a pas été exécutée à distance.

Recette navigateur avec données isolées : PQRST de bout en bout sur un texte, absence Q/S conservée, masquage et correction finale neutre ; Contextes, dix scènes puis dix rappels sans image, révélation après erreur, aucune image après réponse juste, résumé séparé conforme au journal durable (10/10 réponses par passe, 4 premières justes par passe, 6 photos revues). Les tests automatisés couvrent aides, interruptions, sorties partielles, incompatibilités et échec/réessai de checkpoint. Aucun test clinique, inférence Apple réelle ou recette mobile nouvelle revendiqué.

Limites : pas de reprise de séance après rechargement, ni écran de consultation du journal ; fermeture brutale avant checkpoint susceptible de perdre le travail inachevé. PQRST après modèle exclu des temps de référence et du compteur sans aide, sans modifier FSRS ou requalifier les historiques. Lots 2–4 restent à développer ; lot 5 attend la sélection. Aucun commit/push.

## Intégration sur dev

Le 9 octobre, intégration des commits déjà présents sur dev : découverte Contextes réservée à la mémorisation, seul rappel final dans FSRS/maîtrise/temps de référence. Les résultats descriptifs séparés et les journaux restent conservés. Nouveaux ADR renumérotés 042–044 pour préserver 039/040 de dev. Contrôles après résolution : 421 pytest réussis, 1 ignoré ; 12 tests Node, Ruff et vérifications de contenu/interface/syntaxe.
