# 2026-09-24 — Section évaluation + quatre méthodes de remédiation

## Demande

1. Implémenter une **section évaluation** où déplacer ce qui ne doit pas être entraîné (pour ne pas fausser les mesures).
2. Puis, dans l'entraînement : **SFA/PCA** (manque du mot, l'utilisateur génère les attributs), **auto-instruction** (Meichenbaum), **PQRST** (mémoire de textes), **GMT** scénarisé (planification).

## Livré

### 1. Séparation évaluation / entraînement
- Catégorie par thème (`entrainement` / `evaluation`) exposée par l'API ; l'interface range l'accueil en trois groupes : entraînement, **évaluation**, extra.
- **Évaluation = mémoire, concentration, rappel de séries** (les paradigmes qui mesurent) : plafonnés à **1 séance/jour** (garde-fou `LIMITES_SESSIONS_JOUR`), car répéter une mesure la fausse par apprentissage du matériel.
- Aucun nouveau contenu d'allure évaluative n'entre dans l'entraînement (règle maintenue).

### 2. SFA / PCA (paliers 6 et 7 de « retrouver le mot »)
- L'utilisateur **génère les attributs** (catégorie, usage, lieu pour la SFA ; premier son, syllabes, rime pour la PCA) dans une zone de génération guidée, puis **nomme le mot**.
- Les notes ne sont **pas notées** — c'est leur génération qui fait le travail (mécanisme actif des deux méthodes).
- Nouveau type `analyse-mot`, nouvelle zone d'interface `zone-generation`.

### 3. Thème « Méthodes » (22 items)
- **PQRST** : texte affiché temporisé (mode d'affichage `texte`), puis question de mémoire.
- **GMT** : choisir le plan d'étapes cohérent (et vérifier son plan).
- **Auto-instruction** : quelle question se poser avant d'agir — le fil conducteur est aussi rappelé dans les consignes d'autres familles.

## Point d'attention rencontré

Le préfixe d'identifiants du nouveau thème (`me-`) **collisionnait** avec celui de « mémoire » : le validateur l'a signalé (ids dupliqués). Préfixe changé en `mt-`. Leçon : un préfixe par thème, et laisser le validateur faire son travail.

## Contrôles

813 items / 0 erreur ; 132 tests (catégories, limite d'évaluation, PQRST/GMT/auto-instruction, SFA/PCA) ; garde-fous cliniques sans violation.

## Reste à faire

- Passage visuel des nouveaux écrans (section évaluation, texte PQRST, génération SFA/PCA).
- Relecture orthophoniste du nouveau contenu.
- Envisager des **questions de compréhension multiples** par texte PQRST (aujourd'hui une par texte).

## 2026-09-27 — quand révéler la réponse (et la stratégie)

Deux questions de l'utilisateur : réponse immédiate ou second essai ? et « les exercices de
méthode sollicitent la mémoire plus que la stratégie — faut-il indiquer une stratégie de
mémorisation ? ».

- Recherche : **errorless learning** (réponse immédiate, quand la personne ne peut pas se
  corriger) vs **pratique de récupération + hypothèse de guidage** (retour immédiat = meilleure
  séance mais moins bonne rétention ; Schmidt 1991, Winstein & Schmidt 1990).
- Décision (ADR-014) : jamais de réponse avant un essai ; récupération → immédiat ; raisonnement
  → second essai. Implémenté (`domain/feedback.py`, `essai_supplementaire`, message dédié,
  interface qui laisse l'exercice actif).
- Vérifié dans le contenu : le palier 1 de méthodes est **PQRST** → mémoire d'un texte. Le
  panneau « Méthode » affiche maintenant la méthode de l'exercice en cours (PQRST, GMT…) pendant
  la réponse — la stratégie doit être **sous les yeux** pour être utilisable.
- Reste ouvert (décision de contenu) : pour vraiment *entraîner* PQRST plutôt que le tester, il
  faudrait des items demandant de **produire** une étape (poser sa question, reformuler).

## 2026-09-27 — proposition « PQRST mis en œuvre »

Demande : préparer la proposition de palier.

- Constat mesuré : le palier PQRST actuel teste le **résultat** (texte masqué → 2 questions) ; les
  étapes Q (écrire sa question) et S (reformuler) — celles qui portent l'apprentissage — sont
  absentes. La méthode est nommée, pas appliquée.
- Proposition : `docs/20-specs/proposition-palier-pqrst-mis-en-oeuvre.md` — séquence guidée de
  5 étapes dans un même item (Parcours jugé, Question libre non notée + modèle, Lecture sans
  chronomètre, Reformulation jugée sur idées-clés + résumé modèle, Test jugé), 4 textes par
  palier, nouveaux identifiants `mt2-`, placement **après** les paliers actuels.
- Décision non prise : 5 points cliniques à trancher (seuil de reformulation, question libre vs
  choix, 5 ou 3 étapes, longueur des textes, fiche méthode hors écran). Rien n'est implémenté.
- Note de méthode : proposer, chiffrer, et **ne pas coder** tant que l'orthophoniste n'a pas
  tranché les points qui relèvent de la clinique.
