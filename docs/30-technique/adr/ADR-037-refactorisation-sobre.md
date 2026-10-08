# ADR-037 — Registre commun et modules de comportement

## Contexte

Issue #20 : des listes de thèmes et des comportements indépendants étaient dispersés
ou regroupés dans trois fichiers très longs. Un déplacement mécanique doit conserver
la correction, les contenus servis, la concurrence et les interactions audio.

## Décision

- `domain/catalog.py` contient les identités, sources, catégories, points de départ,
  parcours et paramètres structurants. Les anciennes vues sont dérivées du catalogue.
  Les textes utilisateur restent dans `messages.py`.
- Ajout compatible de `interface: {extra, francais, dictee}` à chaque thème de
  `GET /api/entrainement/themes`. L'interface utilise ces propriétés au lieu de
  maintenir ses propres listes de thèmes. Aucun autre contrat HTTP ne change.
- `domain/correction/` sépare texte, nombres, rappel, séquence et grille. Les imports
  publics et helpers utilisés par les outils restent réexportés. `CorrectionResult`
  fournit le détail compatible au service sans multiplier ses variables parallèles.
- La finalisation de progression devient une fonction sans écriture ; les transactions,
  verrous, compteurs et écritures restent dans les couches existantes.
- `tools/validation/` sépare domaines et orchestration ; `validate_items.py` conserve
  le point d'entrée et les imports historiques. Aucun contrôle de contenu retiré.
- `tools/generation.py` partage I/O JSON et CLI simple. Les tirages et manifests
  spécifiques restent dans les générateurs ; aucun contenu existant n'est régénéré.
- Scripts vanilla JS chargés explicitement dans la page : API, préférences, état,
  sessions, missions, programme et comportements d'exercices. Un dispatch de handlers
  gère le rendu spécialisé, la réponse et le feedback côté session.
- `createSessionState` crée un état neuf. Une façade d'accès maintient les callbacks
  existants ; l'état applicatif et la génération d'annulation restent indépendants.
  Le nettoyage des minuteries et de la dictée précède la réinitialisation.
- Les tests et contrôles lisent les scripts effectivement servis, dans l'ordre HTML.
  Ils conservent leurs scénarios et assertions ; le contrôle de démarrage vérifie aussi
  qu'une séance est réellement installée, pas seulement que POST est envoyé.
- Ruff démarre avec F, E9, B006. Pas de formatage global ni d'avalanche de règles.
- `.cluster` garde rapports, décisions et mesures. Copies et scripts temporaires restent
  récupérables au commit `160367c`, mais ne parasitent plus la recherche active.

## Conséquences et vérification

`app.js` passe d'environ 3 000 à environ 530 lignes. Les handlers partagent encore
les utilitaires DOM et la façade d'état : pas de framework ni de couche de services
supplémentaire. Une extraction future doit supprimer une dépendance réelle, pas suivre
un seuil de taille mécanique.

Les contenus et identifiants restent byte-identiques. Comparaison de la correction
avant/après sur 6 670 entrées : résultats identiques, similarité locale neutralisée
pour ce contrôle déterministe ; les tests sémantiques avec doubles du moteur local
restent présents. Les tests de concurrence, de dosage, de progression, de dictée et
d'audio sont conservés. Le test de chargement exécute l'ensemble des scripts avec DOM
et API simulés ; il ne remplace pas un essai du microphone réel.
