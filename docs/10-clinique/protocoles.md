# Protocoles et règles de dosage

## Séance

- Durée **5–10 min** ; limite de sessions/jour paramétrable.
- **Alerte de fatigue** si le temps de réaction se dégrade ou que le taux d'erreur grimpe en cours de session → proposition d'arrêt, **jamais forcée**, mise en avant dans l'UI.
- **Journal de charge perçue** en fin de session : 1 item auto-rapporté (type NASA-TLX simplifié) pour corréler subjectif/objectif et ajuster le dosage.

## Dosage par thème : même durée, moins d'exercices

Le cadre reste **une séance courte (5-10 min)**. Ce qui change d'un thème à l'autre, c'est
le **coût d'un exercice** : on ajuste donc le *nombre* d'exercices, jamais la durée.

| Thème | Exercices par séance | Durée maximale | Pourquoi |
|---|---|---|---|
| Général (calcul mental, mémoire, évocation, quotidien…) | 12 | 10 min **proposées** | items courts, enchaînables |
| **Déduction** | **6** | 10 min **proposées** | chaque grille demande une chaîne de raisonnement complète (mémoire de travail + fonctions exécutives) : une grille dure plusieurs minutes, douze ne tiendraient pas dans une séance |

Trois choses ne bougent pas, quel que soit le thème :

- la **durée maximale** (dix minutes) est **une proposition**, partout (ADR-010) : au-delà, la
  séance invite à s'arrêter — elle ne se ferme pas d'elle-même, la personne décide. Le garde-fou
  de sur-sollicitation reste la **limite de séances** (3 par jour par défaut en entraînement, 6 pour Calcul mental, 1 par semaine pour l'évaluation — dérogation explicite possible, décidée par la personne, ADR-021) et le nombre d'exercices par séance
  (anti-syndrome du patient qui veut « prouver » qu'il va bien) ;
- la **fatigue** reste une **proposition** d'arrêt, jamais une interruption ;
- une séance qui atteint sa limite **termine proprement** : la réponse en cours est conservée,
  le résumé est proposé (voir `docs/30-technique/api-contract.md`).

*À revoir avec l'orthophoniste : si des séances de déduction plus longues sont utiles pour
certains profils, c'est une exception à documenter ici explicitement (durée, profil, justification).*

## Progression par paliers fins

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

Les familles de mémorisation intègrent la montée en charge **dans les
items eux-mêmes** : la taille des empans (3 → 6 chiffres) croît par palier. Conséquences :

- la charge augmente par la longueur et la manipulation demandée ;
- l'affichage temporisé (phase de mémorisation) ne compte PAS dans `temps_ms` :
  seul le temps de réponse est mesuré.

## Bilan de charge (vérification)

Chaque évolution de palier ou de dosage doit être revue à l'aune de la CLT : la charge extrinsèque (interface, consignes, contexte) doit rester minimale pour laisser la capacité disponible à la tâche elle-même.

## Cadre temporel proposé sur deux mois (sprint 5)

Le programme de 8 semaines formalise la progressivité attendue : paliers fins,
reprise sans échec, répétition espacée, alternance des domaines — et il ajoute trois
garde-fous explicites.

1. **La maîtrise prime sur le calendrier.** Le plafond hebdomadaire de palier est une
   borne : un palier non maîtrisé se reprend, même si la semaine autorise plus haut.
2. **La fatigue est respectée.** La proposition d'arrêt reste une proposition, et une
   séance peut être close à tout moment (garde-fou inchangé).
3. **Pas de dette.** Une journée manquée ne se rattrape pas : le programme reprend au
   jour suivant, sans cumul. Le rythme prévoit d'ailleurs une journée légère et un
   jour de repos par semaine.

Le recul est explicite : après deux séances consécutives sous 50 % de réussite sur un
thème, le palier courant est repris avant toute nouvelle montée en complexité. Aucune
observance, aucun taux de complétion n'est calculé : le programme propose un rythme,
il ne mesure pas la personne.
