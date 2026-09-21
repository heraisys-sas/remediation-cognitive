# Module « Retrouver le mot » (évocation — hors MDR)

**Principe** : entraîner l'**accès** à ce qui est déjà su. L'information est présente en mémoire, mais le chemin pour la retrouver est encombré : au lieu de réapprendre, on s'entraîne à déclencher le rappel avec de moins en moins d'aide. C'est le pendant pratique de la récupération indicée et de l'apprentissage sans erreur.

## Familles

- **Reconnaissance** (palier 1, 5) : la définition est affichée, la réponse se choisit parmi trois mots de la même famille — cran le plus facile, pour entrer sans échec.
- **Rappel indicé** (paliers 2, 3, 5) : la définition est seule ; l'utilisateur demande des indices **un par un** (catégorie → attaque phonologique → forme écrite). Le dernier cran affiche la réponse : l'essai se clôt alors **sans erreur** (le moteur l'enregistre comme non retrouvé, sans jamais signaler un échec).
- **Rappel de la source** (palier 4) : une fiche (contexte + information) est affichée de façon temporisée ; le stimulus disparaît, la question porte sur **le contexte dans lequel l'information a été vue** — entraîne la mémoire de la source.

## Structure

- `paliers.json` — manifest des 5 paliers (id, description, prerequis, nb_items)
- `paliers/palier-01..05.json` — 10 items par palier, soit **50 items**

## Réponses attendues

- texte, comparé **sans tenir compte de la casse, des accents, des espaces et des guillemets** : un mot juste écrit sans accent reste juste (l'objectif est le rappel, pas l'orthographe) ;
- pour les items à choix, la réponse est la proposition sélectionnée.

## Garde-fous du contenu

- **Aucun indice ne contient la réponse** — contrôle automatisé dans `tools/validate_items.py` ; la révélation complète est un mode d'interface, pas un indice de plus.
- Les indices sont hiérarchisés et facultatifs : demander de l'aide fait partie de l'exercice, il n'y a pas de pénalité.
- Mesure utile côté séance : nombre d'items retrouvés **sans aide** (`resume.sans_aide`) et essais clos par affichage (`resume.assistees`).

## Génération

Contenu rédigé puis assemblé par `tools/generer_evocation_social.py` (déterministe, graine 20260920). Toute retouche manuelle met à jour `meta.relecture_ortho` ; la relecture orthophoniste formelle reste à faire.
