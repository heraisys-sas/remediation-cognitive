# AGENTS.md — Guide pour les agents (et humains) travaillant sur ce dépôt

> À lire avant toute modification. Ce fichier décrit le projet, les règles non négociables et les conventions. Les décisions structurantes sont dans `docs/30-technique/adr/`, la mémoire de travail dans `memories/`.

## Le projet en une minute

Logiciel de **bilan et rééducation cognitive** pour adultes avec syndrome post-commotionnel (SPC) :

- **Moteur adaptatif unique** (`engine/`) réutilisé par les trois modules — ADR-001.
- **Entraînement** (calcul mental/tables, anglais, Python) — hors MDR, diffusable librement.
- **Rééducation ciblée** — usage **strictement familial**.
- **Bilan** — données de santé (RGPD art. 9), usage **strictement familial**, export PDF/JSON vers un référent à l'initiative de l'utilisateur.
- Contenu = **données versionnées** dans `content/`, validées par `content/schema-item.json`, séparées du code.

Docs d'entrée : `docs/00-produit/vision.md`, `docs/00-produit/cadre-reglementaire.md`, `docs/00-produit/feuille-de-route.md`.

## État courant — sprint 6 livré (2026-09-23)

- **Jouable de bout en bout** : onze thèmes répartis en deux sections — **entraînement** (calcul mental, retrouver le mot dont SFA/PCA, vie sociale, au quotidien, méthodes, déduction) et **évaluation** (mémoire, concentration, rappel de séries, plafonnés à 1 séance/jour), plus Python/anglais en « Extra » ; et les écrans transverses (programme, missions & carnet, repères). Lancer `python3 -m uvicorn backend.app.main:app` puis ouvrir `/ui/`.
- **Principe clinique réaffirmé** : remédiation fonctionnelle plutôt qu'entraînement aux tests (ADR de fait : `docs/10-clinique/remediation.md`).

- **Implémenté** : `engine/` (moteur inchangé) ; `backend/` — `/api/entrainement`, `/api/social`, `/api/programme` (correction par thème, essais assistés, rappel libre au seuil, estimation par fourchette, plan du jour) ; `frontend/` (SPA vanilla : phase de mémorisation temporisée, séries de mots, compte à rebours, propositions cliquables, indices progressifs).
- **Contenu** : **813 items** + 8 missions + **programme de 8 semaines**, générés de façon déterministe (`tools/generer_memo_concentration.py`, `generer_evocation_social.py`, `generer_rappel_series.py`, `generer_quotidien.py`, `generer_deduction.py`, `generer_methodes.py`, `generer_programme.py`).
- **Tests** : 132 passed (`python3 -m pytest -q`). Contrôles : `tools/validate_items.py`, `tools/verifier_reponses.py`, `tools/verifier_interface.py`, `tools/verifier_clinique.py` (garde-fous cliniques automatisés).
- **Contrat d'API figé** : `docs/30-technique/api-contract.md` — toute modification = ADR. Décisions : ADR-004 (aides progressives, options, périmètre social), ADR-005 (empan de mots, rappel libre, rythme), ADR-006 (programme, progression non contrainte).
- **Garde-fou produit** : le programme propose un rythme — il ne mesure rien. Aucun taux d'observance ni de complétion ne doit être calculé (ADR-006).
- **Traçabilité** : `.cluster/sprint1/`, `.cluster/enrichissement/`, `.cluster/sprint3/`, `.cluster/sprint4/`, `.cluster/sprint5/` ; journaux `memories/2026-09-03-sprint-1.md`, `2026-09-15-…`, `2026-09-21-…`, `2026-09-22-empan-de-mots-et-rappel-de-series.md`, `2026-09-22-programme-de-8-semaines.md`, `2026-09-23-renforcer-le-clinique.md`, `2026-09-23-remediation-fonctionnelle.md`.

## Règles non négociables (garde-fous cliniques)

1. **Le dosage prime sur la difficulté** : séances 5–10 min, limites journalières, cap de difficulté avec justification pédagogique explicite.
2. **Aucune norme populationnelle affichée à l'utilisateur** ; jamais présenter un score comme un diagnostic.
3. **Séparation stricte des vocabulaires** : clinique (bilan) vs neutre/ludique (entraînement) — centralisée dans `backend/app/domain/messages.py`, ne pas construire de chaîne utilisateur ailleurs.
4. **Aucune donnée de bilan ne transite par un service tiers non-HDS.**
5. **Stockages séparés** entraînement vs bilan (ADR-002) — aucune jointure inter-périmètre.
6. **Environnement visuel calme** : dark mode par défaut, contrastes doux, zéro scintillement (photophobie SPC).
7. **Phase aiguë post-SPC : bloquer et simplifier** ; l'interleaving n'arrive qu'après un socle acquis.
8. Errorless en entrée de palier ; la détection de fatigue **propose** l'arrêt, jamais forcée.
9. **Remédiation, pas évaluation** : aucun nouvel exercice d'allure évaluative (empan, n-back, séries…) ; on travaille la fonction altérée dans des situations de vie avec des stratégies — `docs/10-clinique/remediation.md`. Les épreuves existantes seront déplacées vers une section « évaluation » quand le module bilan existera.

