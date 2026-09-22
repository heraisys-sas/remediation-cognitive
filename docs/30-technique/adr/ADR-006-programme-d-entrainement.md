# ADR-006 — Programme d'entraînement : cadre temporel proposé, progression non contrainte

**Statut** : accepté (2026-09-22)

## Contexte

Le dépôt offre une progressivité par paliers, une répétition espacée et une détection de fatigue, mais **aucun cadre temporel** : rien n'indique quoi faire aujourd'hui, ni comment occuper deux mois d'entraînement sans monotonie ni surcharge. Demande reçue : « générer deux mois d'exercices, avec complexification si c'est dans les bonnes pratiques ».

Deux risques à éviter :

1. transformer un programme en **obligation** (« tu es en retard de trois séances ») — ce qui irait à l'encontre du garde-fou « le dosage prime sur la difficulté » et nourrirait la sur-sollicitation typique post-commotion ;
2. dupliquer dans un planning ce que le moteur fait déjà mieux (l'avancement par maîtrise).

## Décision

**1. Le programme est un contenu versionné** — `content/programmes/8-semaines.json`, généré par `tools/generer_programme.py` (aucune part aléatoire), validé par `tools/validate_items.py` :

- 8 semaines × 7 jours ; 5 séances, 1 journée légère, 1 jour de repos ;
- durée 6 → 9 minutes (+1 minute toutes les deux semaines, jamais plus de 10) ;
- rotation des thèmes (calcul, mémoire, concentration, accès au mot, social / rappel) avec décalage hebdomadaire ;
- `plafond_palier` par thème et par semaine : **borne**, jamais objectif, ramenée aux paliers réellement disponibles ;
- bloc `regles` explicite : maîtrise prioritaire, fatigue respectée, journée manquée non rattrapée, recul après deux séances faibles.

**2. L'API expose le programme et le plan du jour** — `GET /api/programme` renvoie le programme complet, le plan du jour (semaine, jour, type, thème(s), durée, plafonds) et les règles. Le repérage du jour vient de la logique pure `backend/app/domain/programme.py` (date d'entrée → plan en sortie).

**3. État local minimal, périmètre entraînement** — `backend/data/programme/programme.json` ne stocke que la **date de début**, posée à la première consultation et **jamais déplacée** par une relecture. Aucun suivi de performance, aucune donnée de santé : le programme ne mesure rien.

**4. L'interface propose, l'utilisateur décide** — l'écran « Programme » affiche le plan du jour avec un bouton de démarrage du thème proposé, la vue d'ensemble des 8 semaines et les règles en clair. Les jours de repos et les journées légères sont présentés comme tels, sans culpabilisation.

## Conséquences

- (+) Deux mois d'entraînement deviennent lisibles sans qu'aucune progression soit imposée : le moteur reste seul juge des paliers.
- (+) La montée en complexité est encadrée par un plafond hebdomadaire et une règle de recul, conformes aux protocoles du dépôt (paliers fins, errorless, fatigue).
- (+) Le programme est un contenu versionné : il se relit, se valide et se régénère comme le reste.
- (−) Un troisième état local (date de début) à maintenir, séparé du journal (vie privée) et des données d'entraînement.
- (−) Le programme n'est pas un dispositif de mesure : aucune observance, aucun taux de complétion ne doit en être dérivé, sous peine de contredire le garde-fou « aucune norme ».
