# Module Mémoire (Entraînement — hors MDR)

**Principe** : entraîner la mémoire de travail et la mémorisation par les familles classiques des techniques d'entraînement cognitif — empan, apprentissage par paires, sonde n-back. Implémentations 100 % originales : la logique des paradigmes est assimilée, **aucun matériel protégé n'est copié** (droits ECPA/Pearson).

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
