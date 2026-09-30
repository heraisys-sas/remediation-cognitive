# Bilan & rééducation cognitive — syndrome post-commotionnel

Monorepo pour un logiciel de **bilan cognitif**, de **rééducation ciblée** et d'**entraînement cérébral générique** destiné à des adultes avec syndrome post-commotionnel (SPC).

## Déduction — branche d’essai

100 grilles en cinq paliers : P1–P4 en 3×3, P5 en 4×4. Indices collectifs explicites, références partielles et entre-deux ; progression en trois étapes par palier. [Contenu et vérifications](content/entrainement/deduction/README.md).

## Principe directeur

Le moteur adaptatif (`engine/`) est **unique** et réutilisé par les trois modules. Le contenu (`content/`) est versionné **séparément du code**. Les garde-fous cliniques vivent dans `backend/app/domain/` — ils ne sont pas contournables par l'UI : toute dérogation (ex. la limite de séances du jour, ADR-021) est explicite et accordée côté serveur.

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

## Licence

BSD-3-Clause — voir [LICENSE](LICENSE). S'applique au code et au contenu du dépôt.

## Décisions ouvertes

- Framework frontend : React retenu par défaut, ADR à formaliser.
- Hébergement HDS : à ouvrir uniquement en Phase 3 le cas échéant.

## Relectures orthophoniste

Retours **informels** sur le contenu (items, progression, formulation) — journalés dans [docs/10-clinique/relectures.md](docs/10-clinique/relectures.md) et le changelog. Aucune validation clinique, aucune caution.
