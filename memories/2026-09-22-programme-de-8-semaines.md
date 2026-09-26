# 2026-09-22 — Programme d'entraînement de 8 semaines (sprint 5)

## Demande

« Génère 2 mois d'exercices avec complexification éventuelle si c'est dans les bonnes pratiques. »

## Lecture retenue

Deux mois d'entraînement ne demandent pas 1 500 items de plus : le contenu existant (691 items, 31 paliers) couvre largement 8 semaines grâce à la répétition espacée. Ce qui manquait, c'est le **cadre** : quoi faire chaque jour, à quelle intensité, avec quelle borne de difficulté — et sans transformer ce cadre en obligation.

## Livré

- `content/programmes/8-semaines.json` + `content/programmes/README.md` : 8 semaines × 7 jours, 5 séances / 1 journée légère / 1 repos, durée 6 → 9 min (+1 min toutes les 2 semaines), rotation des thèmes avec décalage hebdomadaire, plafond de palier par thème (borne), bloc `regles` (maîtrise prioritaire, fatigue, pas de rattrapage, alternance, durée, recul).
- `tools/generer_programme.py` (déterministe) et validation étendue dans `tools/validate_items.py` (séance = un seul thème, repos sans thème, plafonds ≤ paliers disponibles, thèmes réellement jouables).
- `GET /api/programme` (+ logique pure `domain/programme.py`, stockage `storage/programme.py` limité à la date de début) et `domain/contenu.programme()`.
- Écran « Programme » : plan du jour avec démarrage direct, vue des 8 semaines, règles.
- 4 tests (plan du jour, avancement calendaire — journée légère et repos compris —, stabilité de la date de début, fin de programme) → 114 tests au total.

## Choix de conception (les bonnes pratiques, appliquées)

- **La maîtrise prime sur le calendrier** : le plafond hebdomadaire est une borne. Un palier non maîtrisé se reprend, même si la semaine « autorise » plus haut.
- **Pas de dette** : une journée manquée ne se rattrape pas — sinon le programme fabrique exactement le sur-engagement que le garde-fou clinique cherche à éviter.
- **Aucune observance mesurée** : pas de taux de complétion, pas de série de jours consécutifs. Le programme propose un rythme, il ne note pas la personne.
- **Recul explicite** : deux séances sous 50 % de réussite sur un thème → reprise du palier courant avant toute nouvelle montée.
- **Journée légère « au choix »** : elle laisse la main à l'utilisateur (y compris les thèmes Extra) — c'est le seul moment où le programme ne désigne pas de thème.

## Pièges rencontrés

- Deux fois dans ce sprint, mon `edit` a visé le mauvais fichier (label de thème cherché dans `contenu.py` au lieu de `messages.py`, refs d'interface dans `index.html` au lieu de `app.js`) : les edits sont atomiques, donc rien n'a été appliqué à moitié — bon rappel de toujours vérifier le fichier cible.
- Un doublon de fonction `fetchSocial` a été introduit en généralisant les appels annexes : supprimé au profit de `fetchJson(base, chemin)`.

## Reste à faire

- Relecture orthophoniste du programme (formulations, rythme, plafonds) — c'est le seul contenu « de cadrage » à faire valider tel quel.
- Ne jamais exposer de taux d'observance, même si la tentation est forte côté produit.

## 2026-09-26 — la répétition espacée revoyait tout le même jour

Signalement : « impression de retrouver plusieurs fois la même série ».

- Diagnostic par les données : dans méthodes, les 12 cartes du palier étaient **toutes dues**
  avec des échéances à **10 minutes** — et le palier compte 12 items pour 12 servis par séance.
- Cause : pas d'apprentissage FSRS par défaut (1 min / 10 min), hérités des applications de
  révision continue. Ici, l'unité est la **séance quotidienne**.
- Correctif : pas à l'échelle du jour (bon → 2 j, échec → lendemain, facile → 8 j) ; une séance
  vide ne consomme pas le quota et n'est pas historisée (pas de recul de palier).
- Leçon : un moteur de répétition espacée doit être réglé sur **le rythme réel d'usage** du
  logiciel. Des pas par défaut pensés pour une révision continue produisent, dans une
  application quotidienne, l'effet inverse de celui recherché : de l'entassement.
- Méthode qui a payé : lire les données réelles (cartes, échéances) plutôt que raisonner sur
  le code seul — l'anomalie était visible en trois lignes.
