# Protocoles et règles de dosage

## Séance

- Durée **5–10 min** ; limite de sessions/jour paramétrable.
- **Alerte de fatigue** si le temps de réaction se dégrade ou que le taux d'erreur grimpe en cours de session → proposition d'arrêt, **jamais forcée**, mise en avant dans l'UI.
- **Journal de charge perçue** en fin de session : 1 item auto-rapporté (type NASA-TLX simplifié) pour corréler subjectif/objectif et ajuster le dosage.

## Progression (Kumon-like)

- Critère de maîtrise par défaut : **90 % de réussite sur 3 sessions consécutives** (paramétrable).
- Entrée de palier en **mode errorless** ; bascule vers l'essai-erreur guidé une fois la fatigabilité réduite (paramètre modifiable avec garde-fou).
- Pas de passage au niveau suivant sans maîtrise fluide.

## Caps de difficulté

- Cap configurable avec **justification pédagogique explicite** (anti sur-sollicitation post-commotionnelle — éviter le syndrome du patient qui veut « prouver » qu'il va bien).
- Python : max 2 niveaux d'imbrication dans les snippets en phase initiale.
- Aucune norme populationnelle affichée à l'utilisateur.

## Bilan

- Batterie 15–20 min, **fractionnable** pour éviter la fatigue.
- Mêmes épreuves toutes les 2 semaines → courbe de récupération.
- Scores bruts + trajectoire personnelle uniquement (côté patient).

## Fatigue progressive conçue dans le contenu (sprint 2)

Les familles mémorisation/concentration intègrent la montée en charge **dans les
items eux-mêmes** : la longueur des calculs chaînés (3 → 7 opérations) et la
taille des empans (3 → 6 chiffres) croissent par palier. Conséquences :

- la fatigue cognitive devient mesurable **au sein même d'une séance** (le RT et
  le taux d'erreur montent naturellement quand la chaîne s'allonge) — la
  détection existante fait le reste ;
- le cap de difficulté (7 opérations maximum) est posé dans les items
  (`cap_complexite`) et rappelé dans l'UI ;
- l'affichage temporisé (phase de mémorisation) ne compte PAS dans `temps_ms` :
  seul le temps de réponse est mesuré.

## Bilan de charge (vérification)

Chaque évolution de palier ou de dosage doit être revue à l'aune de la CLT : la charge extrinsèque (interface, consignes, contexte) doit rester minimale pour laisser la capacité disponible à la tâche elle-même.
