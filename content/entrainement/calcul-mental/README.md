# Calcul mental — automatismes utiles et numératie du quotidien

Paliers fins, répétition espacée FSRS, feedback immédiat. Spec : `docs/20-specs/module-entrainement.md` ; décision : **ADR-011**.

## Ce qu'on travaille, et pourquoi pas les tables dans l'ordre scolaire

Un adulte n'a rien à automatiser sur la table de 1 ni sur celle de 10 : ce ne sont pas des faits à retrouver mais des **règles** (« × 1 ne change rien », « × 10 ajoute un zéro »). Les répéter prend du temps sans rien construire. Les anciens paliers, qui couvraient une table chacun — dont × 1 — et posaient la même question dans les deux sens, sont remplacés par une progression qui suit **ce dont un adulte se sert réellement** :

1. **faits de base** — la récupération automatique libère la mémoire de travail, qui est justement la ressource fragile après une commotion ;
2. **stratégies** — doubles et presque-doubles, compléments à 10 puis à 100 : on ne récupère pas tout, on calcule à partir de repères ;
3. **mémoire de travail** — deux opérations enchaînées, résultat intermédiaire à garder ;
4. **numératie du quotidien** — argent, quantités, durées : c'est le **transfert** dans la vie réelle, qui est le but du module.

## Les neuf paliers

| Palier | Ce qui est travaillé | Exemple |
|---|---|---|
| 1 | Compléments et retraits dans 10 (faits de base) | « Combien manque-t-il à 7 pour faire 10 ? » |
| 2 | Doubles et presque-doubles (stratégie) | « Combien font 6 + 7 ? » (aide : 6 + 6 + 1) |
| 3 | Additions dans 20 | « Combien font 8 + 5 ? » |
| 4 | Soustractions dans 20 | « Combien font 13 − 5 ? » |
| 5 | Compléments à 100 (repères d'argent) | « Combien manque-t-il à 70 pour faire 100 ? » |
| 6 | Multiplications utiles × 2 à × 5 | « Combien font 4 × 7 ? » |
| 7 | Deux opérations enchaînées (mémoire de travail) | « Combien font 8 + 7 − 2 ? » |
| 8 | Au quotidien : l'argent | « Un article à 7 €, payé avec 10 € — combien te rend-on ? » |
| 9 | Au quotidien : quantités et durées | « Pour 4 personnes, 250 g ; pour 8 personnes ? » |
| 10 | **Faits difficiles (× 6 à × 9)** | « Combien font 7 × 8 ? » (aide : × 8 = double de × 4) |
| 11 | **Sens du nombre (dyscalculie)** | « Combien de dizaines dans 47 ? », « À mi-chemin entre 40 et 50 ? » |

11 paliers, **194 items**, aucun doublon d'énoncé dans un palier. Les énoncés sont des questions courtes et naturelles : on s'adresse à un adulte, pas à un enfant qui apprend ses tables.

Les paliers 2, 5, 6, 7, 8 et 9 portent une **aide** repliée (la stratégie, jamais le résultat) ; le palier 7 porte une **consigne** de méthode, affichée une fois par séance.

## Contrôle indépendant du générateur

`tools/validate_items.py` **relit chaque énoncé et recalcule la réponse** (les familles calculables : opérations, compléments, montants). Une question associée au mauvais résultat est donc refusée au dépôt, sans dépendre du code qui l'a produite. Ce contrôle a immédiatement attrapé une erreur de génération réelle (« un article à 12 €, payé avec 10 € », réponse −2).

## Génération

    python3 tools/generate_items.py [--dry-run]

Déterministe (graine fixe). Les identifiants portent un suffixe de génération (`cm2-`) : le contenu ayant été entièrement revu, il ne doit pas hériter des états de révision de l'ancien (règle de versionnage du contenu).

## Les trois publics servis (ADR-012)

- **Dyscalculie** — le palier 11 travaille le **sens du nombre** : comparer, situer, décomposer, sans opération. C'est le socle sans lequel les faits ne s'organisent pas.
- **Maintien de l'attention** — travaillé au thème *concentration* (séries de 3 à 7 opérations, aide de méthode, contrôle du total au dépôt) : ce qui progresse est la **longueur tenue**, jamais la vitesse.
- **Lacunes ciblées** — le palier 10 isole les faits qui résistent (7 × 8, 8 × 9, 9 × 9…) et les travaille par stratégie ; la répétition espacée resservira d'abord ceux qui sont manqués.

## Pistes

- **Abaque mental (soroban)** — mentionné dans `docs/10-clinique/fondements.md` comme intéressant en rééducation (représentation visuo-spatiale plutôt que rappel pur) : pourrait devenir un palier à part entière.
- **Estimation** — « 48 € + 51 €, c'est plutôt 90, 100 ou 110 ? » : une compétence distincte et utile, à introduire en items à choix.
