# ADR-033 — Sérialiser les opérations persistantes d'une séance

## Contexte
La PR #11 mélangeait corrections de concurrence, refactorisations et modifications de comportement. Les écritures JSON atomiques existantes ne suffisent pas à protéger un cycle lecture-modification-écriture entre deux gestionnaires.

## Décision
Reprendre les verrous de fichier et un verrou de transaction par thème. Le démarrage couvre contrôle du quota et incrément ; la clôture couvre lecture et mise à jour des cartes, maîtrise et temps de référence. Les formats de données et l'API restent compatibles. Garder la racine injectable actuelle. Vérifier avec plusieurs clients, threads et processus démarrés via `spawn`.

## Conséquences
Les lectures peuvent créer des fichiers compagnons `.lock`. Les séances en mémoire ne sont pas partagées entre workers ; ce changement ne suffit donc pas à autoriser un déploiement multi-worker. La transaction sérialise l'accès mais n'offre pas de rollback de plusieurs fichiers après panne. Le moteur de fatigue et les contenus ne changent pas. Les autres choix de la revue figurent dans `revue-pr11.md`.
