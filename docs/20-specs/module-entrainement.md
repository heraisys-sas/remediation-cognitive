# Spécification — Module Entraînement (hors MDR)

Vocabulaire neutre, ludique modéré. Même moteur que la rééducation ; aucune revendication clinique ; diffusable librement dès maintenant.

## Calcul mental — automatismes utiles et numératie du quotidien

- Paliers fins par famille (faits de base, stratégies, mémoire de travail, argent, quantités), répétition espacée FSRS, feedback immédiat. Décision : ADR-011.
- Représentation **soroban virtuel optionnelle** — sollicite l'imagerie visuo-spatiale plutôt que le rappel pur ; synergie utile avec la rééducation attentionnelle.
- Contenu : `content/entrainement/calcul-mental/`.

## Anglais

- Verbes irréguliers, vocabulaire — cartes FSRS.
- **Retrieval practice actif** : production (écrire, produire), pas reconnaissance.
- Interleaving une fois le socle acquis.
- Contenu : `content/entrainement/anglais/`.

## Python

- Mémorisation de **concepts** et de **commandes** du langage — thématique cognitive à **double dividende** : l'effort de mémorisation est l'exercice (rappel actif, mémoire de travail), le contenu acquis est une compétence durable.
- Formats, par item : errorless en entrée de palier → **production** (rappel actif) → **prédiction de sortie** (exécution mentale de snippets — format le plus cognitif).
- Cap de complexité : **2 niveaux d'imbrication max** en phase initiale.
- Détail complet : `content/entrainement/python/README.md`.

## Mémoire (sprint 2)

Thème dédié à la mémorisation, fondé sur les techniques classiques d'entraînement
cognitif (implémentations originales) :

- **Empan de chiffres** (endroit puis envers) : longueur 3 → 6 chiffres par palier ;
  l'envers ajoute la manipulation en mémoire de travail.
- **Sonde n-back** : rappel de l'élément situé N positions avant la fin d'une
  séquence (N = 2 → 4) — variante rappel du paradigme n-back, exigeant mais moins
  frustrant que la version oui/non continue.
- **Paires associatives mot–nombre** : 2 → 4 paires, rappel du nombre pour un mot
  sondé (apprentissage par paires, utile au quotidien : codes, rendez-vous…).

## Concentration (sprint 2)

Thème centré sur l'attention qui tient, avec **fatigue progressive conçue dans le
contenu** : la charge croît par palier (chaînes plus longues, séquences plus denses)
et la détection de fatigue existante fait le reste.

Détail des paliers : `content/entrainement/memoire/`
(généré par `tools/generer_memo_concentration.py`, déterministe ; le nom du script
est conservé pour la traçabilité des items existants).

## Transition thérapeutique → développement

Une fois les fonctions exécutives/attentionnelles stabilisées, ce module porte l'objectif « **aller au-delà de la moyenne sans mettre la barre trop haut** » : cap de difficulté adaptative avec justification pédagogique explicite — éviter l'auto-exigence excessive typique post-SPC (le patient qui veut « prouver » qu'il va bien).

## Retrouver le mot (sprint 3)

Thème d'**accès lexical** : l'information est là, le chemin pour la retrouver est encombré. On
n'apprend pas de nouveaux mots — on s'entraîne à déclencher le rappel avec de moins en moins d'aide.

- **Reconnaissance** : définitions avec trois mots de la même famille (cran d'entrée, sans échec).
- **Rappel indicé** : indices révélés **un par un** (catégorie → attaque phonologique → forme
  écrite) ; le dernier cran affiche la réponse et clôt l'essai **sans erreur**. Progression mesurée
  par le nombre d'items retrouvés **sans aide** (`resume.sans_aide`), jamais par la vitesse.
- **Rappel de la source** : fiche temporisée (contexte + information), puis question sur le
  **contexte** — mémoire de la source, souvent atteinte après une commotion.

Détail des paliers : `content/entrainement/evocation/README.md`.

## Missions dans la vraie vie (sprint 3, révisé)

Le thème d'entraînement « vie sociale » (vignettes d'émotion, réponses adaptées, lecture
d'intention) a été **retiré** : trop simple à l'usage, et redondant avec les missions.
Les **missions dans la vraie vie** sont conservées : après un isolement prolongé, c'est
l'**exposition réelle** qui agit, pas l'exercice à l'écran. Le logiciel prépare la mission,
la personne la réalise dehors, le carnet garde la trace. Détail et raisons :
`content/missions/README.md`.

## Empan de mots et rappel de séries (sprint 4)

Deux ajouts à la famille « mémoire » :

- **Empan de mots** (thème mémoire, paliers 9 à 12) : 3 → 5 mots à l'endroit, puis
  3 et 4 mots à l'envers. L'ordre est significatif, la saisie est tolérante
  (accents, casse, ponctuation).
- **Rappel de séries** (thème dédié, 4 paliers) : une série de 4 mots, puis deux et
  trois séries avec rappel **de l'ensemble** — c'est l'interférence entre séries qui
  fait la difficulté —, puis un **rappel différé** : 20 secondes d'attente avant la
  question, sur toutes les séries ou sur la première seulement.

Le rappel libre n'est pas un tout-ou-rien : chaque item déclare un **seuil** de mots
retrouvés (0,5 à 0,75), et l'interface indique ensuite ce qui a été retrouvé et ce
qui manquait. Ce retour est la valeur pédagogique de l'exercice — jamais une note.

## Rythme de présentation

Toutes les séquences à mémoriser suivent la même cadence : chaque chiffre, mot ou
lettre reste visible **2 secondes**, puis un blanc de **2 secondes** le sépare du
suivant. Les séries de mots lues et entendues utilisent déjà cette pause ; pour
l'audio, elle commence à la fin du fichier prononcé. L'interface annonce le rythme
et le validateur exige explicitement les deux durées afin qu'un nouveau palier ne
réintroduise pas une présentation plus rapide.

## Programme de 8 semaines (sprint 5)

Cadre temporel **proposé**, jamais imposé : 8 semaines × 7 jours avec 5 séances,
1 journée légère et 1 jour de repos par semaine ; durée de 6 à 9 minutes selon la
semaine ; rotation des thèmes pour alterner les domaines.

Chaque semaine porte un **plafond de palier** par thème — borne haute de complexité
(2 en semaine 1, 9 en semaine 8, ramenée aux paliers disponibles). Ce plafond n'est
jamais un objectif : l'avancement reste piloté par la maîtrise (90 % × 3 séances) et
par la fatigue. Une journée manquée ne se rattrape pas ; après deux séances sous
50 % de réussite sur un thème, le palier courant est repris avant toute nouvelle
montée en complexité.

L'écran « Programme » de l'interface montre le plan du jour (thème proposé, durée,
borne de palier), la vue d'ensemble des huit semaines et les règles en clair. Détail
du contenu : `content/programmes/README.md`.
