# ADR-001 — Moteur adaptatif unique

**Statut** : accepté (2026-09-03)

## Contexte

Trois modules (entraînement, rééducation, bilan de suivi) partagent les mêmes besoins : paliers fins, maîtrise avant progression, dosage de séance, détection de fatigue, répétition espacée.

## Décision

Un **seul moteur** (`engine/`), réutilisé par les trois modules. Le contenu est traité comme des données (`content/`), pas comme du code. Règle adaptative simple (±1 palier) en v1, avec interface prête pour une migration IRT en Phase 4.

## Conséquences

- (+) Garde-fous implémentés et testés **une seule fois**, pour les trois modules.
- (+) Cohérence de dosage entre modules.
- (+) Le module Entraînement sert de banc d'essai avant la rééducation.
- (−) Couplage : toute évolution du moteur impacte les trois modules → **tests de non-régression obligatoires** sur `engine/tests/`.
- (−) La migration IRT devra recalibrer tous les decks simultanément.
