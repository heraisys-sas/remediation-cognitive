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

## État courant — sprint 5 livré (2026-09-22)

- **Jouable de bout en bout** : huit thèmes (calcul mental, mémoire avec empans de chiffres **et de mots**, concentration, retrouver le mot, vie sociale, rappel de séries, plus Python/anglais en section **Extra**) et trois écrans transverses : **programme de 8 semaines**, **missions hors écran & carnet**, séance. Lancer `python3 -m uvicorn backend.app.main:app` puis ouvrir `/ui/`.
- **Implémenté** : `engine/` (moteur inchangé) ; `backend/` — `/api/entrainement`, `/api/social`, `/api/programme` (correction par thème, essais assistés, rappel libre au seuil, plan du jour) ; `frontend/` (SPA vanilla : phase de mémorisation temporisée, séries de mots, compte à rebours, propositions cliquables, indices progressifs).
- **Contenu** : **691 items** + 8 missions + **programme de 8 semaines**, générés de façon déterministe (`tools/generer_memo_concentration.py`, `generer_evocation_social.py`, `generer_rappel_series.py`, `generer_programme.py`).
- **Tests** : 114 passed (`python3 -m pytest -q`). Contrôles : `tools/validate_items.py` (schéma, manifests, propositions, indices, rythme d'affichage, séries, programme — 0 erreur), `tools/verifier_reponses.py` (0 anomalie), `tools/verifier_interface.py`.
- **Contrat d'API figé** : `docs/30-technique/api-contract.md` — toute modification = ADR. Décisions : ADR-004 (aides progressives, options, périmètre social), ADR-005 (empan de mots, rappel libre, rythme), ADR-006 (programme, progression non contrainte).
- **Garde-fou produit** : le programme propose un rythme — il ne mesure rien. Aucun taux d'observance ni de complétion ne doit être calculé (ADR-006).
- **Traçabilité** : `.cluster/sprint1/`, `.cluster/enrichissement/`, `.cluster/sprint3/`, `.cluster/sprint4/`, `.cluster/sprint5/` ; journaux `memories/2026-09-03-sprint-1.md`, `2026-09-15-…`, `2026-09-21-…`, `2026-09-22-empan-de-mots-et-rappel-de-series.md`, `2026-09-22-programme-de-8-semaines.md`.

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
python3 tools/validate_items.py      # schéma, manifests, options, indices, rythme, séries
python3 tools/verifier_reponses.py   # réponses recalculées depuis l'énoncé
python3 tools/verifier_interface.py  # identifiants et réinitialisation du champ de saisie
python3 tools/generer_memo_concentration.py --dry-run   # régénère mémoire/concentration
python3 tools/generer_evocation_social.py --dry-run     # régénère evocation/social + missions
python3 tools/generer_rappel_series.py --dry-run        # régénère rappel-series
python3 tools/generer_programme.py --dry-run             # régénère le programme de 8 semaines
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
