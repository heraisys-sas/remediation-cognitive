# Remédiation cognitive

Proof of concept de laboratoire pour des adultes présentant des difficultés cognitives après un traumatisme crânien, notamment un syndrome post-commotionnel. Le logiciel propose des exercices de remédiation et d’entraînement, en complément des séances accompagnées et pour élargir les activités utilisables en séance.

Le public visé peut avoir un niveau intellectuel antérieur élevé : progression, consignes et contenus doivent rester stimulants, avec un rythme ajustable. Le logiciel s’utilise localement, sur un poste mono-utilisateur. Il ne constitue pas un bilan standardisé ni un outil diagnostique validé.

## Ce qui fonctionne aujourd’hui

- **Déduction** : placement de formes à partir d’indices croisés ; cinq paliers, grilles 3×3 puis 4×4 au dernier palier.
- **Calcul mental** : opérations, stratégies et situations variées, avec progression en difficulté.
- **Retrouver des mots et leur contexte** : accès lexical à douze paliers, stratégies sémantiques/phonologiques et mémorisation de scènes. Dans le parcours « Retrouver le contexte », les premières questions accompagnent la mémorisation ; seul le rappel final alimente réussite et progression dans la version intégrée sur `dev`.
- **Méthodes pour retenir et s’organiser** : PQRST guidé, rappel, choix et vérification de plans, auto-instructions et recherche d’informations.
- **Tâches fonctionnelles** : actualiser une consigne, comparer deux documents, repérer l’essentiel, travailler des situations du quotidien et reprendre après interruption.
- **Exercices ciblés** : mémoire de travail et associations, séries de mots lues ou entendues dans des parcours séparés.
- **N-back** : comparaison successive de formes à une, deux ou trois places de distance, à rythme libre, dans Exercices ciblés.
- **Application des stratégies** : préparer un plan, utiliser un rappel, prendre un message et organiser son temps dans des simulations avec actions observables.
- **Activités complémentaires** : anglais et Python en Extra ; missions hors écran, journal et programme proposé de huit semaines.

Le moteur gère les paliers, la maîtrise, la répétition espacée FSRS et les séances. Les départs automatiques et la longueur des séances dépendent du parcours. Les aides et propositions d’arrêt accompagnent l’exercice ; les dérogations prévues sont explicites. Les comptes de séance ne sont pas des scores cliniques normés.

La carte **Mémoires immédiates** regroupe code, chemin, changement forme/couleur/association et objets à replacer ; pratique guidée, résultats descriptifs et données séparées. La progression est conservée par parcours et condition. Voir [ADR-045](docs/30-technique/adr/ADR-045-memoires-immediates.md) et [les paliers](docs/20-specs/paliers-memoires-immediates.md).

Les banques ont été enrichies pour une répartition de 65 séances sur treize semaines, à cinq séances par semaine au total, hors anglais/Python. Cela ne prolonge pas le programme logiciel de huit semaines. Voir [l’inventaire](docs/20-specs/couverture-trois-mois-inventaire.md).

Les prototypes d’attention différée, de reproduction de figures et de tâches de couleurs sont **spécifiés, pas encore implémentés**. Le bilan standardisé et l’IRT ne font pas partie du développement autorisé actuel. L’export PDF/JSON reste différé. Le module de graphe vide a été retiré ; une visualisation documentaire reliant exercices, compétences et publications citées pourra être envisagée ultérieurement, éventuellement lors d’une release. Voir la [feuille de route](docs/00-produit/feuille-de-route.md).

## Installer et démarrer

L’instance actuelle est **mono-utilisateur et sans authentification applicative**.
Conserver une écoute locale ; une exposition réseau exige un contrôle d’accès
et une isolation par instance portés par l’infrastructure. Voir le
[guide de déploiement](docs/30-technique/deploiement-local.md).

Backend Python/FastAPI, interface HTML/CSS/JavaScript sans framework ni étape de build. La CI utilise Python 3.12 et Node.js 22 ; Node sert aux contrôles de développement, pas au lancement du serveur.

Depuis un nouveau clone :

```sh
git clone https://github.com/heraisys-sas/remediation-cognitive.git
cd remediation-cognitive
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8766
```

