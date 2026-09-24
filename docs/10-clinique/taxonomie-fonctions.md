# Taxonomie fonctions ↔ exercices ↔ paliers ↔ prérequis

Le graphe de connaissances (`backend/app/kg/`) modélise ces relations — plutôt que des tags SQL plats.

## Fonctions cibles et priorité (rééducation)

| Ordre | Fonction | Référence | Type d'épreuve |
|---|---|---|---|
| 1 | Attention soutenue | Sohlberg & Mateer | Temps de réaction continu (type CPT) |
| 2 | Attention divisée | Sohlberg & Mateer | Double tâche simple |
| 3 | Mémoire de travail | Miyake (updating) | Empan, n-back léger |
| 4 | Flexibilité | Miyake | Trail Making adapté |
| 4 | Inhibition | Miyake | Stroop adapté |
| 5 | Planification | — | Tâches multi-étapes (type Tour de Londres adaptée) |

## Entraînement (hors MDR)

| Thème | Contenu | Moteur |
|---|---|---|
| Calcul mental / tables | Paliers Kumon-like, soroban optionnel | Adaptatif + FSRS |
| Anglais | Verbes irréguliers, vocabulaire | FSRS + production active |
| Python | Concepts, commandes, snippets | FSRS + production + prédiction de sortie |

## Chaînes de prérequis (exemples)

- **Python** : listes → compréhensions de liste ; boucles → boucles imbriquées (cap : 2 niveaux en phase initiale) ; fonctions → générateurs ; types/mutabilité → structures de données.
- **Attention** : soutenue → sélective → alternée → divisée.
- **Calcul** : tables ×2–×5 → tables ×6–×9 → opérations mixtes → soroban mental.

## Familles mémorisation & concentration (sprint 2)

| Famille | Type | Fonctions | Progression |
|---|---|---|---|
| Calcul chaîné (total courant) | chaine-calcul | attention soutenue + MDT | 3 → 7 opérations, termes croissants |
| Cascade de soustractions | chaine-calcul | attention soutenue + automatisation | pas 3–9, 5 soustractions |
| Empan de chiffres | empan | mémoire de travail | 3 → 6 chiffres, endroit puis envers |
| Sonde n-back | n-back | MDT + attention soutenue | pas 2 → 4 |
| Double tâche de filtrage | double-tache | attention divisée + sélective | 5 → 9 éléments |
| Séries à règle | serie-manquante | MDT + vitesse | arithmétique → géométrique → alternée |
| Paires associatives | paires-associatives | MDT + mémorisation longue | 2 → 4 paires |

Chaque item du contenu (`content/schema-item.json`) porte `fonctions_ciblees` et `prerequis` — la source de vérité du graphe.

## Familles « accès au mot » (sprint 3)

| Famille | Type | Fonctions | Progression |
|---|---|---|---|
| Reconnaissance lexicale | reconnaissance | accès lexical | palier 1 et 5 (cran d'entrée) |
| Rappel indicé (indices progressifs) | rappel-indice | accès lexical + récupération | paliers 2, 3, 5 — indices retirés à mesure |
| Rappel de la source | rappel-source | mémoire épisodique (source) + récupération | palier 4 |
| Missions dans la vraie vie | hors moteur | exposition réelle (le facteur qui agit) | 4 niveaux (préparation + carnet) |

Deux familles de la rééducation de l'accès lexical sont mobilisées : l'indiçage progressif
(sémantique puis phonologique) et la récupération espacée avec estompage des aides. Le principe
d'apprentissage sans erreur est porté par l'interface : l'essai se clôt en affichant la réponse,
sans imposer d'échec (ADR-004).

## Familles « empan de mots » et « rappel libre » (sprint 4)

| Famille | Type | Fonctions | Progression |
|---|---|---|---|
| Empan de mots | empan-mots | mémoire de travail (verbale) | 3 → 5 mots endroit, puis 3–4 envers |
| Rappel libre de séries | rappel-libre | récupération + mémoire épisodique | 1 série → 3 séries → rappel différé (20 s) |

Le rappel libre sollicite la **récupération sans indice** (rien n'est proposé) et
l'interférence entre séries successives ; le rappel différé ajoute la résistance au
délai. Ces épreuves produisent un résultat **partiel** par nature : le seuil déclaré
sert de repère de séance, il ne doit jamais devenir un score de mémoire comparable
entre personnes (garde-fou clinique inchangé).
