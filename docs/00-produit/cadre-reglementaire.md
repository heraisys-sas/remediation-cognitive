# Cadre réglementaire (décisions actées)

## Décision MDR

Sous le MDR (règlement UE 2017/745), la mise à disposition — même gratuite — à des professionnels de santé pour usage clinique constitue une **mise sur le marché** (art. 2(27)). Le produit est scindé dès la conception en deux livrables :

| Livrable | Statut | Diffusion |
|---|---|---|
| Module Entraînement (calcul mental, anglais, Python) | Hors MDR, aucune revendication clinique | Libre dès maintenant |
| Module Rééducation | Usage **strictement familial** | Aucune diffusion tierce |
| Module Bilan | Données de santé — usage **strictement familial** | Export vers un référent uniquement à l'initiative de l'utilisateur |

La voie DM classe I autodéclarée (QMS allégé ISO 13485, gestion des risques ISO 14971, documentation technique) est **différée à la Phase 3**, si la demande professionnelle se confirme.

## RGPD / Article 9

Les données de bilan cognitif sont des données de santé : DPIA, chiffrement au repos, droit à l'effacement, export patient natif. **Aucune donnée de bilan ne transite par un service tiers non-HDS.**

## HDS

Si des données de bilan à caractère médical sont stockées : hébergement HDS requis. Séparation physique/logique des données Entraînement (non médicales) et Bilan (potentiellement médicales) pour borner le périmètre HDS au strict nécessaire — cf. ADR-002.

## Relecture orthophoniste

Relecture **informelle et bienveillante** du contenu (choix des items, progression, formulation) — pas une validation clinique, pas de responsabilité professionnelle engagée. Documentée simplement comme retour informel dans le changelog, sans caution clinique.

## Licence

**BSD-3-Clause** (actée le 2026-09-03) — voir `LICENSE` à la racine. S'applique au code et au contenu original du dépôt ; le matériel protégé tiers (ECPA/Pearson, items standardisés) reste strictement exclu et ne doit jamais être intégré.
