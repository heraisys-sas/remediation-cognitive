# 2026-09-15 — Enrichissement « mémoire & concentration » (sprint 2)

## Demande

Améliorer le logiciel avec des entraînements issus des techniques établies — neuropsychologie américaine (calcul sériel type PASAT, filtrage type d2, empan, n-back) et orthophonie française (apprentissage par paires, remédiation mnésique). Logique assimilée, matériel protégé non copié (ECPA/Pearson).

## Livré

- 2 thèmes, 306 items générés de façon déterministe (graine 20260904) : `memoire` 8 paliers × 18 (empan 3→6, paires 2→4, n-back 2→4), `concentration` 9 paliers × 18 (chaînes 3→7 opérations, cascades, double tâche 5→9, séries).
- Backend : `_SOURCES_PAR_THEME` +2, correction `memoire` (sans espaces/casse) et `concentration` (numérique), labels vocabulaires.
- Interface : phase de mémorisation (`zone-memo`, `afficherPhaseMemo`/`jouerAffichage`/`afficherQuestion`, `annulerMemo` sur tous les changements d'écran), styles sans déplacement (min-height réservés).
- Validateur multi-thèmes (cohérence calcul gated sur calcul-mental, `table` interdit hors calcul-mental, motif prerequis générique `^[a-z]+-palier-\d+$`).
- Tests : 99 passed (3 nouveaux). Validateur : 31 fichiers / 497 items / 0 erreur.
- Docs : fondements, protocoles (fatigue progressive dans le contenu), taxonomie, module-entraînement, contrat API (affichage temporisé + honnêteté stimulus).

## Pièges & apprentissages

- IDs générés sans zéro de padding sur le palier (`me-1-empan-01`, pas `me-01-…`) — cohérent avec le validateur (motif libre hors calcul-mental), mais garder en tête si on resserre les motifs un jour.
- Les manifests non calcul-mental n'ont pas de champ `table` — le validateur l'interdit désormais hors calcul-mental.
- Le temps de mémorisation est exclu de `temps_ms` : `etat.debutQuestion` n'est pris que quand la question s'affiche. `annulerMemo()` doit être appelé partout où l'on quitte l'écran (montrerItem, revenirAuxThemes, finirSeance) sous peine de timers zombies.
- Les sous-agents relancés (contenu + interface) ont fini par livrer : leurs diffs ont été intégrés tels quels (revue ligne à ligne), seuls les styles `.memo-*` manquaient — ajoutés à la main.
- `.cluster/enrichissement/spec.md` est hors du dépôt (racine workspace) — la spécification détaillée des paliers reste la référence si régénération.

## Reste à faire

- Relecture ortho/clinique `a_revoir` sur les 306 items.
- Errorless d'entrée de palier + prerequis anglais/Python (reportés).
- ADR-003 (React+Vite), requirements.txt, README dev.
