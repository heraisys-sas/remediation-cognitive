# Sprint 5 — Programme d'entraînement de 8 semaines

## Demande

« Génère 2 mois d'exercices avec complexification éventuelle si c'est dans les bonnes pratiques. »

## Périmètre

- Contenu de cadrage : `content/programmes/8-semaines.json` (8 semaines × 7 jours) + README.
- Générateur déterministe `tools/generer_programme.py` ; validation étendue.
- API `GET /api/programme` (plan du jour calculé depuis une date de début locale) + stockage dédié minimal.
- Interface : bouton d'accueil + écran « Programme » (plan du jour, vue des 8 semaines, règles).
- 4 tests backend ; 114 tests au total.

## Décisions (ADR-006)

- Le programme **propose** : plafond de palier hebdomadaire = borne, pas objectif. La maîtrise (90 % × 3) et la fatigue décident.
- Pas de dette : une journée manquée ne se rattrape pas. Journée légère « au choix » + jour de repos prévus.
- Recul : deux séances sous 50 % de réussite sur un thème → reprise du palier courant.
- Aucune observance mesurée (pas de taux de complétion, pas de série de jours).
- État local limité à la date de début, périmètre entraînement, stockage séparé des données de séance et du carnet.

## Contrôles

- Validateur : 53 fichiers, 691 items, 0 erreur — dont le programme (thèmes réels, plafonds ≤ paliers disponibles, séance = un thème, repos sans thème, durées bornées).
- `verifier_reponses.py` : 691 items, 0 anomalie. `verifier_interface.py` : identifiants et remise à zéro du champ OK.
- `pytest` : 114 passed (dont plan du jour, avancement calendaire avec horloge injectée, stabilité de la date de début, fin de programme).

## Délégation (cluster_bypass_reason)

Sous-agents non mobilisés : les tentatives précédentes ont échoué à l'exécution (HTTP 403 côté fournisseur, aucun livrable produit — consigné dans `.cluster/sprint3/plan.md`). Le travail de ce sprint est un contenu de cadrage + un endpoint + un écran, entièrement couvert par des contrôles versionnés ; la revue reste à faire par la spécialiste sur le contenu du programme (rythme, plafonds, formulations).

## Statut

Livré : contenu, générateur, validation, API, interface, tests, docs (ADR-006, contrat, specs, protocoles, CHANGELOG, READMEs), rapport de sprint.
