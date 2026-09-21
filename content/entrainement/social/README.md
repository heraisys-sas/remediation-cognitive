# Module « Vie sociale » (social — hors MDR)

**Principe** : préparer et consolider les échanges, jamais les remplacer. Un isolement prolongé érode des automatismes (saluer, demander, lire l'état de l'autre) et installe souvent une anticipation négative. La partie qui agit vraiment est la **remise en situation réelle, courte et répétée** — le logiciel fournit la préparation, l'entraînement à froid et le suivi.

## Familles

- **Vignette d'émotion** (paliers 1, 4) : une situation courte, puis choix de l'émotion ressentie parmi trois propositions — l'indice se trouve dans ce que fait ou dit la personne.
- **Réponse adaptée** (paliers 2, 4) : trois répliques possibles (adaptée, trop directe, à côté) ; travail de la demande, du refus, de la politesse, de la sortie d'échange.
- **Lecture d'intention** (palier 3) : une parole avec son ton (« Ça va, tu es sûr ? » — voix douce) et trois lectures possibles de l'intention.

## Missions hors écran (`missions.json`)

8 missions réelles, de niveau 1 à 4 : saluer une personne croisée, demander une information simple, répondre à un message en attente, passer un appel court, proposer une rencontre courte, participer sans parler, reprendre contact, demander de l'aide.

Chaque mission porte un **pourquoi**, des **étapes** préparatoires et un **repère de réussite** volontairement modeste (« la question a été posée à voix haute »). Aucune mission n'a de réponse attendue : le logiciel ne note pas la vie sociale.

Le **carnet** (`/api/social/journal`) conserve les notes de l'utilisateur après chaque mission, dans un **stockage séparé** des données d'entraînement (contient des éléments personnels).

## Réponses attendues

Choix parmi les propositions, comparés sans tenir compte de la casse, des accents, des espaces et des guillemets.

## Précautions

- Aucun diagnostic, aucune norme, aucun vocabulaire clinique (`backend/app/domain/messages.py`).
- Aucun contenu protégé : les situations sont originales ; les principes viennent des programmes d'habiletés sociales et de cognition sociale, jamais leur matériel.
- En cas d'isolement profond avec symptômes dépressifs ou anxieux : l'application reste un complément, une orientation professionnelle s'impose.

## Génération

Contenu rédigé puis assemblé par `tools/generer_evocation_social.py` (déterministe, graine 20260920). Relecture orthophoniste formelle à faire.
