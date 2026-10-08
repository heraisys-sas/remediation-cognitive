# Contribuer et livrer

## Branches

`main` est la version stable. `dev` est l’unique branche permanente d’intégration. Une branche temporaire part de `dev` et sa PR cible `dev`. Après revue du changement, résolution des défauts matériels et CI verte sur le dernier commit, fusionner cette PR puis supprimer sa branche distante. Ne pas conserver de branches intermédiaires de longue durée.

Livrer par une PR `dev` → `main`, avec CI verte et essai fonctionnel local des parcours modifiés. La revue peut être réalisée par l’utilisateur ou un agent autorisé ; aucun nombre obligatoire de reviewers n’est imposé au POC. Toute fusion doit rester autorisée dans le contexte de la tâche. Pas de force push sur `dev` ou `main`, ni de modification courante poussée directement sur ces branches.

## Commencer un changement

Depuis un checkout propre, après lecture de `AGENTS.md` :

```sh
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c correction-description
```

Si `dev` n’existe pas localement, utiliser `git switch --track origin/dev` à la place de `git switch dev`. Si le checkout contient un travail actif ou non commité, ne pas changer de branche ni le réinitialiser : utiliser un checkout distinct. Ne pas utiliser `stash` pour masquer le travail d’un autre agent.

```sh
git push -u origin correction-description
gh pr create --base dev
```

Décrire le problème, le comportement final et les vérifications. Toute modification du contenu servi respecte les identifiants et historiques : [contenu versionné](docs/30-technique/contenu-versionne.md). Les changements d’API ou de conception structurants sont documentés dans un ADR.

## Validation et fusion vers dev

La CI conserve Ruff, pytest, validateurs de contenu/réponses/interface, scénarios JavaScript et vérifications de syntaxe. Vérifier la CI sur le dernier commit, pas sur une version antérieure. Ajouter les contrôles adaptés au changement et corriger les défauts avant fusion.

```sh
gh pr checks NUMERO
gh pr merge NUMERO --squash --delete-branch
```

Le squash est réservé aux branches temporaires. Les preuves de validation et limites des essais sont consignées dans la PR. Une CI verte ne remplace pas un essai du micro, des ressources Apple ou du comportement réel de l’interface quand ces fonctions changent.

## Livraison dev vers main

```sh
gh pr create --base main --head dev --title "Livraison : description"
```

Réaliser les essais concernés avec le code de `dev` : démarrage et fin de séance, parcours modifiés, lecture des consignes et dictée locale si impactées. Une version à essayer n’est pas annoncée comme stable avant cette étape.

Après validation et autorisation de livraison :

```sh
gh pr checks NUMERO_LIVRAISON
gh pr merge NUMERO_LIVRAISON --merge
```

Utiliser un **merge commit**, pas un squash de `dev`, pour conserver l’ascendance commune entre branches permanentes. Ne jamais supprimer `dev` après livraison. Les corrections urgentes de `main` sont reportées dans `dev` par PR avant le prochain cycle ; ne pas laisser les branches diverger silencieusement.

## Lancer la bonne version localement

Choisir `main` pour l’usage stable ou `dev` pour les essais. Arrêter le serveur avant de changer de branche. Dans un checkout propre :

```sh
git fetch origin
git switch main  # ou dev pour l’essai
git pull --ff-only origin main  # ou origin dev
```

Utiliser le Python déjà équipé des dépendances du projet. Si l’accompagnement Apple est installé dans ce checkout :

```sh
.local/apple-fm-venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8766
```

Sinon, `python3 -m uvicorn …` lance les exercices mais peut ne pas fournir l’accompagnement Apple. Le [SDK Apple](docs/30-technique/accompagnement-apple-local.md) est installé dans un environnement Python ; la [dictée](docs/30-technique/dictee-locale-apple.md) utilise un adaptateur Swift distinct dans `.local/bin`. Ces fichiers locaux ignorés par Git restent en place lors d’un changement de branche dans **le même checkout**. Un nouveau checkout ne les reçoit pas automatiquement.

Recharger `/ui/` avec ⌘⇧R et commencer une nouvelle séance après mise à jour. Ne pas recopier ni réinterpréter automatiquement les historiques personnels. Un checkout sale ou un échec de `pull --ff-only` demande un examen des changements, pas un reset destructif.

## Transition du 8 octobre 2026

`dev` est créée depuis `main` au commit `8b3510b`. La PR #23 cible `dev` et y apporte la correction du rappel final des contextes et la remise en cohérence du backlog. Ces changements ne sont pas livrés sur `main` par la création de `dev` : la PR de livraison et les essais restent nécessaires. Décision : [ADR-040](docs/30-technique/adr/ADR-040-flux-dev-main.md).