## Conventions

- **Langues** : documentation et contenu en français ; identifiants de code en anglais, docstrings/commentaires en français.
- **Contenu** : tout item passe par `content/schema-item.json` avant intégration ; relecture orthophoniste tracée dans `meta.relecture_ortho` — relecture **informelle**, jamais présenter comme une validation clinique.
- **Contenu généré** : tirages aléatoires **isolés par `thème:famille`** (jamais de générateur partagé), extension ajoutée en fin de famille, et **aucune régénération d'un contenu déjà servi** (remplacer les identifiants si un changement s'impose). Toute modification de contenu est annoncée dans le message de commit — règle complète : `docs/30-technique/contenu-versionne.md`.
- **Moteur** (`engine/`) : toute évolution exige des tests de non-régression dans `engine/tests/`.
- **Décisions structurantes** : nouvel ADR dans `docs/30-technique/adr/` (format : contexte / décision / conséquences).
- **Journal** : relectures dans `docs/10-clinique/relectures.md`, événements produit dans `CHANGELOG.md`.
- **Secrets** : jamais de clé ou donnée réelle dans le dépôt (`.gitignore` exclut `.env`, `data/`, clés) — les données de bilan chiffrées restent hors du dépôt.
- **Licence** : BSD-3-Clause — toute contribution intégrée au dépôt entre sous cette licence ; matériel protégé tiers interdit.

## Commandes

```bash
pip3 install -r <(printf 'fastapi\nuvicorn\nhttpx\npytest\nfsrs\npython-docx\n')  # dépendances actuelles (aucun requirements.txt encore)
python3 -m pytest -q                 # tous les tests (backend/tests + engine/tests)
python3 -m pytest -q engine/tests    # moteurs seuls
python3 -m uvicorn backend.app.main:app   # serveur de dev → /ui/ (interface) et /docs (API)
python3 tools/validate_items.py      # schéma, manifests, options, indices, rythme, séries
python3 tools/verifier_reponses.py   # réponses recalculées depuis l'énoncé
python3 tools/verifier_interface.py  # identifiants et réinitialisation du champ de saisie
python3 tools/verifier_clinique.py   # garde-fous cliniques (vocabulaire, photophobie, matériel protégé, relecture)
python3 tools/generer_memo_concentration.py --dry-run   # régénère mémoire/concentration
python3 tools/generer_evocation_social.py --dry-run     # régénère evocation/social + missions
python3 tools/generer_rappel_series.py --dry-run        # régénère rappel-series
python3 tools/generer_programme.py --dry-run             # régénère le programme de 8 semaines
python3 tools/generer_quotidien.py --dry-run             # régénère le thème « au quotidien »
python3 tools/generer_deduction.py --dry-run            # régénère le thème « déduction »
python3 tools/generer_methodes.py --dry-run             # régénère le thème « méthodes »
```

Dépendances effectives du sprint 1 : fastapi, uvicorn, httpx, pytest, fsrs (paquet officiel open-spaced-repetition). Un `requirements.txt`/lock est à produire au prochain sprint.

## Décisions ouvertes

- Quota journalier : 3 séances/jour **par thème** (jusqu'à 9/jour au total) — global ou par thème, à trancher (paramétrable dans `backend/app/domain/dosage.py`).
- Framework frontend — vanilla sans build au sprint 1 ; React+Vite quand l'UI se complexifiera (ADR-003 à formaliser).
- Gestion des clés de chiffrement — ADR à produire (le stockage JSON actuel n'est pas chiffré ; périmètre non médical uniquement).
- Mode errorless d'entrée de palier et prerequis anglais/Python complets — reportés (sprints 2, 3 et 4 ont livré les familles de mémoire, d'accès au mot et de rappel).
- Relecture orthographique et clinique des items générés (`meta.relecture_ortho` = `a_revoir`) et des 8 missions avant diffusion au-delà de l'usage familial.
- Carnet des missions : mono-utilisateur, aucune donnée de séance n'y transite — à confirmer si un usage multi-profils arrive.
- Rappels libres : les seuils servent de repères de séance — ne jamais en faire des scores de mémoire comparables (garde-fou issu d'ADR-005).
- `requirements.txt` verrouillé + README développeur « démarrage en 5 minutes ».

## Mémoire partagée

`memories/` : journal transverse des sessions de travail (un fichier `YYYY-MM-DD-slug.md` par session/événement significatif). Les agents y consignent décisions, apprentissages et pièges pour la session suivante. Factuel, concis, daté — les décisions structurantes vont aussi dans les ADR.
