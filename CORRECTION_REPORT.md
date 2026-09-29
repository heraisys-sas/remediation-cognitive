# CORRECTION_REPORT — Déduction : preuve exacte du « fixe seule » et réparation du palier 3

**Date** : 2026-09-29 · **Dépôt** : `/Users/olivierhz/orthogone/deduction-corrections` · **Branche** : `amelioration-deduction-20260927` · **Base** : `895efdf` · **Commit de la correction** : `8299f0b`

Reprise rapide pour Codex : ce qui a été fait, les nombres réellement mesurés, les limites.

## Cadre

- Brief « correction Déduction » exécuté via AutoClaw, chat unique, **modèle réellement utilisé : glm-5.3 (identité runtime `zai/zaicoding_glm-5.3`)** — aucun sous-agent.
- `origin` corrigé avant tout push : `https://github.com/heraisys-sas/remediation-cognitive.git` (il pointait initialement vers un checkout local). Aucune fusion main, aucun force push, aucun redémarrage serveur.
- Les deux fichiers de l'ébauche Codex (`tools/deduction_commun.py`, `tools/mesurer_difficulte.py`) ont été relus, durcis (vocabulaire cité vérifié — un jeton inconnu échoue bruyamment) et conservés.

## Défauts traités

1. **Faux « zéro solo » au palier 3.** La propagation à sens unique (sans unicité des cases) ne voyait pas les chaînes « diagonale + opposé + comparaison ». Correction : preuve exacte par énumération exhaustive des jetons cités (`lru_cache`, budget 100 000 nœuds, `ValueError` si dépassé), propagation binaire bidirectionnelle, unicité, vocabulaire vérifié. Reproduction : ex-df-3-03 première phrase → triangle rouge case 8, cercle bleu case 0.
2. **« k » trompeur.** Renommé `rang_lecture` (ordre présenté ≠ minimum logique) ; `support_propage` = borne supérieure (lots 1..3). Documentation corrigée : palier 1 **non séquentiel** (mélangé), palier 4 sans « moins de phrases » (paliers.json, générateur, README).
3. **Redondances internes fausses.** Copies sans `et`, retrait réel de chaque atome (ancre comprise), aucune mutation ; tests dédiés.

## Contenu réparé (13 grilles, IDs remplacés)

`df-3-03→dc-3-03, df-3-04→dc-3-04, df-3-05→dc-3-05, df-3-07→dc-3-07, df-3-09→dc-3-09, df-3-11→dc-3-11, df-3-12→dc-3-12, df-3-13→dc-3-13, df-3-15→dc-3-15, df-3-16→dc-3-16, df-3-17→dc-3-17, df-3-18→dc-3-18, df-3-20→dc-3-20` — autres IDs inchangés ; les df-3-* remplacés ne seront pas réutilisés.

Méthode : chaque phrase solo [ancre + opposé + comparaison] est scindée en **deux chaînes de deux informations** partageant le maillon central (`[ancre + opposé]` / `[opposé + comparaison]`) — le verrou pédagogique du validateur (≥ 2 informations + une relation binaire par phrase) est respecté et le croisement entre phrases restitue la déduction. Doublons exacts retirés ; chaînes scindées devenues redondantes retirées (vocabulaire `oppose`/`comparaison` protégé, plancher 4). Script rejouable : `.cluster/correction-deduction-20260929/scinder_phrases_solo.py`.

## Nombres réellement mesurés (outil exact, 80 grilles)

| Mesure | Avant (contenu `895efdf`) | Après |
|---|---|---|
| Palier 3 — phrases solo | **19** (13 grilles / 20) | **0** |
| Palier 3 — rang de lecture | 1–3 | 2–4 |
| Palier 3 — redondances entre phrases | 16 | 9 (dont 4 plancher-bloquées : 1 par grille sur dc-3-12, 16, 17, 20) |
| Palier 3 — redondances internes | 229 | 171 |
| Paliers 2 et 4 | 0 solo | inchangés |

Vérification indépendante (énumération brute 9!) : **1 solution unique par grille réparée, égale à la stockée** ; phrases indispensables : 9 grilles 4/4, 4 grilles 3/4 (plancher ≥ 4 du validateur).

Observation hors périmètre : palier 4, redondances entre phrases 122 (≈ 6/grille) — pré-existantes, visibles depuis la propagation corrigée.

## Contrôles passés

- `python3 -m pytest -q` → **216 passed** (+6 tests : repro df-3-03, scission inoffensive, propagation inverse + unicité, retrait réel + ancre + non-mutation, rang vs support, zéro solo paliers 2–4 par énumération indépendante).
- `python3 tools/validate_items.py` → 0 erreur (920 items) ; `verifier_reponses.py` → 0 anomalie ; `verifier_interface.py` → OK.
- `node tools/verifier_phrases.js` → 8 phrases dorées + 687 phrases / 1269 informations, 0 anomalie ; `node --check frontend/src/app.js` → OK.
- Générateur (essai borné) : 8 grilles en ≈ 2,5 s ; 32 grilles générées vérifiées conformes (0 solo, 0 rang-1, déterminées, ≥ 4 phrases, ≥ 2 informations + relation par phrase).

## Suites (pour Codex)

- Relecture orthophoniste du contenu : statut inchangé (`a_revoir`).
- Quatre grilles à phrase retirable résiduelle (plancher ≥ 4) : accepter ou re-générer ces quatre contenus.
- Palier 4 : arbitrer un nettoyage des redondances mesurées (hors défaut C).
- Négations binaires toujours peu exercées (piste d'enrichissement déjà tracée).
