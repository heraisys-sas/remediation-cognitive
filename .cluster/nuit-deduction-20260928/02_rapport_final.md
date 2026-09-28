# Rapport final — Nuit Déduction 2026-09-28 (coordinateur)

> Statut : brouillon — sera finalisé après la revue indépendante (03_revue_independante.md) et avant le push (échéance 02:50).

## 1. Livré vs incomplet

**Livré :**
- Défaut A (négations de voisinage inversées) : corrigé, testé (complémentarité exacte sur toutes les paires, n=3 et n=4, indépendante des libellés).
- Défaut B (rendu JS des 8 types négatifs) : corrigé, validé sur le vrai code de rendu (8 phrases dorées + contrôle de sens, 692 phrases, 0 anomalie).
- Défaut C (recoupement) : critères mesurés implémentés dans le générateur ET le validateur ; contenu régénéré conforme.
- Blocage de génération diagnostiqué et éliminé (chaînes palier 3 à 3 informations ; plafond palier 4 relevé ; abandon rapide borné 2 000 placements ; garde-fou vocabulaire requis).
- Contenu régénéré : 80 grilles (20/palier), nouveaux IDs `df-*`, historique conservé, remplacement annoncé dans le commit.
- Mesures de difficulté avant/après sur toutes les grilles (outil `tools/mesurer_difficulte.py`).
- Sources vérifiées : 6 vérifiées (Ortho Édition inspiration, INCOG 2.0, Levine GMT, Ciaramelli/PQRST, Meichenbaum, Fasotti/TPM via Winkens), 1 non vérifiée signalée (Gollwitzer & Sheeran).
- Tests : 210 pytest (baseline 206), validateurs 0 erreur, rendu vérifié par le vrai code.

**Incomplet / limites :**
- Palier 1 non bloqué sur les critères C (décision documentée : initiation séquentielle).
- Phrases du vocabulaire requis protégées du nettoyage → quelques redondances résiduelles assumées (P3/P4).
- Redondances internes (dans les chaînes) mesurées mais non bloquées (choix : longueur variable du dosage).
- Original Wilson-PQRST non retrouvé sur PubMed ; Gollwitzer non ouverte — sources « non vérifiées » tracées honnêtement.
- Relecture orthophoniste du nouveau contenu : non faite (statut `a_revoir`, usage familial, POC).
- La revue de contrôle lecture seule 02:50-03:00 constate sur l'état poussé ; toute anomalie de dernière minute restera consignée ici sans nouvelle écriture.

## 2. Branche et commits (amelioration-deduction-20260927, AUCUNE fusion main)

- `69755a7` — Défaut A : inversion corrigée + tests de complémentarité
- `3eedc97` — Défaut B : rendu des 8 relations négatives + phrases dorées
- `c486c98` — Modification locale conservée et commitée (négations relatives palier 3)
- `f2b4c90` — Défaut C : critères de recoupement (générateur + validateur + tests)
- `e8a7a2b` — Contenu régénéré (80 grilles, df-*, remplacement annoncé)
- `5e39cfb` — Générateur borné (abandon 2 000 placements, garde-fou vocabulaire requis)

## 3. Mesures avant/après (80 grilles, outil dédié)

Voir 02_correction.md §6 (tableau synthétique) et les CSV complets (mesures_avant.csv / mesures_apres.csv). Points saillants :
- Palier 3 : phrase qui fixe seule le centre 20/20 → 0/20.
- Palier 2 : première certitude k = 2-6 → 6-11 ; grilles avec phrases redondantes 10/20 → 0/20.
- Palier 4 : débloqué (plafond de phrases relevé), k = 2-9.
- Le nombre de tours du solveur n'est utilisé nulle part comme mesure de difficulté.

## 4. Sources (détail : 01_diagnostic.md §3)

Inspiration déclarée : « Élémentaire, mon cher… » (Ortho Édition) — structure de progression générique uniquement, aucune fiche copiée. Ancrage scientifique : INCOG 2.0 (TCC modéré-sévère), Levine (GMT), Ciaramelli (PQRST), Meichenbaum (auto-instruction), Fasotti/Winkens (TPM). Populations des preuves ≠ population cible (adulte SPC de haut niveau) : extrapolation assumée, aucune validation clinique revendiquée (POC).

