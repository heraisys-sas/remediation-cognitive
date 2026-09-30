# Mise à jour du 30 septembre — aides raisonnées et P2

- P2 : 6–8 phrases par grille, moyenne **7,25** contre 9,8. Sept regroupements à deux repères individuels du même pion ; aucune chaîne changeant de sujet. Première étape accompagnée par une méthode visible et, sur cinq grilles, un repère explicite de démarrage. La troisième étape retire les repères individuels.
- Cinq paliers : orientation vers les phrases numérotées, comparaison des possibilités, puis conclusion sur un troisième clic explicite. Les démonstrations proviennent des phrases affichées et de l’unicité des pions/cases ; les coordonnées aléatoires de secours sont retirées.
- Les intersections sont contrôlées et les démonstrations complexes sont rejouées étape par étape. Le repère pédagogique visible de P2 est distingué du noyau minimal ; ce dernier reste déductible sans aide.
- P1/P3/P4/P5 : énoncés et solutions identiques au commit précédent, vérifiés par comparaison. Les aides modifiées entraînent de nouveaux identifiants pour les 100 items ; P2 est régénéré.
- **240 tests réussis, 1 ignoré** (empreintes sémantiques système absentes). Unicité indépendante des 100 grilles, 940 items valides, 839 phrases et 19 références de rendu vérifiées. Syntaxe JS et cohérence interface : OK. Régénération identique vérifiée.
- Test de progression rendu indépendant du 29 septembre : cette date devenue passée faisait expirer artificiellement les sessions du test. Aucun changement du serveur pour contourner ce défaut de test.

Voir ADR-018. Le réglage pédagogique particulier des autres paliers reste à examiner en usage ; les aides communes ne constituent pas une calibration clinique.

---

# Livraison Codex — 29 septembre 2026, session du soir

Implémentation directe sur `amelioration-deduction-20260927`, base `7400534`, après les échecs AutoClaw. Cette livraison remplace les observations de corpus de 80 grilles dans les comptes rendus historiques ci-dessous.

## Résultat

100 nouveaux items, 20 par palier, 3 étapes (7/7/6). P4 est désormais le 3×3 avancé, P5 le 4×4. Exclusions collectives, répartition, diversité, entre-deux et références partielles présents dans le contenu effectivement servi. Les contraintes collectives restent des indices explicites propres à chaque grille.

| Palier | Phrases moyennes | Phrases fixant seules une case | Informations retirables par propagation |
|---|---:|---:|---:|
| 1 | 4,5 | 3 au total (initiation autorisée) | 0 |
| 2 | 9,8 | 0 | 0 |
| 3 | 7,7 | 0 | 0 |
| 4 | 7,6 | 0 | 0 |
| 5 | 14,9 | 0 | 0 |

Le nombre de phrases n'est pas une mesure de difficulté. Les paliers changent les familles, les références et le guidage ; leur difficulté cognitive n'est pas étalonnée. Une information nécessaire à la preuve par propagation n'est pas forcément indispensable à l'unicité : les deux propriétés sont contrôlées séparément.

## Vérifications

