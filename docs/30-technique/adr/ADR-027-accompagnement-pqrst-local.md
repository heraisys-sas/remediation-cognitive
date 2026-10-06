# ADR-027 — Retour métacognitif PQRST avec le modèle Apple local

## Contexte

Le prototype vise une relance pertinente pour un adulte après sa reformulation,
sans installer un autre modèle et sans transmettre ses réponses à un service distant.
Une intervention pendant la séquence pourrait faciliter le rappel et brouiller la
réussite autonome. Le premier périmètre est donc le retour après correction.

## Décision

- Ajouter un accompagnement facultatif uniquement après validation de PQRST mis en œuvre.
- La personne peut retravailler sa formulation et demander deux relances au maximum.
  Ces modifications ne sont pas soumises au moteur de correction.
- Le SDK officiel Apple sélectionne une catégorie parmi des questions métacognitives
  prédéfinies. Aucun texte libre généré n'est affiché ; le modèle n'est pas correcteur.
- Modèle système embarqué uniquement, pas de repli distant ni d'outils réseau.
- SDK facultatif : absence, modèle indisponible ou délai dépassé ne bloquent jamais la séance.
- Seuls le texte de travail, la question personnelle et la reformulation sont traités, sans stockage de conversation.
  Les scores, historiques et identifiants de contenu restent inchangés.

## API

`GET /api/capacites/accompagnement` annonce la disponibilité locale.
`POST /api/capacites/accompagnement` reçoit `texte`, `reformulation` et une `question` facultative (2 000 caractères maximum) et retourne
`disponible` et, si possible, `relance` et `categorie`. Les entrées sont bornées et une expiration
limite l'attente. L'interface affiche le résultat comme question de méthode, jamais
comme jugement de justesse.

## Conséquences et limites

Ce périmètre teste la pertinence du choix de relance, pas une conversation ouverte.
Une catégorie peut être mal choisie ; le format contraint ne valide pas le sens.
L'efficacité clinique de cet accompagnement n'est pas démontrée. Avant extension,
relire des exemples avec l'orthophoniste, notamment reformulations correctes,
incomplètes, paraphrases et contresens, et vérifier le comportement hors réseau.
Le SDK réutilise les ressources Apple Intelligence présentes sur le Mac ; sa
 disponibilité dépend de la configuration du système. Aucun nouveau corpus créé.

La catégorie `question` relie la production du champ 2 à la reformulation. Elle est exclue lorsque le champ 2 est vide. La question personnelle n’est jamais comparée au modèle ni notée.