Ouvrir [l’interface locale](http://127.0.0.1:8766/ui/). `main` est la version stable ; pour essayer les changements intégrés, utiliser un checkout propre de `dev` avant de démarrer le serveur. Le fichier `requirements-dev.txt` contient les dépendances serveur et de test avec plages de versions compatibles ; ce n’est pas un verrou des dépendances transitives.

Après une mise à jour : arrêter le serveur, mettre à jour la branche choisie sans écraser les changements locaux, relancer et recharger la page avec ⌘⇧R sur Mac. Commencer une nouvelle séance. Les commandes Git sont dans [CONTRIBUTING.md](CONTRIBUTING.md).

### Voix, dictée et accompagnement Apple

Les exercices peuvent fonctionner avec la saisie clavier. Les capacités supplémentaires sont détectées sur le poste ; aucun service distant ne doit remplacer une capacité locale indisponible.

- **Lecture** : voix du système, selon les capacités installées sur le poste.
- **Correction des réponses libres** : normalisation et variantes, puis similarité Apple NaturalLanguage si disponible, sinon repli lexical. Ces deux fournisseurs ne sont pas équivalents ; leur calibration reste un chantier ouvert ([issue #6](https://github.com/heraisys-sas/remediation-cognitive/issues/6)). Les chiffres, séries, QCM et mots stricts gardent leurs règles propres.
- **Dictée locale Apple** : adaptateur Swift, macOS 26+, Xcode/Swift adapté et ressources françaises prêtes. [Installation et diagnostic](docs/30-technique/dictee-locale-apple.md).
- **Accompagnement PQRST Apple Intelligence** : Mac compatible, Apple Intelligence activée, macOS/Xcode 26+ et SDK Python facultatif. [Préparation et limites](docs/30-technique/accompagnement-apple-local.md).

L’adaptateur de dictée est dans `.local/bin` ; le SDK est dans l’environnement Python qui lance le serveur. Un changement de branche dans le même checkout conserve ces installations ignorées par Git ; un autre checkout ne les reçoit pas automatiquement.

Si le SDK est installé dans `.local/apple-fm-venv`, lancer avec ce Python plutôt qu’avec celui d’un environnement sans SDK :

```sh
.local/apple-fm-venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8766
```

Cet environnement doit également contenir les dépendances serveur ; si nécessaire, les installer avec `.local/apple-fm-venv/bin/python -m pip install -r requirements-dev.txt`. L’installation initiale des dépendances et la préparation des ressources Apple peuvent nécessiter le réseau ; les fonctions Apple utilisées par le logiciel s’exécutent localement.

### Vérifier le moteur sémantique Apple

La similarité sémantique utilise les empreintes de phrases françaises **NaturalLanguage / NLEmbedding**, accessibles depuis Python par PyObjC. Elle ne dépend pas du SDK Apple Foundation Models ni de l’activation d’Apple Intelligence. Elle fonctionne localement quand le framework et les empreintes françaises sont disponibles, sans modèle tiers à embarquer.

Dans l’environnement Python qui lance réellement le serveur :

```sh
.local/apple-fm-venv/bin/python -c 'from backend.app.domain.capacites import fournisseur_similarite; print(fournisseur_similarite())'
```

`nle_embedding` confirme le moteur Apple ; `lexical` indique le repli. Adapter l’exécutable si le serveur utilise `.venv` ou un autre Python. Le même diagnostic est exposé par [GET /api/capacites](http://127.0.0.1:8766/api/capacites), champ `similarite.fournisseur`. `similarite.disponible = true` signifie qu’un fournisseur existe, pas nécessairement celui d’Apple.

La similarité est un recours pour des reformulations libres, après les vérifications de sens explicites. Elle ne remplace pas la correction stricte ni ne garantit la justesse d’une réponse. Les variantes, articles et petites contextualisations peuvent être reconnus par les règles déterministes même sans moteur Apple. Le seuil historique et les divergences Apple/repli restent à valider dans l’issue #6.

## Personnaliser l’accueil

Dans **Réglages → Ce que tu souhaites travailler**, coche les difficultés qui te concernent : concentration, mémoire, recherche de mots, organisation… Les cartes associées sont indiquées et le choix est conservé sur cet appareil. Toutes les cartes sont visibles par défaut. Ce filtre personnalise l’affichage, sans diagnostic ni modification de progression. Voir les [correspondances et leurs sources](docs/30-technique/accueil-difficultes.md).

## Données et contenu

- Les items et leurs paliers sont des données versionnées dans `content/`, distinctes du code. Toute modification substantielle d’un item déjà servi respecte les [règles d’identifiants et d’historiques](docs/30-technique/contenu-versionne.md).
- Le stockage de séances et de progression est local, dans `backend/data/`, ignoré par Git. Les données personnelles ne sont pas à commiter ni à recopier automatiquement entre les versions stable et d’essai.
- Les réglages du navigateur peuvent être communs à deux versions visitées sur la même adresse et le même port.
- Les relectures de contenu sont consignées dans le [journal orthophonique](docs/10-clinique/relectures.md). Les retours informels ne constituent pas une validation clinique.

## Développer et livrer

**Branche temporaire → `dev` → `main`.**

Une branche temporaire part de `dev`. Après revue et CI verte, sa PR est fusionnée dans `dev`, puis la branche temporaire est supprimée. Une PR de livraison `dev` → `main` suit les essais fonctionnels des parcours concernés, de la voix et de la dictée si elles sont impactées. `main` reste stable ; la CI seule ne déclenche pas de livraison automatique.

La CI vérifie les pushes et PR vers `dev` et `main`. [Guide de contribution](CONTRIBUTING.md), [instructions des agents](AGENTS.md), [décisions techniques](docs/30-technique/adr/ADR-040-flux-dev-main.md).

### Vérifications

Avec les dépendances de `requirements-dev.txt` et Node installés :

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check backend engine tools
.venv/bin/python tools/validate_items.py
.venv/bin/python tools/verifier_reponses.py
.venv/bin/python tools/verifier_interface.py
node tools/verifier_phrases.js
node --test tools/test_serie_contextes.cjs
```

Pour un autre environnement Python, remplacer `.venv/bin/python` par son exécutable. Ne pas régénérer le contenu servi pour vérifier une modification de code.

## Organisation du dépôt

```text
backend/    API FastAPI, correction, capacités locales et stockage
engine/     Paliers, maîtrise, séances et répétition espacée
content/    Items, manifests de paliers, missions et programme
frontend/   Interface, voix/dictée, images et audio préparé
tools/     Générateurs, validateurs et contrôles d’interface
docs/      Produit, références cliniques, spécifications et ADR
memories/   Journal factuel des changements et revues
```

Les répertoires historiques `content/bilan`, `content/reeducation`, `infra` et `docs/40-qms` ne prouvent pas la livraison de modules de bilan, d’hébergement HDS ou d’une démarche réglementaire. La feuille de route active fait référence pour les travaux prévus.

## Licence

[BSD-3-Clause](LICENSE), applicable au code et au contenu du dépôt.
