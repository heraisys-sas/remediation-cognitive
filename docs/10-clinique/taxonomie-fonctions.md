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

Chaque item du contenu (`content/schema-item.json`) porte `fonctions_ciblees` et `prerequis` — la source de vérité du graphe.
