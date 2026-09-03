# Spécification — Moteur adaptatif commun

## Périmètre

Un **seul moteur** (`engine/`), réutilisé par les trois modules (rééducation, entraînement, bilan de suivi). Sans dépendance au backend. Voir ADR-001.

## Règle adaptative (v1)

- Ajustement **±1 palier** selon le taux de réussite glissant (fenêtre paramétrable).
- Critère de maîtrise avant progression : **90 % de réussite sur 3 sessions consécutives**.
- Interface prête pour une migration IRT (Phase 4) — l'IRT est plus robuste mais plus lourde à calibrer sans base d'items normée ; on commence simple.

## Répétition espacée

- **FSRS** pour tous les items déclaratifs (tables, vocabulaire, commandes Python).
- Items ordonnancés par deck ; **interleaving activable par phase** (désactivé en phase aiguë post-SPC : bloquer et simplifier).

## Session

- Orchestration 5–10 min ; limite de sessions/jour paramétrable.
- **Détection de fatigue** : dégradation du RT et montée du taux d'erreur → proposition d'arrêt (jamais forcée).
- Journal de charge perçue en fin de session (1 item auto-rapporté).
- Enregistrement : essais, RT, erreurs, charge perçue — chiffré au repos.

## Garde-fous (codés en dur, non contournables par l'UI)

1. **Détection de dégradation** (RT en hausse, erreurs en hausse) → interruption proposée, jamais forcée, mise en avant.
2. **Cap de difficulté** configurable avec justification pédagogique explicite.
3. **Séparation stricte des vocabulaires** bilan (clinique, disclaimers) vs entraînement (neutre, ludique modéré) — centralisée dans `backend/app/domain/messages.py`.
4. **Aucune donnée de bilan** ne transite par un service tiers non-HDS.
