# Feuille de route

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
- [ ] Intégrer la branche memoires-immediates dans dev selon le flux Git, puis livrer main après autorisation et essai d’usage. Aucun push/fusion automatique.

Les paramètres restent des choix de conception. Les candidats d’attention/inhibition/flexibilité non sélectionnés et l’application des stratégies restent en attente ; ce lot n’en développe aucun.