- Propagation sans hypothèse : les 100 grilles résolues ; chaque information conservée est nécessaire à cette preuve, test de retrait effectué sur tout le corpus.
- Recherche MRV indépendante du propagateur : 100 solutions uniques identiques aux réponses, 193 945 nœuds au total. Budget explicite, échec si dépassé ; tests d'ambiguïté et de contradiction.
- 2 160 affectations comparées à un oracle indépendant pour les contraintes riches. Régression : un compte impossible « deux cercles dans chaque ligne » est refusé, aucune distribution latine implicite.
- Rendu réel JS : 19 phrases de référence, 890 phrases du corpus sans anomalie ; corrections des enchaînements négatif/positif et du contrôle d'atomes conservant auparavant le `et` du parent.
- `validate_items.py` : 940 items, 0 erreur ; `verifier_reponses.py` : 0 anomalie (l'unicité déduction relève du nouvel outil séparé) ; `verifier_interface.py` et syntaxe JS : OK.
- `pytest` avec Node sur PATH : 237 passed, 1 skipped. Le test ignoré concerne les empreintes sémantiques Apple indisponibles dans cet environnement ; aucun test de déduction n'est ignoré.
- Régénération complète dans un dossier temporaire : contenu des cinq fichiers identique octet pour octet.
- Progression testée avec des révisions dues et un ancien historique parfait : les dernières étapes deviennent accessibles ; les anciens scores ne valident pas les nouvelles étapes ; le palier ne recule pas.

Documentation : ADR-017 et README du thème. Nouveaux contenus `a_revoir`. Publication limitée à la branche d'essai ; main, le serveur actif et l'autre checkout n'ont pas été modifiés.

---

# Rapports historiques (avant cette refonte)

# CORRECTION_REPORT — Déduction : preuve exacte du « fixe seule » et réparation du palier 3

**Date** : 2026-09-29 · **Dépôt** : `/Users/olivierhz/orthogone/deduction-corrections` · **Branche** : `amelioration-deduction-20260927` · **Base** : `895efdf` · **Commits de la correction** : `8299f0b` (première passe), `d534e40` et `7f0ff8b` (deuxième passe : identifiants, aides, sélecteur de palier)

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

## Deuxième passe — même jour (identifiants + aides)

Corrections demandées après validation Codex du matin — le sélecteur de palier s'y est ajouté en complément prioritaire. Commits de cette passe : `d534e40` (identifiants + aides), `7f0ff8b` (sélecteur de palier).

### 1. Identifiants du générateur dérivés du contenu

Défaut reproduit : `generer_palier(1, random.Random(GRAINE), 1, set())[0]` produisait un `df-1-01` dont les énoncés diffèrent du `df-1-01` livré — identifiant positionnel réutilisé à contenu changé (remplacement silencieux). Désormais :

- `identifiant_item` = `df-<palier>-<empreinte>` où l'empreinte est un sha256 tronqué (12 hex) du contenu pédagogique canonique — consigne, figures, couleurs, énoncés, indices, aide, réponse ; **date, auteur et identifiant exclus** ;
- garanties testées : re-génération identique → identifiants identiques ; changement (phrase / aide / réponse) → identifiant différent ; date/auteur sans effet ; aucun recouvrement avec les identifiants positionnels `df-*`/`dc-*` ; un même identifiant n'est partagé que par un contenu identique ;
- collision d'empreinte en génération : échec bruyant (`SystemExit`) — jamais deux contenus sous un identifiant ;
- `_item` ne reçoit plus de rang positionnel ; aucune régénération des 80 grilles.

### 2. Aides harmonisées (47 items, paliers 2–4)

- Les 47 items portant encore « dont la phrase donne la position » (P2 20 + P3 7 + P4 20) passent à `AIDE_CROISEMENT`. Énoncés, solutions, indices et consignes **strictement préservés** (assertions du script) ; l'aide, la méta et l'identifiant changent — identifiant recalculé par empreinte. Correspondance complète : `.cluster/correction-deduction-20260929/mapping_aides_anciens_nouveaux.md` ;
- le palier 1 garde son texte d'ancrage (initiation) — décision documentée ;
- contrôles ajoutés : validateur du dépôt (`tools/validate_items.py`) + test dédié sur tout le corpus avancé.

### 3. Sélecteur de palier — le choix part au serveur

Défaut confirmé par Codex : en choisissant « Essai — palier 2 », le frontend démarrait la séance au palier courant (grille `df-1-01` servie). `demarrerSession` recevait le palier mais POSTait `…/sessions` sans corps.

- le palier choisi part dans le corps JSON (`{"palier": N}`, contrat `DemarrageOptionnel`) ; le mode **auto** reste sans corps (progression côté serveur, comportement inchangé) ; les réessais (réseau, bandeau) conservent le palier choisi ; version du script incrémentée (`app.js?v=20260929a`) ;
- contrôle effectif de la requête JS : `tools/verifier_session.js` exécute le **vrai** `demarrerSession` + `apiFetch` d'`app.js` sur un `fetch` simulé — palier 2 → POST avec corps et `Content-Type` ; auto → aucun corps ; réessai réseau → palier conservé ; branché dans pytest (Node requis, sinon ignoré et signalé) ;
- test d'API dédié au thème : palier 2 forcé → tous les items servis sont du palier 2 ; sans corps → palier 1 (état vierge) ; palier inconnu → 422 ; filtrage serveur (`selectionner_items`) revérifié strict par palier ;
- robustesse au passage : le scanner d'extraction de `verifier_session.js` gère les commentaires français (apostrophes) — sinon un bloc déborde silencieusement.

### Contrôles de cette passe

- `python3 -m pytest -q` → **220 passed, 0 skipped** sur ce poste (dont les 2 contrôles ajoutés pour le sélecteur). Codex signalait 215 passed + 1 skipped (empreintes système absentes) : le test concerné (`backend/tests/test_correction_sens.py`, empreintes sémantiques locales) s'exécute et passe ici — même suite, même contenu.
- `validate_items` → 0 erreur (920 items, contrôle des aides inclus) ; `verifier_reponses` → 0 anomalie (920 identifiants uniques) ; `verifier_interface` → OK.
- Node : 8 phrases dorées + 687 phrases / 1269 informations, 0 anomalie ; `node tools/verifier_session.js` → 3 contrôles (palier 2, auto, réessai) ; `node --check frontend/src/app.js` → OK.
- Générateur (essai borné) : 32 grilles conformes (0 solo, 0 rang-1, déterminées, ≥ 4 phrases, verrou pédagogique respecté).
- Aides : 60/60 en « croisement » aux paliers 2–4 ; 20/20 en « ancrage » au palier 1.
- Aucun travail sur les redondances dans cette passe (demande explicite).

## Suites (pour Codex)

- Relecture orthophoniste du contenu : statut inchangé (`a_revoir`).
- Quatre grilles à phrase retirable résiduelle (plancher ≥ 4) : accepter ou re-générer ces quatre contenus.
- Palier 4 : arbitrer un nettoyage des redondances mesurées (hors défaut C).
- Négations binaires toujours peu exercées (piste d'enrichissement déjà tracée).
