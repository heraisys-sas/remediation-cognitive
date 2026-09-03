# Spécification — Module Bilan (usage strictement familial)

## Batterie d'entrée (15–20 min, fractionnable pour éviter la fatigue)

| Fonction | Épreuve |
|---|---|
| Attention soutenue | Temps de réaction continu (type CPT) |
| Attention divisée | Double tâche simple |
| Mémoire de travail | Empan, n-back léger |
| Flexibilité | Trail Making adapté |
| Inhibition | Stroop adapté |
| Vitesse de traitement | — |

## Règles d'affichage

- Scores bruts + comparaison à la **trajectoire personnelle uniquement**. Aucune norme population générale affichée à l'utilisateur (risque d'anxiété/mésinterprétation) ; les normes restent visibles côté professionnel si export.
- **Ne jamais présenter un score comme un diagnostic.** Disclaimer systématique : « Ce bilan ne constitue pas un diagnostic. Partagez l'export avec votre professionnel de santé référent. »

## Suivi longitudinal

- Bilan de suivi automatique périodique (toutes les 2 semaines) avec les **mêmes épreuves** → courbe de récupération.

## Export

- **PDF lisible + JSON structuré** pour transmission à un orthophoniste/neuropsychologue référent, à l'initiative de l'utilisateur.
- Désidentification par défaut dans l'export JSON.
- Généré côté `backend/app/export/`.

## Données

- Données de santé (RGPD art. 9) : chiffrement au repos, droit à l'effacement, export patient natif.
- Stockage **séparé** des autres périmètres (ADR-002) ; périmètre HDS potentiel.
- Aucun transit par un service tiers non-HDS.
