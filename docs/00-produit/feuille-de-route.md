# Feuille de route

## État d’intégration vérifié — 21 octobre 2026

Les cases historiques ci-dessous décrivent leur date de validation, pas toujours
l’état intégré. Les paliers des quatre mémoires, les stratégies appliquées V3,
le n-back 1/2/3 et les banques enrichies sont réunis sur
`feat/lots-cognitifs-complets`, avec le filtre d’accueil de la PR #27.
Validation de cet ensemble : 518 tests Python réussis, 1 ignoré ; 99 tests Node,
24 tests Playwright Chromium/WebKit (bureau et mobile jusqu’à 320 px), Ruff et
validateurs de 1 424 items conformes. Les tests navigateur de l’accueil incluent
les deux nouvelles cartes ; ils ne constituent pas une recette physique de tous
les exercices ni une validation clinique.

La fusion dans `dev` reste distincte de la livraison sur `main`. Le retrait du
graphe est intégré dans `dev` par PR #26. Le déploiement local fait l’objet de la
PR #28 ; la calibration #6 reste active. Gestion des utilisateurs et transfert
de progression ne sont pas ajoutés. Les cinq séances hebdomadaires servent au
dimensionnement des contenus, sans nouveau plafond global imposé. Le programme
logiciel de huit semaines reste inchangé ; treize semaines nécessitent un choix
explicite. Autres candidats et export de synthèse restent à arbitrer.

## Référentiel des compétences et des exercices

Le [référentiel cognitif](../10-clinique/referentiel-exercices.md) relie les compétences, exercices retenus, justifications déjà examinées et implémentations réelles. Sa première version détaille les mémoires immédiates et inventorie les autres compétences à partir des cartes et de cette feuille de route. La [revue des exercices implémentés](../10-clinique/revue-competences-exercices.md), autorisée le 9 octobre 2026, apporte classification, sources Consensus et propositions de révision. Le signal a ensuite été donné : la [recherche des exercices pour les compétences prévues](../10-clinique/recherche-exercices-feuille-de-route.md) prépare leur sélection avant de nouvelles spécifications. Les formats d’observation peuvent rejoindre « Exercices ciblés », rubrique d’autoévaluation, selon la précision de l’utilisateur. Il ne vaut pas autorisation de développer de nouveaux exercices ni de réactiver le bilan historique.

## Spécifications cognitives — 9 octobre 2026

Le [cadre commun](../20-specs/cadre-exercices-cognitifs.md) traduit le référentiel, la revue et la recherche en protocoles relisibles, avec distinction entraînement/autoévaluation. Décision documentaire : [ADR-042](../30-technique/adr/ADR-042-cadre-cognitif-et-autoevaluation.md). Aucun code ni contenu d’exercice modifié par ce lot.

- [x] Spécifier les [corrections de l’existant](../20-specs/corrections-exercices-existants.md) : PQRST, faux n-back, deux passes du contexte, actions de stratégie et objectifs fidèles. Déduction, Calcul mental et Retrouver le mot conservés.
- [x] Spécifier les [quatre mémoires immédiates retenues](../20-specs/memoires-immediates.md) ; les trois pistes écartées restent exclues.
- [x] Rédiger les [fiches candidates](../20-specs/candidats-cognitifs.md), toutes en statut **proposition à arbitrer**, y compris les usages d’observation/réserve.
- [ ] Arbitrer sélection/destination des candidats et paramètres proposés ; une priorité documentaire ne vaut pas décision de livraison.
- [ ] Réaliser les corrections et les mémoires retenues par lots indépendants, après fixation des paramètres ; état logiciel actuel dans chaque fiche.
- [ ] Effectuer relecture professionnelle et essais de compréhension/confort ; cela ne constitue pas une validation clinique.

## Lot autorisé le 1er octobre 2026

- [x] Fusionner l’état courant de la branche d’essai dans main (8a75404).
- [x] Clarifier les rubriques et les descriptions ; ne plus présenter les exercices actuels comme une évaluation standardisée.
- [x] Séries : 2 secondes d’affichage + 2 secondes de pause ; parcours lus et entendus séparés, voix locale française, mots préparés et mutualisés. Réglage de confort, pas norme validée.
- [x] Développer Actualiser une consigne et Comparer deux documents.
- [x] Remplacer l’entrée Concentration par Repérer l’essentiel ; retirer la carte « Calculs en chaîne et suites » à la demande de l’utilisateur.
- [x] Valeur ajoutée des chaînes et suites examinée : décision de retirer leur carte sans modifier Calcul mental ni créer de remplacement.
- [ ] Relecture des nouveaux contenus avec l’orthophoniste ; ajuster rythme et charge selon l’essai.
- [x] Reprise après interruption réellement vécue : contrôle commencé, détour non noté, dossier masqué, point de reprise puis achèvement.

Voir [ADR-022](../30-technique/adr/ADR-022-parcours-series-et-attention-fonctionnelle.md).

## Suivi actif — vérifié le 8 octobre 2026

