# Missions dans la vraie vie (hors écran)

**Pourquoi ces missions existent.** Ce n'est pas l'exercice à l'écran qui rétablit le lien : c'est l'**action réelle**. Après une longue période de retrait — isolement, convalescence, évitement — les automatismes sociaux s'érodent (saluer, demander, engager, terminer un échange) et une anticipation négative s'installe (« ça va mal se passer »). Ce qui agit, dans la littérature, c'est la **remise en situation progressive et répétée**, pas la connaissance des règles sociales.

D'où la répartition des rôles :

- **le logiciel prépare et suit** — il propose la mission, aide à préparer les phrases, garde la trace ;
- **la personne réalise dehors** — c'est là que le lien se rétablit ;
- **le carnet** conserve ce qui s'est passé, sans note ni comparaison.

> Le thème d'entraînement « vie sociale » (vignettes d'émotion, choix de la réponse adaptée, lecture d'intention) a été **retiré** : jugé trop simple à l'usage, et il faisait doublon avec ces missions. Les missions, elles, sont conservées — c'est l'exposition réelle qui agit.

## Les 8 missions

Quatre niveaux, du plus simple au plus engageant. Chacune porte un **pourquoi**, des **étapes** de préparation et un **repère de réussite** volontairement modeste.

| Niveau | Missions |
|---|---|
| 1 | Saluer une personne croisée ; demander une information simple |
| 2 | Répondre à un message en attente ; passer un appel court |
| 3 | Proposer une rencontre courte ; participer sans parler |
| 4 | Reprendre contact avec une personne perdue de vue ; demander de l'aide |

Aucune mission n'a de réponse attendue : le logiciel ne note pas la vie sociale.

## Le carnet

Après chaque mission, une note libre et un ressenti facultatif (facile, moyen, difficile, inattendu), conservés dans un **stockage séparé** des données d'entraînement (`backend/data/journal/`) — le carnet contient des éléments de vie privée.

## Précautions

Aucun diagnostic, aucune norme, aucun vocabulaire clinique. En cas d'isolement profond accompagné de signes dépressifs ou anxieux, l'application reste un **complément** : une orientation professionnelle s'impose.

## Génération

`tools/generer_evocation.py` (les missions y sont émises avec le contenu d'accès au mot) — déterministe. Relecture orthophoniste à faire.
