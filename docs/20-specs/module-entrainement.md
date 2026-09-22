# Spécification — Module Entraînement (hors MDR)

Vocabulaire neutre, ludique modéré. Même moteur que la rééducation ; aucune revendication clinique ; diffusable librement dès maintenant.

## Calcul mental / tables

- Paliers très fins (Kumon), répétition espacée FSRS, feedback immédiat.
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
cognitif (implémentations originales — aucun matériel protégé copié) :

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

- **Calcul chaîné** : additions/soustractions bout à bout, évaluées de gauche à
  droite, 3 → 7 opérations — le total courant doit être maintenu en mémoire de
  travail, sans rien poser. Famille des tâches de calcul sériel (logique PASAT
  assimilée ; protocole NON copié : visuel, rythme libre, opérations variables).
- **Cascade de soustractions** : départ − pas répété (départ et pas variables) —
  automatisation de la soustraction sous charge.
- **Double tâche de filtrage** : suite mêlant lettres et chiffres (affichée
  temporisée), puis « somme des chiffres » ou « nombre de lettres » — attention
  divisée et sélective (logique d2 assimilée, originale).
- **Séries à règle** : nombre manquant dans une suite arithmétique, géométrique ou
  alternée — mémoire de travail et vitesse.

Détail des paliers : `content/entrainement/memoire/` et `content/entrainement/concentration/`
(générés par `tools/generer_memo_concentration.py`, déterministe).

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

## Vie sociale (sprint 3)

Thème de **remise en lien**, pensé pour des personnes longtemps peu socialisées. Le logiciel
prépare, fait répéter à froid et garde la trace ; la mise en situation réelle reste le facteur actif.

- **Vignette d'émotion** : situation courte → émotion ressentie (trois propositions).
- **Réponse adaptée** : trois répliques (adaptée, trop directe, à côté) — demande, refus, politesse, sortie d'échange.
- **Lecture d'intention** : une parole avec son ton → ce que la personne cherche à dire.
- **Missions hors écran + carnet** : 8 missions graduées (saluer, demander une information, passer un
  appel court, proposer une rencontre…), chacune avec un pourquoi, des étapes et un repère de
  réussite modeste ; l'utilisateur réalise la mission dans la vie réelle, puis note ce qui s'est
  passé dans son carnet (stockage séparé).

Détail : `content/entrainement/social/README.md`. Précautions : pas de diagnostic, pas de norme,
aucun contenu protégé ; en cas d'isolement profond avec signes dépressifs, l'outil reste un
complément et une orientation professionnelle s'impose.

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

## Rythme de présentation (correctif sprint 4)

Les éléments d'un empan défilent à **un par seconde environ** (800 ms par chiffre,
900 ms par mot) ; le blanc inter-éléments (120 ms) ne sert qu'à séparer visuellement
les éléments, ce n'est pas une pause d'attente. L'interface annonce le rythme
explicitement, et le validateur borne ce rythme (400–2000 ms) : une pause d'attente
déguisée en empan ne peut plus entrer dans le contenu.
