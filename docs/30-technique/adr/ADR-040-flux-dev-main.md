# ADR-040 — Branches temporaires vers dev, livraisons vers main

## Contexte

Les modifications étaient validées sur plusieurs branches d’essai et fusionnées directement dans main. L’utilisateur demande une branche permanente dev pour intégrer les changements validés, puis livrer depuis dev vers main. Les ressources locales Apple ne doivent plus être confondues avec les versions du code.

## Décision

Créer dev depuis main (8b3510b). Les branches temporaires partent de dev, y sont fusionnées par PR après revue et CI verte, puis supprimées. La PR #23 est redirigée vers dev. Main reste stable jusqu’à une PR de livraison dev → main, autorisée et validée fonctionnellement.

CI sur pushes et PR vers dev et main, avec les contrôles existants conservés. Squash pour les branches temporaires, merge commit pour la livraison de la branche permanente dev ; dev n’est jamais supprimée. Hotfix de main reporté vers dev par PR ; pas de force push. Le guide CONTRIBUTING.md décrit les commandes et exceptions de checkout sale.

## Conséquences

Une intégration n’est pas une livraison stable. Les essais de micro, voix et parcours concernés complètent la CI avant main. Pas de nouvelle politique réglementaire ni de reviewers humains obligatoires pour ce POC. Ces règles sont des conventions documentées et vérifiées par CI ; elles ne prétendent pas configurer une protection GitHub de branches.

Un changement de branche dans le même checkout conserve les installations locales ignorées par Git ; un nouveau checkout ne copie pas le SDK, l’adaptateur Swift ni les données. Le checkout utilisateur et son serveur sont préservés pendant cette transition.
