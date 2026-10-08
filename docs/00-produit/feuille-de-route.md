# Feuille de route

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
- [ ] Décider de l’utilité et du périmètre d’un export JSON/PDF avant son développement (issue #8). Le graphe de connaissances n’est pas planifié ; les modules vides ne sont pas des fonctionnalités livrées.
- [ ] Vérifier le rythme et la charge sur les usages réels avant toute nouvelle adaptation du dosage.

### Orientations sorties du backlog actif

Le bilan standardisé, l’IRT, le bilan automatique toutes les deux semaines et une batterie diagnostique ne sont pas autorisés par cette feuille de route. Les anciennes phases réglementaires ne sont pas des tâches du sprint de laboratoire. Leur historique reste dans Git ; une éventuelle réouverture exige une décision explicite.

## Prototypes d’épreuves cognitives — spécification de référence

La backlog du 7 octobre 2026 est remplacée par la [spécification des prototypes d’épreuves cognitives](../20-specs/prototypes-epreuves-cognitives.md), version 1. Décision : [ADR-038](../30-technique/adr/ADR-038-prototypes-epreuves-cognitives.md).

- [x] Formaliser déroulements, réglages, comptage, interruptions et critères d’acceptation.
- [ ] Développer par lots : infrastructure, séries de couleurs, attention différée, reconstruction de figures.
- [ ] Vérifier les règles de mesure et le confort à partir des essais locaux avant d’ajouter les comparaisons avancées.

Familiarisation et mesure personnelle restent dans un périmètre local distinct de la remédiation, sans diagnostic ni réactivation implicite du bilan standardisé historique. Les pistes N-back, double tâche, Corsi et recherche visuelle sont conservées dans la spécification, hors version 1.
