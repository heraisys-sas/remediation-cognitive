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

La planification historique ci-dessous reste à réviser : elle ne vaut pas décision d’ajouter un bilan ou un modèle IRT, piste écartée par l’utilisateur.

## Phase 1 — priorité immédiate (usage familial, sans contrainte réglementaire)

- [ ] Moteur adaptatif : règle ±1 palier, critères de maîtrise (90 % × 3 sessions), orchestration de séance, détection de fatigue
- [ ] FSRS pour les items déclaratifs
- [ ] Module Entraînement : calcul mental/tables → anglais → Python
- [ ] Module Rééducation (usage familial) avec garde-fous actifs
- [ ] Relectures informelles de l'orthophoniste au fil de l'eau

**Critères de sortie** : un cycle complet de calcul mental jouable de bout en bout, garde-fous vérifiés par tests, première relecture de contenu réalisée.

## Phase 2 — bilan structuré (toujours en usage familial)

- [ ] Batterie 15–20 min fractionnable (attention soutenue, divisée, mémoire de travail, flexibilité, inhibition, vitesse de traitement)
- [ ] Trajectoire personnelle ; bilan de suivi automatique toutes les 2 semaines
- [ ] Export PDF + JSON (désidentifié par défaut)
- [ ] Calibration des épreuves avec un neuropsychologue

## Phase 3 — DM classe I autodéclarée (différée, conditionnelle)

- [ ] Décision go/no-go selon la demande professionnelle constatée
- [ ] QMS allégé ISO 13485, ISO 14971, documentation technique
- [ ] Hébergement HDS le cas échéant

Chantier administratif **distinct des sprints produit** — ne pas mélanger.

## Phase 4 — boucle longitudinale

- [ ] Migration règle adaptative → IRT (quand les données le justifient)
- [ ] Ajustements de dosage sur données réelles
- [ ] Cap de difficulté adaptative réévalué (objectif « au-delà de la moyenne sans mettre la barre trop haut »)

## Backlog — nouvelles épreuves cognitives à prototyper

> Ces éléments relèvent du futur module **évaluation/bilan** et non du module de remédiation, conformément aux garde-fous du dépôt. Ils constituent des pistes de prototype et ne doivent pas être présentés comme des tests standardisés ou diagnostiques sans validation clinique et métrologique.

### Attention différée avec questions de culture générale

- [ ] Créer une épreuve d’attention/mémoire de travail fondée sur des questions de culture générale.
- [ ] Énoncer une question, recueillir ou laisser préparer la réponse, puis énoncer la question suivante **avant** de révéler la bonne réponse à la question précédente.
- [ ] Permettre plusieurs niveaux de difficulté et des délais/interférences variables.
- [ ] Prévoir des modalités écrite, orale et mixte.
- [ ] Mesurer : bonnes réponses, erreurs, omissions et temps de réponse.

### Mémoire visuospatiale — reproduction de figures

- [ ] Afficher pendant une durée paramétrable une figure géométrique relativement complexe composée de plusieurs formes imbriquées.
- [ ] Masquer ensuite complètement le modèle.
- [ ] Permettre à l’utilisateur de reconstruire la figure de mémoire.
- [ ] Prévoir deux modes : dessin libre et reconstruction à partir d’une palette de formes.
- [ ] Faire varier la complexité : nombre de formes, intersections, symétrie/asymétrie, orientation, position relative et détails.
- [ ] Conserver la reproduction pour comparaison avec le modèle.
- [ ] Étudier un scoring automatique portant sur les éléments présents/oubliés/ajoutés, leur position, orientation, proportions, intersections et la similarité globale.

### Série couleur 1 — lecture rapide de noms de couleurs

- [ ] Générer une liste aléatoire de 50 noms de couleurs simples, affichés en noir.
- [ ] Demander de lire à voix haute le plus grand nombre de mots possible en 45 secondes.
- [ ] Reboucler automatiquement sur la liste de 50 jusqu’à la fin du temps.
- [ ] Compter le nombre d’items parcourus, les réponses correctes, erreurs et omissions.
- [ ] Calculer le débit de réponses correctes par minute.
- [ ] Si la reconnaissance vocale est utilisée, conserver la transcription et permettre une correction manuelle des erreurs de reconnaissance.

### Série couleur 2 — dénomination rapide de carrés colorés

- [ ] Afficher une liste de 50 carrés de couleurs simples.
- [ ] Demander de nommer oralement leur couleur le plus rapidement possible pendant 45 secondes.
- [ ] Reboucler sur les 50 stimuli jusqu’à la fin du temps.
- [ ] Utiliser le même vocabulaire de couleurs que dans l’épreuve de lecture.
- [ ] Compter items parcourus, réponses correctes, erreurs, omissions et débit correct par minute.

### Série couleur 3 — interférence couleur-mot de type Stroop

- [ ] Afficher 50 noms de couleurs dont la couleur typographique ne correspond pas au mot écrit.
- [ ] Demander de **nommer la couleur des caractères**, sans lire le mot.
- [ ] Faire durer l’épreuve 45 secondes et reboucler sur les 50 stimuli.
- [ ] Compter items parcourus, réponses correctes, erreurs, omissions et corrections spontanées.
- [ ] Calculer le débit correct par minute.

### Comparaison des trois épreuves de couleurs

- [ ] Regrouper les trois épreuves dans une même session optionnelle.
- [ ] Produire un tableau comparatif : items traités, bonnes réponses, erreurs, omissions, précision et débit correct par minute.
- [ ] Calculer des écarts de vitesse entre lecture, dénomination simple et condition d’interférence.
- [ ] Étudier un indicateur de coût d’interférence, sans le présenter comme un diagnostic ni une norme populationnelle.

### Infrastructure commune de mesure

- [ ] Enregistrer pour chaque épreuve : date/heure, durée, niveau, nombre de stimuli, réponses, bonnes réponses, erreurs, omissions et temps de réaction lorsque mesurable.
- [ ] Conserver la distinction entre **performance brute**, **précision** et **vitesse de traitement**.
- [ ] Prévoir un mode entraînement avec feedback et un mode évaluation sans feedback pendant l’épreuve.
- [ ] Rendre configurables durées, tailles de listes, délais de présentation, difficultés et modalités audio/visuelles.
- [ ] Afficher une évolution strictement intra-individuelle (séances précédentes, tendances personnelles) sans comparaison normative.
- [ ] Étudier une difficulté adaptative pour les prototypes d’entraînement, mais ne pas modifier automatiquement une épreuve destinée à être comparable dans le temps sans décision clinique explicite.

### Pistes complémentaires

- [ ] Étudier un N-back visuel/auditif uniquement dans le périmètre évaluation/bilan.
- [ ] Étudier une tâche de double attention.
- [ ] Étudier une tâche de mémoire de séquences spatiales inspirée des blocs de Corsi.
- [ ] Étudier une tâche de recherche visuelle avec distracteurs.
- [ ] Avant implémentation de ces épreuves, formaliser leur place produit et leurs règles de mesure dans un ADR, puis prévoir une revue clinique/métrologique.

