# ADR-050 — Frontière de déploiement sans comptes applicatifs

Statut : accepté pour implémentation, 21 octobre 2026 — issue #7.

## Contexte

L’instance persistante actuelle est mono-utilisateur, sans authentification.
L’utilisateur exclut la gestion des utilisateurs dans ce lot ; une infrastructure
externe pourra porter les fonctions d’accès manquantes. Le transfert de
progression est reporté.

## Décision

Conserver une écoute locale par défaut dans les instructions de lancement et
émettre un avertissement non bloquant au démarrage ASGI, y compris avec Uvicorn
lancé directement. Documenter les données et la séparation ADR-002.
Ne pas déduire l’adresse d’écoute à partir d’en-têtes HTTP ou de variables
d’environnement non utilisées par le serveur.

Une exposition distante nécessite un contrôle d’accès externe et une instance
avec stockage isolé par personne. Le service ne sait pas sélectionner un profil
selon une identité transmise par une passerelle.

## Conséquences

Aucune dépendance, aucun compte et aucune nouvelle infrastructure imposés.
L’avertissement informe mais n’empêche pas un déploiement mal configuré ; les
vérifications réseau restent à effectuer par l’exploitant selon le
[guide](../deploiement-local.md). Aucun changement du moteur ou des données.
