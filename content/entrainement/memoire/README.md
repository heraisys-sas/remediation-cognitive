# Module Mémoire (Entraînement — hors MDR)

**Principe** : entraîner la mémoire de travail et la mémorisation par les familles classiques des techniques d'entraînement cognitif — empan, apprentissage par paires, sonde n-back. Implémentations originales : la logique des paradigmes est assimilée.

## Familles

- **Empan de chiffres** (endroit puis envers) : longueur 3 → 6 chiffres par paliers ; l'envers ajoute la manipulation en mémoire de travail. Affichage séquentiel, 800 ms par élément.
- **Paires associatives mot–nombre** : 2 → 4 paires de mots concrets courants, affichage en liste (16 s), puis rappel du nombre associé à un mot sondé — entraîne une compétence utile au quotidien (codes, rendez-vous, cours).
- **Sonde n-back** : rappel de l'élément situé N positions avant la fin d'une séquence de lettres (N = 2 → 4) — variante « rappel » du paradigme n-back, exigeante mais moins frustrante que la version oui/non continue.

## Structure

- `paliers.json` — manifest des 8 paliers (id, description, prerequis, nb_items)
- `paliers/palier-01..08.json` — 18 items par palier, soit **144 items**

## Réponses attendues

- empans : chaîne de chiffres (les espaces de saisie sont ignorés côté serveur) ;
- n-back : lettre (casse ignorée) ;
- paires : nombre.

## Génération

Contenu produit par `tools/generer_memo_concentration.py` (déterministe, graine 20260904). Toute retouche manuelle d'un item doit mettre à jour `meta.relecture_ortho` (relecture orthographique et clinique avant diffusion large).

## Moteur

Identique aux autres thèmes : paliers (90 % × 3 séances), FSRS, détection de fatigue. L'affichage temporisé (phase de mémorisation distincte de la question, stimulus masqué avant la saisie) est pris en charge par l'interface ; le temps de mémorisation ne compte pas dans `temps_ms`.

## Empan de mots (sprint 4, paliers 9 à 12)

Même logique que l'empan de chiffres, avec du matériel verbal : trois à cinq mots
courts présentés un par un, à retranscrire **dans l'ordre** (puis à l'envers aux
paliers 11 et 12). L'ordre est significatif : la comparaison se fait mot à mot,
sans accents ni casse.

- palier 9 : 3 mots, endroit · palier 10 : 4 mots, endroit · palier 11 : 5 mots,
  endroit · palier 12 : 3 et 4 mots, envers.
- Le rappel verbal est sensible à la similarité phonologique et au sens : le pool
  est concret, court, et sans doublon dans une même séquence.

## Rythme d'affichage (correctif sprint 4)

Le rythme est d'environ **un élément par seconde** : 800 ms pour un chiffre,
900 ms pour un mot, plus un **blanc de 120 ms** qui ne sert qu'à séparer
visuellement les éléments — ce n'est pas une pause d'attente. L'interface affiche
désormais le rythme explicitement (« 3 éléments · un toutes les 0,92 s ») au lieu
d'une durée approximative qui pouvait se lire comme un temps de pause. Le
validateur borne ce rythme entre 400 et 2000 ms par élément.
