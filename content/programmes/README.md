# Programme de 8 semaines (`8-semaines.json`)

**Principe** : le programme décrit **ce qui est proposé** chaque jour — jamais ce qui est exigé. Il donne un rythme, une rotation de thèmes et une borne de difficulté hebdomadaire ; ce qui décide réellement de l'avancement d'un palier, c'est la **maîtrise** (90 % de réussite sur 3 séances consécutives) et la tolérance à la fatigue. Aucun palier n'est forcé par le calendrier.

## Structure

- **8 semaines × 7 jours = 56 jours** (environ deux mois).
- **Rythme hebdomadaire** : 5 séances · 1 journée légère (« au choix », plus courte) · 1 jour de repos.
- **Durée** : 6 minutes les deux premières semaines, +1 minute toutes les deux semaines, plafonnée à 9 minutes (jamais plus de 10).
- **Rotation des thèmes** : calcul mental → mémoire → attention fonctionnelle → accès au mot → méthodes / rappel de séries, avec un décalage d'une semaine à l'autre pour que le même thème ne tombe pas toujours le même jour.
- **`plafond_palier`** (par thème et par semaine) : borne haute de complexité. Semaine 1 : palier 2 au plus ; semaine 8 : palier 9 au plus — ramené au nombre de paliers réellement disponibles dans chaque thème.

## Pourquoi cette montée en complexité

La progressivité est une bonne pratique établie (paliers très fins, reprise sans échec, répétition espacée, alternance des domaines après consolidation) : elle est déjà portée par le contenu et le moteur. Le programme ajoute seulement un **cadre temporel lisible** :

| Semaine | Durée | Plafond de palier |
|---|---|---|
| 1–2 | 6 min | 2 puis 3 |
| 3–4 | 7 min | 4 puis 5 |
| 5–6 | 8 min | 6 puis 7 |
| 7–8 | 9 min | 8 puis 9 |

Trois garde-fous sont explicites dans le fichier (`regles`) :

1. **La maîtrise prime** — un palier non maîtrisé se reprend, même si le plafond de la semaine est plus haut.
2. **La fatigue est respectée** — la proposition d'arrêt en fin de séance reste une proposition, et une séance peut être close à tout moment.
3. **Pas de dette** — une journée manquée ne se rattrape pas : le programme reprend au jour suivant.

Le champ `recul` précise qu'après deux séances sous 50 % de réussite sur un thème, le palier courant est repris avant toute nouvelle montée en complexité.

## Validation

Le fichier est vérifié par `tools/validate_items.py` : 8 semaines, 7 jours par semaine, thèmes réellement jouables, séance = un seul thème (alternance), jour de repos sans thème, plafonds cohérents avec les paliers disponibles, durées bornées.

## Génération

`tools/generer_programme.py` — aucune part aléatoire : le programme est reproductible à l'identique.
