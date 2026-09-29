# 2026-09-29 — Correction déduction : preuve exacte du « fixe seule », palier 3 réparé

Suite du brief « correction Déduction » (modèle réellement utilisé : glm-5.3, identité runtime `zai/zaicoding_glm-5.3`, chat unique AutoClaw, aucun sous-agent). Dépôt `deduction-corrections`, branche `amelioration-deduction-20260927`, base `895efdf`.

- **Défaut C réel** : la détection par propagation à sens unique rendait un faux « zéro solo » au palier 3. Énumération exhaustive : 19 phrases fautives dans 13 grilles/20 (chaînes diagonale + opposé + comparaison qui fixent 2 jetons).
- **Corrections** : preuve exacte par énumération injective (cache + budget + erreur explicite) ; propagation binaire bidirectionnelle avec unicité ; `rang_lecture` et `support_propage` (borne) ; redondances internes réellement retirées, ancre testée, sans mutation.
- **Contenu** : 13 grilles scindées en chaînes de deux informations (mêmes solutions — vérifiées par énumération brute 9!) ; doublons et chaînes redondantes retirés ; IDs remplacés df-3-XX → dc-3-XX ; autres IDs inchangés.
- **Générateur** : unaires retirés des relations P3 ; plancher minimaliser 3→4 (bug latent : le validateur exige ≥ 4 phrases) ; aide par palier ; descriptions corrigées. Essai borné : 32 grilles conformes.
- **Contrôles** : pytest 216 ; validateurs 0 erreur ; Node 8 dorées + 687 phrases / 1269 infos sans anomalie ; app.js OK.
- **Pièges/leçons** : le verrou pédagogique du validateur (≥ 2 informations + une relation par phrase) a imposé la scission « en deux chaînes » plutôt qu'en atomes seuls. Élimination : dans une grille toute-pinnée, retirer l'info d'un jeton laisse la grille déterminée (dernière case) — les scénarios de test doivent en tenir compte. `timeout` absent sur macOS (utiliser le budget des outils). Vérifier l'indentation des JSON avant réécriture (paliers.json = 2 espaces).
- **Traçabilité** : `.cluster/correction-deduction-20260929/` (script de scission, audits, mesures avant/après) ; ADR-016 ; CORRECTION_REPORT.md à la racine ; addendum dans `.cluster/nuit-deduction-20260928/` (le rapport `895efdf` est dépassé sur C).