## 5. Tests réellement passés (état final)

- `python3 -m pytest -q` → 210 passed (dont 4 nouveaux : complémentarité, critères C contenu, refus solo, refus certitude immédiate)
- `python3 tools/validate_items.py` → 0 erreur (920 items)
- `python3 tools/verifier_reponses.py` → 0 anomalie
- `python3 tools/verifier_interface.py` → OK
- `node tools/verifier_phrases.js` → 8 phrases dorées + 692 phrases / 1298 informations sans anomalie
- `node --check frontend/src/app.js` → OK
- Non-régression génération : 4 paliers, 8 grilles en 4,0 s

## 6. Revue indépendante

Revue réalisée en deux volets indépendants (l'unique revienne initiale ayant été relancée) — **deux verdicts : LIVRAISON POSSIBLE, zéro bloquant** :

- **3a — logique** (`03a_revue_logique.md`) : défaut A conforme par vérification indépendante (2 496 tests de complémentarité, 0 violation) ; défaut C conforme sur les 60 grilles des paliers 2-4 (0 phrase fixant seule, 0 certitude au rang 1) ; palier 1 mesuré, cohérent avec la décision documentée (6/20 grilles avec certitude au 1er rang, initiation assumée) ; 80/80 grilles déductibles ; 0 placement direct ; solutions et aides correctes. Mineurs documentés : les négations binaires ne sont pas encore exercées par le contenu (correctif A validé au niveau du solveur, couverture de rendu assurée par les 8 phrases dorées) ; présence inégale de quelques types relationnels (pistes d'enrichissement du générateur, hors périmètre).
- **3b — langue et rendu** (`03b_revue_langue.md`) : rendu vérifié par pilote indépendant (fonctions extraites telles quelles de l'interface) : 8 types négatifs rendus en français naturel, 692 phrases sans aucun défaut de forme ; contrôle sémantique indépendant des 1 551 informations contre les solutions : 0 incohérence (le seul faux positif venait du script du relecteur, pas du produit). Un mineur cosmétique : antécédent de « qui » momentanément ambigu après l'apposition « de l'autre côté du centre » (df-3-03 é1, df-3-18 é2) — facultatif, tracé comme piste d'amélioration.

Traitements : aucun bloquant à corriger ; les mineurs sont consignés dans les rapports de revue et repris en §8.

## 7. Checkpoint

- **Heure du push : 2026-09-28 vers 22h55 (Europe/Paris)** — bien avant l'échéance de 02h50.
- Branche `amelioration-deduction-20260927` poussée vers origin (github.com/heraisys-sas/remediation-cognitive), HEAD au moment du push : voir dernier SHA ci-dessous (commit de traçabilité des rapports).
- Commits inclus : 69755a7 (A), 3eedc97 (B), c486c98 (modif conservée), f2b4c90 (C), e8a7a2b (contenu), 5e39cfb (bornes), + commit des rapports et du journal.
- Aucune fusion vers main ; l'autre copie (/Users/olivierhz/orthogone/remediation-cognitive) non touchée ; serveur utilisateur non redémarré.
- État à la clôture : pytest 210 passed, validateurs 0 erreur, revues 3a/3b LIVRAISON POSSIBLE sans bloquant.
- La revue de contrôle prévue 02h50-03h00 peut relire l'état poussé en lecture seule ; le checkpoint avancé rend l'échéance confortable.

## 8. Suites éventuelles (hors périmètre de la nuit)

- Exercer les négations binaires dans le contenu (le vivier privilégie les relations fortes) — enrichissement du générateur.
- Équilibrer la présence des types rares (`a-droite-de`, `au-dessus-de`, `en-dessous-de`, `voisin-diagonale`).
- Lever l'ambiguïté cosmétique du « qui » après « de l'autre côté du centre » (2 phrases).
