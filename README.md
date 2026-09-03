# Bilan & rééducation cognitive — syndrome post-commotionnel

Monorepo pour un logiciel de **bilan cognitif**, de **rééducation ciblée** et d'**entraînement cérébral générique** destiné à des adultes avec syndrome post-commotionnel (SPC).

## Principe directeur

Le moteur adaptatif (`engine/`) est **unique** et réutilisé par les trois modules. Le contenu (`content/`) est versionné **séparément du code**. Les garde-fous cliniques vivent dans `backend/app/domain/` — ils ne sont pas contournables par l'UI.

## Les trois modules

| Module | Statut | Diffusion |
|---|---|---|
| **Entraînement** (calcul mental/tables, anglais, Python) | Hors MDR | Libre dès maintenant |
| **Rééducation ciblée** | Usage strictement familial | Aucune diffusion tierce |
| **Bilan** (données de santé) | Usage strictement familial | Export vers un référent à l'initiative de l'utilisateur |

## Arborescence

```text
docs/          00-produit (vision, cadre réglementaire, feuille de route)
               10-clinique (fondements, taxonomie, protocoles, relectures)
               20-specs (moteur adaptatif, 3 modules)
               30-technique (architecture, sécurité, ADR)
               40-qms (Phase 3 différée — volontairement vide)
backend/       FastAPI — 3 périmètres d'API isolés + garde-fous + graphe de connaissances
engine/        Moteur adaptatif commun (paliers, FSRS, maîtrise, sessions)
content/       Items et paliers versionnés (schéma : content/schema-item.json)
frontend/      Web responsive — dark mode par défaut, contrastes doux, zéro scintillement
infra/         Déploiement, isolation HDS
```

## Phases

1. **Moteur + Entraînement + Rééducation (familial)** — en cours
2. **Bilan structuré** (familial, export PDF/JSON)
3. **DM classe I autodéclarée** (différée, conditionnelle)
4. **Boucle longitudinale**

Détail : [feuille de route](docs/00-produit/feuille-de-route.md).

## Décisions ouvertes

- Licence du code et du contenu (voir [cadre réglementaire](docs/00-produit/cadre-reglementaire.md)) — ne pas diffuser le dépôt tant que non tranchée.
- Framework frontend : React retenu par défaut, ADR à formaliser.
- Hébergement HDS : à ouvrir uniquement en Phase 3 le cas échéant.

## Relectures orthophoniste

Retours **informels** sur le contenu (items, progression, formulation) — journalés dans [docs/10-clinique/relectures.md](docs/10-clinique/relectures.md) et le changelog. Aucune validation clinique, aucune caution.
