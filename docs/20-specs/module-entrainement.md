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
