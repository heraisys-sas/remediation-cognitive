# Essayer l'accompagnement PQRST local

Ce prototype apparaît après la correction du palier « PQRST mis en œuvre » dans
Méthodes. Écrire une reformulation, valider la séquence, puis choisir « Demander
une relance ». On peut retravailler le texte et demander une dernière relance ;
le résultat déjà enregistré ne change pas.

## Préparer le poste

Mac compatible Apple Intelligence, fonction activée et ressources système prêtes,
macOS 26+, Xcode 26+ avec licence acceptée. Le modèle utilisé est celui d'Apple,
aucun poids de modèle supplémentaire n'est installé par le projet.

Depuis la racine du dépôt, avec le Python qui lance habituellement le serveur :

```sh
python3 -m venv --system-site-packages .local/apple-fm-venv
.local/apple-fm-venv/bin/python -m pip install apple-fm-sdk==0.2.1
.local/apple-fm-venv/bin/python -c 'from backend.app.domain.accompagnement_local import etat; print(etat())'
```

L'environnement isolé réutilise les dépendances serveur existantes. Son répertoire
est ignoré par Git. Après avoir arrêté soi-même l'ancien serveur, lancer :

```sh
.local/apple-fm-venv/bin/python -m uvicorn backend.app.main:app
```

Recharger la page. Un serveur lancé avec un autre Python sans SDK continuera les
exercices normalement, mais ne fournira pas l'accompagnement Apple.

## Vérifier

`GET /api/capacites/accompagnement` retourne la disponibilité et un code de raison
si elle manque. Les requêtes ne transmettent ni identifiant patient, ni score, ni
réponse attendue. L'adaptateur appelle uniquement SystemLanguageModel, sans outil
ni repli cloud. Le téléchargement du SDK et la préparation initiale des ressources
Apple nécessitent un réseau ; l'inférence utilise les ressources du Mac.

Compléter les tests unitaires par un essai manuel sans réseau, et relire les
relances avec l'orthophoniste. Une sortie structurée n'assure pas la pertinence
pédagogique. Ce prototype choisit entre quatre angles (dont le lien avec la question personnelle) de réflexion, sans conversation
ouverte ni nouvelle correction sémantique.

Source technique : https://github.com/apple/python-apple-fm-sdk
Décision de périmètre : ADR-027-accompagnement-pqrst-local.md.

## Vérification du 6 octobre 2026

SDK 0.2.1 installé dans l'environnement isolé ; disponibilité réelle confirmée.
Le test `TEST_APPLE_FM_LOCAL=1 .local/apple-fm-venv/bin/python -m pytest -q
backend/tests/test_accompagnement_local.py` passe (15 tests). Deux appels natifs
successifs ont produit des catégories distinctes. Le choix n'est pas toujours
optimal : « objectif » a été choisi pour une reformulation qui mentionnait déjà
l'action principale. L'interface ne présente donc pas la relance comme une lacune
détectée. Le test matériel a nécessité l'accès natif hors sandbox ; pas de coupure
réseau imposée au Mac pendant cet essai. Aucun serveur utilisateur redémarré.

## Lot 1 — Comparer deux documents

Le même environnement permet d'ouvrir « Approfondir » après correction dans
Comparer deux documents. Expliquer son raisonnement, puis répondre à une première
relance pour en demander une dernière. Le modèle choisit un critère et un angle ;
les valeurs citées sont reprises exactement des documents par le logiciel. Les
échanges ne changent pas le score et ne sont pas enregistrés. Voir ADR-029.
