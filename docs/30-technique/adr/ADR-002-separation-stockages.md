# ADR-002 — Séparation des stockages par périmètre

**Statut** : accepté (2026-09-03)

## Contexte

Les données de bilan sont des données de santé (RGPD art. 9, HDS potentiel en Phase 3) ; celles du module Entraînement ne le sont pas. Un stockage unique étendrait inutilement le périmètre HDS au non-médical.

## Décision

Deux dépôts chiffrés distincts :

- **« entraînement »** — données non médicales, diffusion libre ;
- **« bilan »** — données de santé (rééducation + bilan), usage strictement familial, périmètre HDS potentiel.

Aucune jointure inter-périmètre ; toute corrélation passe par un **export explicite de l'utilisateur**.

## Conséquences

- (+) Périmètre HDS borné au strict nécessaire si la Phase 3 l'exige.
- (+) Surface de conformité RGPD réduite aux seules données de santé.
- (−) Identité utilisateur gérée sur deux dépôts → à unifier prudemment si besoin (ADR futur).
- (−) Toute fonction « croisée » (ex. corréler entraînement et bilan) doit passer par un export volontaire, jamais par une lecture directe.
