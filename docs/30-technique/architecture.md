# Architecture

## Vue d'ensemble

- Monorepo : backend FastAPI, frontend web responsive, moteur adaptatif `engine/` partagé (sans dépendance backend).
- Contenu = **données versionnées** (`content/`), séparé du code, validé par `content/schema-item.json`.

## Séparation des périmètres (ADR-002)

| API | Périmètre | Stockage |
|---|---|---|
| `/api/entrainement` | Hors médical, diffusable | Dépôt chiffré « entraînement » |
| `/api/reeducation` | Usage strictement familial | Dépôt chiffré « bilan » |
| `/api/bilan` | Données de santé (RGPD art. 9) | Dépôt chiffré « bilan » — périmètre HDS potentiel |

Aucune jointure inter-périmètre ; toute corrélation passe par un export explicite de l'utilisateur.

## Garde-fous cliniques (`backend/app/domain/`)

- `dosage.py` — sessions/jour, caps de difficulté.
- `fatigue.py` — détection de dégradation (RT, taux d'erreur).
- `messages.py` — séparation stricte des vocabulaires.

Ces services sont appelés **par** l'API, jamais contournés par l'UI.

## Graphe de connaissances (`backend/app/kg/`)

Relations **exercice ↔ fonction ↔ palier ↔ prérequis** — graphe léger plutôt que tags SQL plats. Premier cas d'usage : prérequis Python et chaînes d'attention. Source de vérité : champs `fonctions_ciblees` et `prerequis` du schéma d'item.

## Frontend

- Web responsive (sessions courtes, usage mobile probable en pause).
- **Dark mode par défaut**, contrastes doux, zéro scintillement (photophobie SPC).
- Framework : React retenu par défaut (ADR à formaliser).
- Implémentations d'épreuves dans `frontend/src/exercices/` : CPT, double tâche, empan/n-back, Trail Making, Stroop, multi-étapes + moteurs d'exercices du module Entraînement.

## Hébergement

- HDS requis si données de bilan à caractère médical stockées — isolation physique/logique dans `infra/`.
- Backend FastAPI (cohérent avec la stack RAG médical existante) ; sessions/scores en fichiers chiffrés.
