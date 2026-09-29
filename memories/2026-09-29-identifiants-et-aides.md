# 2026-09-29 — Déduction : identifiants dérivés du contenu + aides harmonisées

Deuxième passe du brief correction (demandée après validation Codex du matin). Dépôt `deduction-corrections`, branche `amelioration-deduction-20260927`, base `adbabd9`.

- **Défaut reproduit** : `generer_palier(1, random.Random(GRAINE), 1, set())[0]` donnait `df-1-01` avec des énoncés différents du `df-1-01` livré — identifiant positionnel réutilisé à contenu changé (violation du « contenu versionné » §2, remplacement silencieux).
- **Correction** : `identifiant_item` = `df-<palier>-<empreinte sha256 12 hex>` du contenu canonique (contenu + réponse ; date/auteur/id exclus) ; garde-fou anti-collision à la génération ; `_item` ne prend plus de rang positionnel.
- **Aides** : 47 items (P2 20 + P3 7 + P4 20) → `AIDE_CROISEMENT` ; énoncés/solutions/indices/consignes intacts (assertions du script) ; nouveaux IDs ; mapping `.cluster/correction-deduction-20260929/mapping_aides_anciens_nouveaux.md` ; contrôle validateur + test sur le corpus avancé ; le palier 1 garde l'aide d'ancrage (décision documentée).
- **Pièges** : ne pas confondre « identifiant stable » et « compteur » ; le contenu canonique inclut tout le pédagogique (l'ordre des phrases compte) ; tests locaux 218 passed, 0 skipped — Codex voit 1 test ignoré (`test_correction_sens.py`, empreintes système absentes) qui passe ici.
- Aucun travail sur les redondances (demande explicite).
