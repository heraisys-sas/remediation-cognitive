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

## Relations entre exercices, compétences et références

Le module vide `backend/app/kg/` a été retiré le 20 octobre 2026. Aucun moteur de graphe n’est implémenté ni planifié. Les relations restent décrites dans les contenus et le [référentiel des exercices](../10-clinique/referentiel-exercices.md) ; les champs `fonctions_ciblees` et `prerequis` sont conservés.

Une représentation graphique documentaire pourra être générée ultérieurement à partir des exercices, des compétences décrites et des articles scientifiques cités dans les documents du projet. Sa génération lors d’une release est une piste, sans automatisation ni échéance décidée. Elle devra permettre de retrouver chaque document source et distinguer une compétence sollicitée d’une efficacité d’entraînement démontrée : la citation d’un article ne valide pas à elle seule un exercice. Cette visualisation ne pilotera pas le moteur ni la progression.

## Frontend

- Web responsive (sessions courtes, usage mobile probable en pause).
- **Dark mode par défaut**, contrastes doux, zéro scintillement (photophobie SPC).
- Framework : React retenu par défaut (ADR à formaliser).
- Implémentations d'épreuves dans `frontend/src/exercices/` : CPT, double tâche, empan/n-back, Trail Making, Stroop, multi-étapes + moteurs d'exercices du module Entraînement.

## Hébergement

- HDS requis si données de bilan à caractère médical stockées — isolation physique/logique dans `infra/`.
- Backend FastAPI (cohérent avec la stack RAG médical existante) ; sessions/scores en fichiers chiffrés.
