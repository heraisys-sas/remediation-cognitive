# Cadre d'usage et précautions (hors dispositif médical)

Ce document fixe la limite entre ce que le logiciel **fait** (un entraînement cognitif, hors dispositif médical) et ce qu'il **ne fait pas** (aucun diagnostic, aucun score normé, aucune évaluation clinique). Il sert de référence à la relecture orthophoniste et au cadrage produit.

## Ce que le logiciel est, et n'est pas

**Est.** Un outil d'entraînement : séances courtes (≤ 10 min), progression par paliers fins, répétition espacée, aide progressive, détection de fatigue qui **propose** l'arrêt.

**N'est pas.** Un dispositif médical, un bilan, un outil de diagnostic ou de suivi clinique. Aucun score n'est comparé à une norme ; aucun résultat n'est présenté comme une mesure d'une fonction. Le module Bilan, quand il existera, sera un périmètre distinct (ADR-002) avec ses propres garde-fous.

## Vocabulaire (garde-fou central)

Deux registres étanches, centralisés dans `backend/app/domain/messages.py` :

- **entraînement / social / rééducation** — vocabulaire neutre et chaleureux : « séance », « réussite », « question », « on y reviendra »… Jamais « test », « score », « trouble », « norme ».
- **bilan** — vocabulaire clinique et disclaimers professionnels, réservé à l'usage familial et à l'export vers un professionnel.

Le contrôle `tools/verifier_clinique.py` vérifie en continu que le vocabulaire non médical ne contient aucun terme clinique ou normatif.

## Précautions par famille d'exercices

| Famille | Ce qu'elle sollicite | Précautions |
|---|---|---|
| Empan de chiffres / de mots | mémoire de travail | Ne jamais chronométrer le rappel (la vitesse n'est pas l'objectif) ; arrêter dès que la séquence devient source de frustration |
| n-back | mémoire de travail + attention soutenue | Exigeant : ne proposer qu'après un socle acquis (prérequis déjà posés) |
| Chaînes de calcul, cascades | attention soutenue, automatisation | Charge soutenue : la fatigue est attendue, elle est **proposée** comme pause, jamais imposée |
| Double tâche | attention divisée / sélective | La plus coûteuse : la proposer en début de séance, jamais en fin |
| Rappel libre de séries | récupération sans indice | Le résultat est **partiel par nature** : c'est un repère de travail, jamais un score |
| Retrouver le mot (indices) | accès lexical | Demander de l'aide fait partie de l'exercice, sans pénalité ; l'essai se clôt sans erreur |
| Missions dans la vraie vie | exposition réelle (le facteur qui agit) | Préparation à froid seulement ; la réalisation se fait dehors, et se note dans le carnet |

## Signes d'alerte (non diagnostiques) — quand en parler à un professionnel

Le logiciel n'interprète rien, mais il oriente. Si, pendant l'usage, une de ces situations revient souvent, l'utilisateur est invité à en parler à son médecin ou à son orthophoniste :

- l'entraînement devient **de plus en plus difficile** malgré la régularité ;
- des **maux de tête**, des nausées ou une sensibilité à la lumière **aggravent** pendant ou après les séances ;
- l'**humeur baisse** durablement, ou le sommeil se dégrade ;
- les difficultés rencontrées à l'écran se retrouvent de façon gênante **dans la vie quotidienne**.

Ces repères sont génériques et volontairement non cliniques : ils signalent « parlez-en », jamais un diagnostic.

## Relecture orthophoniste

Tout item porte `meta.relecture_ortho` avec un statut :

- `a_revoir` — à relire (défaut à la génération) ;
- `relecture_en_cours` — en cours de relecture ;
- `valide_informel` — relu, **sans valeur de validation clinique**, et obligatoirement **daté** (une validation non datée est refusée par le contrôle).

La relecture est **informelle** : elle vérifie la justesse et la formulation, elle n'est jamais présentée comme une validation clinique du logiciel.

## Références

- `tools/verifier_clinique.py` — contrôle automatique des garde-fous (vocabulaire, photophobie, matériel protégé, relecture).
- `docs/10-clinique/fondements.md`, `protocoles.md`, `taxonomie-fonctions.md` — assise des familles et de la progression.
- `docs/30-technique/adr/ADR-002` (séparation des stockages), `ADR-004` à `006` (aides, rappel, programme).
