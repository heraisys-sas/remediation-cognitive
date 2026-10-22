# Plan de développement cognitif

9 octobre 2026 — GO utilisateur reçu. Travail par lots ; aucune sélection implicite des nouveaux candidats. Sources : [cadre](cadre-exercices-cognitifs.md), [corrections](corrections-exercices-existants.md), [mémoires](memoires-immediates.md), [candidats](candidats-cognitifs.md).

## Lots et sorties vérifiables

| Lot | Livrable | Condition de sortie | État |
|---|---|---|---|
| 0 | Plan, responsabilités, sauvegarde de progression et reprise à 17 h 10 | Plan écrit ; automatisation attachée à la conversation ; aucun doublon lors de reprise | Terminé — reprise exécutée sans doublon |
| 1A | PQRST séquencé, texte masqué au rappel, retour S avant T conservé | Parcours complet, absence/aides distinguées, tests de masquage et transitions, journal additif persistant | Validé — 9 octobre 2026 |
| 1B | Résultats des deux passes de contexte | Photo sur Afficher, rappel sans photo puis photo après erreur ; résultats séparés, première réponse conservée et persistance testée | Validé — 9 octobre 2026 |
| 1C | Libellés fidèles, intégration API/persistance et validation commune | Aucun n-back continu annoncé pour la position sérielle ; compatibilité ancienne API/historiques, seul rappel final pris en compte par FSRS (ADR-039) | Validé — intégration et contrôles communs |
| 2 | Retenir un code, puis Refaire le chemin | Essai complet clavier/souris, masquage, aides, sortie et données de condition fiables | Implémenté et validé — branche memoires-immediates |
| 3 | Qu’est-ce qui a changé ?, puis Quel objet était où ? | Couleurs pertinentes, vrais essais identiques, association et ordre distincts, correction sans fuite | Implémenté et validé — branche memoires-immediates |
| 4 | Application des stratégies existantes | Plan exécuté/modifié, rappel externe utilisé, prise de message et estimation ; une action observable par tâche | Livré et validé localement — 10 octobre, V2 à trois variantes par parcours |
| 5 | Nouveaux candidats | Sélection explicite avant livraison ; destination entraînement ou Exercices ciblés et paramètres fixés | EX-CAND-010 sélectionné et livré localement ; autres candidats en attente |

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

## Lots 2–3 — quatre mémoires immédiates

GO utilisateur explicite, tâches backend, code/chemin et visuels réparties entre trois sous-agents ; intégration et recette par le parent. Carte unique de pratique, exemple facultatif et quatre essais, sans adaptation automatique. Pas de seconde version d’observation livrée. API distincte et stockage additif, sans modifier le moteur existant ; ADR-045. Paramètres persistants, overrides conditionnés au mode dérogatoire.

439 pytest réussis, 1 ignoré ; 35 tests Node dédiés ajoutés à la CI. Ruff et contrôles locaux de contenu/réponses/interface/phrases/syntaxe passent. Recette code (zéro initial, aide interrompue), chemin (clavier et annulation), changement (exemple hors données, décision verrouillée, localisation absente/fausse alerte), objets (emplacements vides et réserve indépendante, largeur 375 px). Les tests API parcourent les quatre essais de chacun des quatre parcours et les trois conditions visuelles.

Branche memoires-immediates depuis origin/dev 71b3df4. Intégration dans dev autorisée le 10 octobre ; le checkout remediation-dev utilisé par le serveur est conservé. Validation technique, pas clinique. Lot 4 reste à organiser ; candidats non sélectionnés inchangés.


## Reprise et progression — 10 octobre 2026

Les lots 2–3 ont été commités et poussés sur origin/dev : `44acda5`. Le nouveau lot local de paliers est décrit dans [paliers-memoires-immediates.md](paliers-memoires-immediates.md) et ADR-046. Arbitrage GPT Astra au niveau ultra : axes conservés, pas de norme ni de classement HPI ; clôtures chronologiques et révision de progression pour éviter les effets rétroactifs des blocs concurrents. Les répétitions de chiffres sont une nouvelle configuration, pas une hausse garantie de difficulté.

GO de poursuite utilisateur reçu : finaliser les paliers puis implémenter EX-REV-005 à 008 du lot 4, avec actions observables, journaux distincts et QCM historiques conservés. Agents `strategies_backend` et `strategies_frontend`, fichiers distincts ; raccordement, recette et documents par le parent. Code précis et concis, revue IA. Le lot 5 attend toujours une sélection.

Reprises de conversation programmées aujourd’hui à 3 h 15 puis 8 h 15 Europe/Paris : `reprise-orthogone-3h15`, `reprise-orthogone-8h15`. Lire le journal avant relance, vérifier agents et changements, ne pas créer de doublon ; rester silencieux si travail déjà en cours ou terminé. Le quota disponible reste une condition d’exécution. Aucun commit/push automatique pour ces nouveaux lots.

## Lot 4 — livraison locale V2

Paliers des mémoires et quatre simulations de stratégies intégrés dans le checkout deduction-corrections. Douze scénarios V2 en rotation persistée, archives V1 conservées. Les choix de conception et limites sont dans [la spécification servie](strategies-appliquees.md), ADR-046 et ADR-047.

