# 2026-09-03 — Création du projet et cadrage

## Décisions prises

- **Scission réglementaire actée** : Entraînement hors MDR (diffusable) ; Rééducation + Bilan en usage strictement familial ; voie DM classe I autodéclarée différée en Phase 3 (conditionnelle).
- **Moteur adaptatif unique** (ADR-001) ; stockages séparés entraînement / bilan (ADR-002).
- **Module Python cadré** : mémorisation de concepts et de commandes du langage — thématique à double dividende (l'effort de mémorisation est l'exercice cognitif, le contenu acquis est une compétence durable). Formats : errorless → production (rappel actif) → prédiction de sortie. Cap : 2 niveaux d'imbrication max en phase initiale.
- Critère de maîtrise par défaut : **90 % de réussite sur 3 sessions consécutives**.
- Squelette créé : 78 fichiers, 12 assertions de smoke tests passées (règle ±1 palier, maîtrise, fatigue, dosage, vocabulaires).

## Points d'attention

- La charge cognitive d'un snippet à prédire monte très vite (boucle + condition dépasse la mémoire de travail post-SPC) — respecter le cap d'imbrication.
- La relecture orthophoniste est **informelle** — ne jamais la présenter comme une validation clinique, la tracer dans `docs/10-clinique/relectures.md` + `CHANGELOG.md`.
- Aucune norme populationnelle côté patient ; aucun score présenté comme un diagnostic.
- Ne pas committer de données de bilan réelles (`.gitignore` exclut `data/`, `.env`, clés).

## Reste à faire (état au 2026-09-03)

- Licence à trancher (ne pas diffuser le dépôt d'ici là).
- Framework frontend à formaliser en ADR (React par défaut).
- Gestion des clés de chiffrement : ADR au premier sprint backend.
- Dépendances backend à figer (fastapi, uvicorn, pydantic, fsrs, reportlab…).
- Distant git à configurer si souhaité (dépôt local uniquement à ce stade).
