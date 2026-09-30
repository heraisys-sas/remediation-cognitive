# ADR-019 — Plans vérifiables et documents consultables

Date : 2026-09-30. Statut : adopté pour la branche d’essai.

## Contexte

La revue des 136 items de Méthodes et Au quotidien a identifié des plans sans erreur nécessaire, un exercice de recherche transformé en rappel par masquage du document et des QCM à distracteurs manifestement inadéquats. L’utilisateur a demandé leur correction.

## Décision

- Méthodes P4 : chaque situation exprime les deux précédences d’un plan de trois étapes. Le plan proposé est une rotation de l’ordre correct. La question demande quelle **seule étape déplacer, sans changer l’ordre des deux autres**. Un test énumère les déplacements et vérifie qu’une seule étape rétablit l’ordre. Le sens des précédences énoncées relève aussi de la relecture du texte, pas de ce test mécanique.
- Méthodes P5 : `contenu.document` (chaîne non vide) est un support permanent. Il est renvoyé dans le contenu public de l’API, présenté avec la question et les choix, sans `contenu.affichage` ni phase temporisée. L’interface le rend comme texte, sans injection HTML. Il est supprimé avec la zone des choix au changement de question. Le validateur refuse un document absent ou un affichage temporisé pour ce type.
- Les huit documents contiennent plusieurs renseignements voisins pour que la question oriente la recherche. PQRST garde ses phases de mémorisation existantes.
- Méthodes P2/P3 et Au quotidien P2/P4/P5/P6/P7/P8 : situations avec contraintes explicites, alternatives liées au même problème. Le choix se fonde sur le but, la dépendance, le repère disponible ou le temps. P5 quotidien utilise de véritables liens événement-action ; P7 porte sur les supports externes. Une réponse à un rendez-vous déjà manqué traite la situation présente, pas seulement la prévention future.
- 32 items Méthodes remplacés par `mt3-…`, 64 items Au quotidien par `qo2-…`. Les anciens identifiants ne désignent jamais les nouveaux problèmes. Les paliers/prérequis et les familles non modifiées restent identiques. Les historiques sont conservés, sans migration destructive.

## Conséquences et limites

L’API expose un nouveau champ de contenu optionnel ; les routes et le format des réponses utilisateur restent identiques. Le serveur doit charger le nouveau corpus et l’interface le nouveau script. Le document n’est pas caché pendant la recherche, y compris au second essai.

Contrôles : unicité de relocalisation des huit plans, document obligatoire, rendu JS des plans/documents en alternance avec clic sur les choix, tests API, reproduction des fichiers par les générateurs, validation générale et suite de tests.

Les QCM restent un entraînement au choix de stratégie, pas une démonstration de transfert dans la vie réelle. Ces corrections ne valident pas une efficacité clinique, une difficulté normative ou une progression homogène entre familles. L’estimation des durées et la correction lexicale des reformulations PQRST restent hors de cette correction ciblée.
