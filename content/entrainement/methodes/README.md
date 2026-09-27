# Module « Méthodes » (méthodes et stratégies — hors MDR)

**Principe** : ici on n'entraîne pas une fonction par la répétition, on installe une **méthode** que l'on pourra réutiliser partout — lire avec une intention, poser son but avant d'agir, se parler pour se guider. Trois méthodes éprouvées :

| Palier | Méthode | Ce qui est entraîné |
|---|---|---|
| 1 | **PQRST** — Parcourir, Question, Lire, énoncer, Tester | mémoire de textes : **deux questions de mémoire par texte** |
| 2 | **Goal Management Training** — but, étapes, vérification | planification : choisir le plan d'étapes cohérent |
| 3 | **Auto-instruction** (Meichenbaum) — « qu'est-ce que je dois faire ? comment ? vérifie » | autorégulation : la question à se poser avant d'agir |
| 4 | **Vérification de plan** — le « V » de GMT | relire un plan ordonné et repérer l'étape mal placée |
| 5 | **Repérer l'information** — attention sélective | trouver l'information utile dans un courrier, une notice, une affichette |

12 items au palier 1, 8 aux autres, soit **44 items**.

## Comment c'est entraîné

- **PQRST** : le texte s'affiche temporisé (25 s), puis disparaît — la question est posée de mémoire (`affichage` mode `texte`). La consigne rappelle la méthode, c'est elle qui est retenue.
- **GMT** : la situation est donnée, la bonne réponse est le **plan d'étapes cohérent** (et non une étape isolée) ; la consigne invite à vérifier son plan.
- **Auto-instruction** : la bonne réponse est la **première question à se poser** (portant sur le but et le moyen), pas sur le résultat attendu.

Toutes les réponses sont à choix, pour une correction objective. La méthode elle-même est un **fil conducteur** : un panneau « Méthode — avant de répondre » (les trois questions d'auto-instruction) est disponible à tout moment pendant les séances, toutes familles confondues.

## Génération

`tools/generer_methodes.py` (déterministe, mélange isolé par famille). Relecture orthophoniste à faire.


## PQRST mis en œuvre (palier 6, ADR-015)

Un item = **une séquence guidée** sur un texte de quatre phrases : Parcours (jugé), **Question à écrire** (non notée, modèle affiché), Lecture (sans chronomètre), **Reformulation** (jugée à **4 idées-clés sur 5**, résumé modèle montré), Test (2 questions de mémoire). Les deux productions — sa question, sa reformulation — sont ce que le palier entraîne. La **fiche méthode** (5 lignes) est reprise au résumé de séance.

## Proposition en attente