La référence est l’état livré sur `main`, pas une ancienne case non cochée.

### Livré

- [x] Moteur adaptatif, maîtrise, orchestration, répétition espacée FSRS et propositions d’arrêt.
- [x] Parcours indépendants, correction locale et dictée locale, séries lues/entendues séparées.
- [x] Parcours lexical adulte à douze paliers et 288 mots (PR #19).
- [x] Catalogue partagé, correcteurs et interface découpés ; validateurs conservés (PR #21, issue #5).
- [x] Référence des temps personnalisée : médiane de cinq à cent premières réponses correctes sans aide ; repli initial à 1000 ms (issue #9).
- [x] Appels de synthèse testés par faux sous-processus en CI, sans dépendre d’une voix installée (issue #10).
- [x] Scènes de contexte versionnées, découverte puis rappel final, et rejeu des items non dus (PR #22).

Dans les scènes, les premières questions servent à mémoriser et ne comptent pas pour la progression. Le résumé, la maîtrise et FSRS reposent sur le rappel final uniquement (ADR-039). Un arrêt pendant la découverte ne produit aucun résultat de rappel.

### Priorité suivante : correction sémantique locale — issue #6

- [ ] Constituer un corpus versionné de formulations acceptables et de contre-exemples, tiré des tâches à réponse libre existantes, avec décisions attendues relues.
- [ ] Mesurer séparément le repli lexical et Apple NaturalLanguage ; conserver scores, fournisseur et disponibilité. CI : repli déterministe ; poste Mac : moteur Apple réellement exécuté, aucun score simulé présenté comme calibration.
- [ ] Vérifier les erreurs proches : négations, nombres, horaires, jours, rôles et actions inversés. Garder les mots stricts, séries, nombres et QCM hors de la similarité sémantique.
- [ ] Documenter les divergences et le mode dégradé. Justifier les seuils par fournisseur sur un corpus de contrôle distinct ; ne pas annoncer une validation clinique.
- [ ] Ajouter les cas aux tests et consigner le choix dans un ADR avant de modifier la règle d’acceptation.

Périmètre : rester hors ligne, sans modèle supplémentaire obligatoire ; préserver la tolérance aux articles et petites contextualisations. Un score lexical ne mesure pas la même chose qu’une proximité vectorielle : le seuil 0,78 commun ne vaut pas calibration établie. Aucune modification du seuil dans cette remise en cohérence documentaire.

### Autres travaux ouverts

- [ ] Relecture informelle des contenus avec l’orthophoniste et essais de confort ; aucune validation clinique présumée.
- [ ] Préciser l’usage mono-utilisateur local et les conséquences d’une exposition réseau (issue #7). Aucun chantier d’authentification imposé au POC.
- [ ] Décider de l’utilité et du périmètre d’un export JSON/PDF avant son développement. L’ancienne issue #8 est close par décision du 20 octobre 2026 : elle n’engage plus la livraison d’un export ni d’un moteur de graphe. L’export reste différé, sans fonctionnalité livrée.
- [x] Retirer le module de graphe vide et corriger les mentions le présentant comme implémenté (20 octobre 2026).
- [ ] Piste ultérieure : générer une représentation documentaire des exercices, compétences et articles scientifiques cités, éventuellement lors d’une release. Périmètre et automatisation à décider ; voir [l’architecture](../30-technique/architecture.md#relations-entre-exercices-compétences-et-références).
- [ ] Vérifier le rythme et la charge sur les usages réels avant toute nouvelle adaptation du dosage.

### Orientations sorties du backlog actif

Le bilan standardisé, l’IRT, le bilan automatique toutes les deux semaines et une batterie diagnostique ne sont pas autorisés par cette feuille de route. Les anciennes phases réglementaires ne sont pas des tâches du sprint de laboratoire. Leur historique reste dans Git ; une éventuelle réouverture exige une décision explicite.

## Prototypes d’épreuves cognitives — contrats complémentaires

La backlog du 7 octobre 2026 a été remplacée par la [spécification des prototypes d’épreuves cognitives](../20-specs/prototypes-epreuves-cognitives.md), version 1, selon [ADR-038](../30-technique/adr/ADR-038-prototypes-epreuves-cognitives.md). Elle est conservée pour ses contrats détaillés de couleurs/comptage vocal, corrections entrelacées et palette de figures. Le [tableau d’articulation](../20-specs/cadre-exercices-cognitifs.md#9-articulation-avec-les-spécifications-antérieures) définit les exigences remplacées ; l’ancien ordre de lots n’engage plus leur livraison.

- [x] Formaliser déroulements, réglages, comptage, interruptions et critères d’acceptation.
- [ ] Arbitrer les candidats correspondants avant leur développement ; couleurs et corrections entrelacées ne deviennent pas une priorité d’entraînement par défaut.
- [ ] Vérifier les règles de mesure et le confort à partir des essais locaux avant d’ajouter les comparaisons avancées.

L’observation personnelle rejoint la destination « Exercices ciblés » ; une version d’entraînement exige une pratique réelle et un protocole séparé. Corsi est repris dans Refaire le chemin, principe déjà retenu ; n-back, double tâche et recherche visuelle ont des fiches candidates, sans sélection implicite. Aucun diagnostic ni bilan standardisé/IRT réactivé.

## Développement autorisé le 9 octobre 2026

Le [plan de développement cognitif](../20-specs/plan-developpement-cognitif.md) organise les corrections existantes, puis les quatre mémoires immédiates retenues. PQRST séquencé et résultats séparés des deux passes de contexte sont implémentés et validés le 9 octobre 2026 ; voir les contrôles et limites dans le plan. Les nouveaux candidats restent à sélectionner. Reprise de conversation exécutée à 17 h 10 Europe/Paris, sans doublon.

### Quatre mémoires immédiates — branche de développement

- [x] Retenir un code, Refaire le chemin, Qu’est-ce qui a changé ?, Quel objet était où ? : pratique guidée V1, interface discrète, aides/interruption et données durables séparées.
- [x] Validation technique : 439 tests pytest, 35 tests Node dédiés et recette des quatre interfaces, dont objets à largeur mobile.
- [x] Intégration dans dev : commit 44acda5 poussé le 10 octobre.
- [ ] Livraison sur main après autorisation et essai d’usage.

Les paramètres restent des choix de conception. Les candidats d’attention/inhibition/flexibilité restent en attente de sélection. Les paliers des mémoires et l’application des stratégies sont désormais validés localement, sans intégration supplémentaire dans dev/main.

### Paliers demandés le 10 octobre

- [x] Progressions par charge puis rétention implémentées localement pour les quatre mémoires ; [détails et sources](../20-specs/paliers-memoires-immediates.md).
- [ ] Valider le confort des paliers avancés en usage, puis intégrer ce nouveau lot dans dev.

### Application des stratégies et paliers — livraison locale du 10 octobre

- [x] Progressions persistées des quatre mémoires, avec paramètres avancés séparés et historiques conservés.
- [x] Quatre simulations d’application : plan, rappel, message et estimation du temps ; trois situations par parcours, une carte d’accueil.
- [x] Validation locale : 476 tests pytest réussis, 1 ignoré ; 71 tests Node réussis ; recette et limites dans le [plan](../20-specs/plan-developpement-cognitif.md#lot-4--livraison-locale-v2).
- [ ] Relecture professionnelle et essai avec le public visé.
- [ ] Intégration de ce nouveau lot dans dev puis livraison main après autorisation.

Les [propositions d’arbitrage](../20-specs/arbitrage-prochains-lots.md) ne sélectionnent aucun candidat supplémentaire.

### N-back dans Exercices ciblés — 10 octobre

- [x] EX-CAND-010 sélectionné explicitement et implémenté localement : 1-back visuel à rythme libre, comparaison successive, 16 formes, 15 décisions, correction après bloc.
- [x] Exemple hors journal, absence séparée, interruptions et retries durables, interface mobile calme.
- [x] Validation : 494 tests pytest réussis, 1 ignoré ; 93 tests Node réussis, recette complète et interruptions.
- [ ] Intégration dev/main après autorisation ; essai d’usage et relecture professionnelle.

[Spécification de la version servie](../20-specs/nback.md). Aucun autre candidat sélectionné.

### Couverture trois mois — 10 octobre

- [x] Dimensionnement confirmé : 13 semaines, cinq séances par semaine au total, 65 séances réparties.
- [x] Audit des 14 cartes hors anglais/Python : stocks par palier/parcours, répétitions FSRS, banques courtes et calendrier de huit semaines signalés.
- [x] N-back V2 : trois distances volontaires, choix persistant, 65 séries nouvelles testées par niveau, anti-doublon durable et archives conservées.
- [ ] Enrichir les banques courtes après choix de priorité et relecture.
- [ ] Programme logiciel de treize semaines éventuel : nouvelle version et choix explicite à définir, sans prolongation des programmes commencés.

[Rapport et répartition de 65 séances](../20-specs/couverture-trois-mois-inventaire.md). Validation : 508 pytest et 99 Node réussis, 1 pytest ignoré. Aucun commit/push.

### Banques courtes enrichies — livraison locale du 10 octobre

- [x] 126 nouveaux contenus relus : PQRST : 12, adapter/vérifier : 12 chacun, différé/première série : 12 chacun par modalité, SFA/PCA : 18 chacun, contexte : 20 scènes, stratégies : 12 situations par tâche.
- [x] Sources datées et régénération testée ; anciens IDs/contenus préservés ; photos WebP640/960, dix scènes maximum par séance.
- [x] 517 tests pytest réussis/1ignoré, 99 tests Node réussis ; validation contenu et Ruff passent. Recette8091 actualisée, aucun commit/push.

La couverture vise65 séances réparties sur13 semaines, avec répétition espacée ; programme actif de 8 semaines inchangé. Relecture professionnelle/essai d’usage restent ouverts. Voir [inventaire final](../20-specs/couverture-trois-mois-inventaire.md).
