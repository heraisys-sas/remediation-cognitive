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

## État courant — sprint 3 livré (2026-09-21)

- **Jouable de bout en bout** : sept thèmes — calcul mental, anglais, Python, mémoire (empan, paires associatives, n-back), concentration (chaînes, cascades, double tâche, séries), **retrouver le mot** (reconnaissance, rappel indicé à indices progressifs, rappel de la source) et **vie sociale** (vignettes d'émotion, réponses adaptées, lecture d'intention) — plus un écran **missions hors écran & carnet**. Lancer `python3 -m uvicorn backend.app.main:app` puis ouvrir `/ui/`.
- **Implémenté** : `engine/` (FSRS 6.3.2 encapsulé, SessionRunner, maîtrise 90 % × 3, fatigue = proposition) ; `backend/` (routes `/api/entrainement` selon le contrat + périmètre `/api/social` pour missions et carnet, correction serveur par thème, persistance JSON sous `backend/data/` — gitignored) ; `frontend/` (SPA vanilla sur `/ui`) ; **587 items de contenu** (9 paliers calcul mental, anglais/Python, mémoire 8 × 18, concentration 9 × 18, evocation 5 × 10, social 4 × 10) + 8 missions — généré par `tools/generer_memo_concentration.py` et `tools/generer_evocation_social.py` (déterministes).
- **Tests** : 106 passed (`python3 -m pytest -q`). Contrôles de cohérence : `python3 tools/validate_items.py` (schéma, manifests, options, indices — 0 erreur), `python3 tools/verifier_reponses.py` (réponses recalculées — 0 anomalie), `python3 tools/verifier_interface.py` (identifiants interface ↔ HTML). Toute modification doit les garder verts.
- **Contrat d'API figé** : `docs/30-technique/api-contract.md` — le modifier = décision structurante (ADR). Extensions récentes : `contenu.affichage` (sprint 2), `contenu.options`/`contenu.indices` + champ `indice_utilise` et essai « assisté » + périmètre `/api/social` (sprint 3, ADR-004).
- **Traçabilité du sprint** : `.cluster/sprint1/` et `.cluster/enrichissement/` ; `memories/2026-09-03-sprint-1.md`, `memories/2026-09-15-enrichissement-memo-concentration.md`, `memories/2026-09-21-acces-au-mot-et-vie-sociale.md`.

## Règles non négociables (garde-fous cliniques)

1. **Le dosage prime sur la difficulté** : séances 5–10 min, limites journalières, cap de difficulté avec justification pédagogique explicite.
2. **Aucune norme populationnelle affichée à l'utilisateur** ; jamais présenter un score comme un diagnostic.
3. **Séparation stricte des vocabulaires** : clinique (bilan) vs neutre/ludique (entraînement) — centralisée dans `backend/app/domain/messages.py`, ne pas construire de chaîne utilisateur ailleurs.
4. **Aucune donnée de bilan ne transite par un service tiers non-HDS.**
5. **Stockages séparés** entraînement vs bilan (ADR-002) — aucune jointure inter-périmètre.
6. **Environnement visuel calme** : dark mode par défaut, contrastes doux, zéro scintillement (photophobie SPC).
7. **Phase aiguë post-SPC : bloquer et simplifier** ; l'interleaving n'arrive qu'après un socle acquis.
8. Errorless en entrée de palier ; la détection de fatigue **propose** l'arrêt, jamais forcée.

## Conventions

- **Langues** : documentation et contenu en français ; identifiants de code en anglais, docstrings/commentaires en français.
- **Contenu** : tout item passe par `content/schema-item.json` avant intégration ; relecture orthophoniste tracée dans `meta.relecture_ortho` — relecture **informelle**, jamais présenter comme une validation clinique.
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
python3 tools/validate_items.py      # schéma, manifests, options, indices
python3 tools/verifier_reponses.py   # réponses recalculées depuis l'énoncé
python3 tools/verifier_interface.py  # identifiants demandés par l'interface ↔ présents dans l'HTML
python3 tools/generer_memo_concentration.py --dry-run   # régénère mémoire/concentration
python3 tools/generer_evocation_social.py --dry-run     # régénère evocation/social + missions
```

Dépendances effectives du sprint 1 : fastapi, uvicorn, httpx, pytest, fsrs (paquet officiel open-spaced-repetition). Un `requirements.txt`/lock est à produire au prochain sprint.

## Décisions ouvertes

- Quota journalier : 3 séances/jour **par thème** (jusqu'à 9/jour au total) — global ou par thème, à trancher (paramétrable dans `backend/app/domain/dosage.py`).
- Framework frontend — vanilla sans build au sprint 1 ; React+Vite quand l'UI se complexifiera (ADR-003 à formaliser).
- Gestion des clés de chiffrement — ADR à produire (le stockage JSON actuel n'est pas chiffré ; périmètre non médical uniquement).
- Mode errorless d'entrée de palier et prerequis anglais/Python complets — reportés (le sprint 2 a livré mémoire/concentration, le sprint 3 l'accès au mot et la vie sociale).
- Relecture orthographique et clinique des 396 items générés (`meta.relecture_ortho` = `a_revoir`) et des 8 missions avant diffusion au-delà de l'usage familial.
- Carnet des missions : mono-utilisateur, aucune donnée de séance n'y transite — à confirmer si un usage multi-profils arrive.
- `requirements.txt` verrouillé + README développeur « démarrage en 5 minutes ».

## Mémoire partagée

`memories/` : journal transverse des sessions de travail (un fichier `YYYY-MM-DD-slug.md` par session/événement significatif). Les agents y consignent décisions, apprentissages et pièges pour la session suivante. Factuel, concis, daté — les décisions structurantes vont aussi dans les ADR.