Validation : 476 tests pytest réussis, 1 ignoré ; 71 tests Node réussis (35 mémoires, 10 contextes, 26 stratégies), Ruff et contrôle interface passent. Recette isolée : quatre parcours V1 complets ; plan V2 complet, puis variante atelier différente ; affichage à 320 px sans débordement. Six objets restent contenus dans leurs cases sur écran étroit. Durées active, pause et écoulée contrôlées séparément.

Reprise de 8 h 15 après interruption des agents par quota ; leurs modifications partielles relues et finalisées par le parent. Derniers changements : accès explicite à la réexposition du message avec restitution initiale conservée, documentation V2. Recette message V2 formulaire à 10 h après aide : restitution et action exactes ; viewport restauré et onglet de recette fermé. Le serveur de recette 8091 utilise les données isolées ; le checkout et le serveur habituels restent préservés. Aucune intégration dev/main ni commit/push de ces nouveaux lots. Lot 5 attend la sélection explicite ; relecture professionnelle et essai d’usage restent à réaliser.

## EX-CAND-010 — véritable n-back livré localement

Autorisation explicite du 10 octobre, conception/revue GPT Astra ultra et développement réparti backend/frontend. Un 1-back visuel sans cadence fixe dans Exercices ciblés, 16 présentations et 15 décisions, exemple indépendant ; comparaison à chaque position, historique retiré, feedback seulement après bloc. Contrat dans [nback.md](nback.md) et ADR-048. Pas de 2-back, dual n-back ou adaptation automatique.

494 tests pytest réussis, 1 ignoré ; 93 tests Node réussis, dont 22 n-back ; Ruff, interface et syntaxe passent. Recette : exemple ABBC complet, bloc complet de 15 décisions avec une absence déclarée (5 identiques reconnues sur5, 9 différentes reconnues sur10), aucune forme entre positions ; téléphone320px sans débordement, pause avant réponse et rechargement en cours de comparaison clôturés sans erreurs futures. Journal durable vérifié, console sans erreur, viewport restauré et onglet agent fermé.

Serveur recette 8091 mis à jour, données isolées ; aucun commit/push ni modification du checkout remediation-dev. Les autres candidats attendent sélection explicite. La clôture keepalive à la fermeture reste au mieux ; un arrêt brutal peut laisser une archive ouverte sans la qualifier de terminée.

## Couverture de trois mois — cinq séances hebdomadaires au total

Demande confirmée le 10 octobre : évaluer les cartes hors anglais/Python et couvrir 13 semaines, soit 65 séances réparties. L’[inventaire des 14 cartes](couverture-trois-mois-inventaire.md) détaille stocks, paliers, quotas et scénario de stress. Outil reproductible : tools/auditer_couverture.py, sans données personnelles. Les banques courtes et le programme de huit semaines sont signalés ; aucun calendrier existant n’est prolongé silencieusement.

N-back V2 : choix volontaire 1/2/3-back mémorisé, n premières formes non notées, n+15 formes, toujours 15 décisions et cinq cibles. L’anti-doublon canonique persistant inclut les archives V1 ; 65 ouvertures distinctes sont testées par n, avec redémarrage. Leurres et coïncidences sont séparés et masqués avant fin. Aucun changement de rythme ou promotion automatique.

Validation : 508 tests pytest réussis, 1 ignoré ; 99 tests Node réussis, dont 28 n-back ; Ruff, interface, diff et syntaxe passent. Recette 2-back complète : 17 formes et 15 réponses justes. Exemples 2/3-back, trois initialisations non notées, pause sans réponse, choix 3 mémorisé après rechargement, console sans erreur. Onglet de recette fermé. Serveur 8091 mis à jour avec données isolées (PID55180/session95818). Aucun commit/push.

## Enrichissement des banques courtes — finalisé le 10 octobre 2026

GO utilisateur puis relecture ciblée GPT Astra ultra : 126 nouveaux contenus (90 items + 36 simulations). PQRST guidé : 12 ; Garder le cap adapter/vérifier : 12 chacun ; différé et première série : 12 chacun par modalité ; SFA/PCA : 18 chacun ; contextes20 scènes ; stratégies12 situations par tâche (48 au total), protocole V3. Les variantes ambiguës de durée, les négations, les définitions et les situations contradictoires ont été corrigées. Les réponses/distracteurs des nouvelles scènes ont été relus pour limiter l’inférence sémantique.

Sources éditoriales datées et générateurs synchronisés, manifests actualisés. Anciens items et scénarios V1/V2 strictement conservés. Contextes : dix scènes maximum par séance, découverte puis rappel sans photo inchangés, fichiers WebP 640/960 légers ; textes exacts vérifiés visuellement. ADR-049 et contrat API mis à jour. Les 65 séances sont réparties entre les cartes, pas par carte ; programme actif de 8 semaines conservé.

Validation finale : **517 tests pytest réussis, 1 ignoré ; 99 tests Node réussis**. Validateur98 fichiers/1 424 items/12 manifests, zéro erreur ; correcteurs, Ruff, interface et diff passent. Tests de régénération et intégrité des images ; rotation 12+1 et reprise/archives stratégies V1/V2. Recette8091 chargée, dix scènes maximum constatées, nouvel asset640 servi, aucune erreur console ; onglet de test fermé. Serveur PID57657/session46354, données isolées ; checkout remediation-dev intact. Aucun commit/push.

Relecture orthophonique et essai auprès du public restent à réaliser ; cette revue IA ne les remplace pas. L’[inventaire final](couverture-trois-mois-inventaire.md#banques-enrichies-après-go--état-final-du-10-octobre-2026) distingue les stocks avant/après.
