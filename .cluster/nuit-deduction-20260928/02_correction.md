# 02 — Correction (voie 2) : défauts A/B/C + génération — nuit 2026-09-28

État : **TERMINÉ** (parts génération et défauts ; sources dans 01_diagnostic.md).

## 1. Commits (branche amelioration-deduction-20260927, aucun push avant intégration)

- `69755a7` — Défaut A : `pas-voisin-dessus/dessous` nient leur propre positive (inversion corrigée) + tests de complémentarité (indépendants des libellés).
- `3eedc97` — Défaut B : rendu français des 8 relations négatives + 8 phrases dorées vérifiées sur le VRAI code de rendu (`verifier_phrases.js`).
- `c486c98` — Modification locale préservée puis commitée (palier 3 : 4 négations relatives — décision conservée, anti-grammaire-pure).
- `f2b4c90` — Défaut C : critères de recoupement mesurés (générateur + validateur + tests).
- `e8a7a2b` — Contenu régénéré : 80 grilles, nouveaux IDs `df-*`, remplacement annoncé.

## 2. Défaut A — corrigé et testé

- `tools/deduction_commun.py` : `pas-voisin-dessus = not (i2 == i1 + n)` ; `pas-voisin-dessous = not (i2 == i1 - n)`.
- Test : complémentarité EXACTE des 8 paires positif/négatif, n=3 ET n=4, toutes paires de cases distinctes, appariement déclaré explicitement (`PAIRES_POSITIVE_NEGATIVE` dans `backend/tests/test_deduction.py`) ; repro n=3 case0→case3 vérifiée.

## 3. Défaut B — corrigé et testé

- `frontend/src/app.js` (`relationAtome`) : les 8 types négatifs retournent leur formulation (« n'est pas juste au-dessus du … », « n'est pas plus à droite que le … ») au lieu d'une chaîne vide.
- `tools/verifier_phrases.js` : 8 phrases dorées exactes sur le vrai code de rendu + contrôle de sens par type sur tout le contenu. Résultat final : 692 phrases, 1298 informations, 0 anomalie.

## 4. Défaut C — corrigé, mesuré, verrouillé

Fonctions partagées (`deduction_commun.py`) : `phrases_qui_fixent_seules`, `rang_premiere_certitude`, `recoupement_suffisant`, `PALIERS_RECOUPMENT_BLOQUANT = {2,3,4}`.
- Générateur : bannissement des phrases-solo du vivier (y compris pour le vocabulaire requis) ; vérification k≥2 sur l'ordre PRÉSENTÉ ; plafond palier 4 relevé (8→18) sinon déductibilité 4×4 inatteignable ; palier 3 : chaînes à 3 informations (0 % → 100 % de réussite, cf. 01_diagnostic.md) ; `VOCABULAIRE_REQUIS` 2/3 aligné sur le productible (l'ancien était ignoré en silence) + garde-fou erreur si type requis absent du vivier.
- Validateur (`validate_items.py`) : contrôle « phrase fixe seule une position » + « première certitude d'une seule phrase » (appliqué même aux grilles non déductibles), 8 types négatifs admis dans `TYPES_INDICE_GRILLE`.
- Tests : 4 nouveaux (critères C sur contenu, refus solo, refus certitude immédiate, complémentarité) — **210 passés** (baseline 206).

Décisions documentées :
- Palier 1 : critères C mesurés SANS bloquer (initiation séquentielle ; l'ancien stock comportait déjà k=1-4 ; les solos y sont des ancres de ligne/colonne assumées).
- Les « phrases retirables » résiduelles (4-5 grilles P3/P4) sont les phrases du vocabulaire requis, protégées du nettoyage par conception (ADR-007) — assumé, listé dans mesures_apres.csv.

## 5. Génération

- Échantillon 3 grilles/palier validé avant stock complet (6,1 s).
- Stock complet : 80 grilles (20/palier), placements distincts 80/80, IDs `df-1-01`…`df-4-20`, graine 20260928, date_creation 2026-09-28.
- Paliers 1 conservés sur mesure (phrases 4, identiques) ; 2/3/4 régénérés avec la nouvelle grammaire.
- Ancien contenu archivé : `.cluster/nuit-deduction-20260928/contenu_avant/`.

## 6. Mesures avant/après (synthèse)

| Palier | phrases moy (avant→après) | k premier placement (avant→après) | solos (avant→après) | grilles avec redondance (avant→après) |
|---|---|---|---|---|
| 1 | 4,0 → 4,0 | 1-4 → 1-4 | 20 → 22* | 0 → 0 |
| 2 | 8,6 → 11,0 | 2-6 → **6-11** | 0 → 0 | 10 → **0** |
| 3 | 8,2 → 4,3 | 2-9 → 2-4 | **20 → 0** | 4 → 4** |
| 4 | 15,2 → 15,2 | 3-10 → 2-9 | 0 → 0 | 5 → 5** |

\* palier 1 non bloqué (décision documentée). \*\* vocabulaire requis protégé (conception ADR-007).
Le nombre de tours du solveur n'est utilisé nulle part comme mesure de difficulté.

## 7. Tests finaux (tous verts)

- `python3 -m pytest -q` : **210 passed**
- `python3 tools/validate_items.py` : 0 erreur (920 items)
- `python3 tools/verifier_reponses.py` : 0 anomalie
- `python3 tools/verifier_interface.py` : OK
- `node tools/verifier_phrases.js` : 692 phrases / 1298 informations, 0 anomalie (dont 8 dorées)
- `node --check frontend/src/app.js` : OK
- UI ciblée : rendu vérifié par le vrai code via `verifier_phrases.js` (harnais ADR-009) ; serveur utilisateur non touché.

## 8. Limites

- Le stock « avant » du palier 1 est conservé à l'identique (déjà conforme) : les grilles df-1-xx reprennent le même style séquentiel.
- Les redondances internes par phrase restent mesurées mais non bloquées (les chaînes à 3 informations contiennent par construction des informations partiellement redondantes) — choix assumé : la longueur variable des phrases fait partie du dosage.
- Pas de relecture orthophoniste du nouveau contenu (statut `a_revoir` conservé, usage familial).
