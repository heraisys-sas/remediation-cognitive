# Stratégie de test

## Moteurs (critique — ADR-001)

- Non-régression **obligatoire** sur `engine/tests/` : ordonnancement FSRS, critères de maîtrise, règle ±1 palier, détection de fatigue.
- Tests de timing : mesures de RT stables (résolution, dérive horloge).

## Backend

- Tests unitaires par service métier (`backend/app/domain/`).
- Tests d'intégration des routes API — vérifier l'**isolation des trois périmètres** : aucune fuite entraînement ↔ bilan.
- Journalisation des accès bilan testée.

## Frontend

- Comportement des épreuves : timing, événements, règles d'arrêt (proposition, jamais forcée).
- Audit visuel systématique : contrastes doux, dark mode, absence de scintillement (photophobie).

## Contenu

- Chaque item validé par `content/schema-item.json` avant intégration.
- Relecture orthophoniste tracée (`meta.relecture_ortho`) avant activation d'un nouveau palier.

## Commandes

```bash
python3 -m pytest -q          # tout (backend/tests + engine/tests)
python3 -m pytest -q engine/tests   # moteurs seuls
```
