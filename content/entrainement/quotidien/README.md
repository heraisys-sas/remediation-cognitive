# Module « Au quotidien » (remédiation fonctionnelle — hors MDR)

**Principe** : contrairement aux épreuves d'évaluation (empan, n-back, séries…), ces exercices travaillent la fonction **altérée dans des situations de vie**, avec une **stratégie enseignée** par la consigne — voir `docs/10-clinique/remediation.md`.

## Familles

- **Prise de message** (`prise-message`, palier 1) — mémoire de travail fonctionnelle : retenir *qui / quoi / quand* le temps d'agir, puis répondre à une question ciblée. Astuce enseignée : « regroupe les informations : qui, quoi, quand, où ».
- **Étape suivante** (`etape-suivante`, palier 2) — planification : choisir la prochaine étape d'une tâche (préparer un repas, renouveler une ordonnance, envoyer un colis…). Astuce : « qu'est-ce qui doit venir avant le reste ? ».
- **Estimation de durée** (`estimation-temps`, palier 3) — anticipation : estimer le temps d'une action. La réponse est acceptée dans une **fourchette** : une estimation n'est pas une mesure exacte.

## Structure

- `paliers.json` — manifest des 3 paliers
- `paliers/palier-01..03.json` — 12 items par palier, soit **36 items**

## Réponses attendues

- `prise-message` : texte tolérant (accents, casse, espaces, ponctuation) — la réponse est un fait **présent dans le message** affiché ;
- `etape-suivante` : la proposition choisie ;
- `estimation-temps` : un nombre de minutes, accepté dans `reponse.intervalle` (bornes incluses).

## Garde-fous

- La réponse d'un `prise-message` doit figurer dans le message affiché — contrôle bloquant du validateur (une question introuvable serait un exercice mal formé).
- L'estimation est volontairement large : on ne juge pas la précision, on entraîne la comparaison avec une situation vécue.

## Génération

`tools/generer_quotidien.py` (déterministe, graine 20260923 ; mélange des propositions isolé par famille). Relecture orthophoniste formelle à faire.

## Suite naturelle

Ces trois familles sont les premières d'une série plus large : « par où commencer », « remettre les étapes dans l'ordre », « repérer une information dans un courrier », « prévoir un rappel » (mémoire prospective). La règle reste la même : **à quoi ça sert demain ?**
