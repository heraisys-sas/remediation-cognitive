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

## Commandes

```bash
python3 -m pytest -q                 # tous les tests (backend/tests + engine/tests)
python3 -m pytest -q engine/tests    # moteurs seuls
# Backend (quarantaine de dépendances à figer) : uvicorn backend.app.main:app
```

## Décisions ouvertes

- **Licence** (code et contenu) — ne pas diffuser le dépôt tant que non tranchée.
- **Framework frontend** — React retenu par défaut, ADR à formaliser.
- **Gestion des clés de chiffrement** — ADR à produire au premier sprint backend.

## Mémoire partagée

`memories/` : journal transverse des sessions de travail (un fichier `YYYY-MM-DD-slug.md` par session/événement significatif). Les agents y consignent décisions, apprentissages et pièges pour la session suivante. Factuel, concis, daté — les décisions structurantes vont aussi dans les ADR.
