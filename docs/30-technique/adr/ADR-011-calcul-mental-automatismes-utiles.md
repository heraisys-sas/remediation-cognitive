# ADR-011 — Calcul mental : des automatismes utiles, pas des tables à réciter

**Statut** : accepté (2026-09-26)

## Contexte

Le thème « calcul-mental » suivait neuf paliers, un par table (×2, ×5, ×10, ×3, ×4, ×6, ×7, ×8, ×9), chaque palier posant toute la table dans les deux sens (« 2 × 1 », « 1 × 2 ») sous forme de produit brut.

Trois problèmes, signalés en usage : « inutile de faire la table des 10 et des 1 ».

1. **× 1 et × 10 ne sont pas des faits à automatiser** mais des **règles** ; les driller ne construit rien.
2. **Les deux sens** (« 1 × 2 » puis « 2 × 1 ») font des doublons commutatifs : 19 items par palier pour 10 faits réels.
3. **La forme scolaire** (« 2 × 1 ») ne dit rien de l'usage : un adulte n'a pas besoin de réciter une table, il a besoin de calculer juste ce qu'il rencontre — une addition de prix, un rendu de monnaie, une quantité doublée — et de retrouver vite les faits de base pour ne pas saturer sa mémoire de travail.

## Décision

**1. La progression suit l'usage, pas l'ordre scolaire.** Neuf paliers :

| Palier | Contenu |
|---|---|
| 1 | Compléments et retraits dans 10 (faits de base) |
| 2 | Doubles et presque-doubles (stratégie) |
| 3 | Additions dans 20 |
| 4 | Soustractions dans 20 |
| 5 | Compléments à 100 (repères d'argent) |
| 6 | Multiplications utiles (× 2 à × 5) |
| 7 | Deux opérations enchaînées (mémoire de travail) |
| 8 | Au quotidien : l'argent (totaux, rendu de monnaie) |
| 9 | Au quotidien : quantités et durées (proportions, totaux) |

**2. Ni × 1, ni × 10 comme tables.** Les multiplications se limitent aux faits utiles (× 2 à × 5), sans doublon commutatif. « × 10 » n'apparaît qu'à l'usage, dans un calcul réel.

**3. Les énoncés s'adressent à un adulte** : questions courtes et naturelles (« Combien manque-t-il à 7 pour faire 10 ? », « Un article à 7 €, payé avec 10 €… »), jamais un produit nu.

**4. Les stratégies sont enseignées, pas supposées.** Les paliers concernés portent une **aide** repliée (le moyen, jamais le résultat) — « un presque-double, c'est le double plus un » — et le palier 7 une consigne de méthode affichée une fois par séance.

**5. Le dépôt recalcule la réponse à partir de l'énoncé.** Le contrôle de contenu ne fait plus confiance au générateur : il relit la question et refait le calcul (familles calculables), et refuse une discordance.

**6. Nouveaux identifiants (`cm2-`)** : le contenu étant entièrement revu, il ne doit pas hériter des états de révision de l'ancien (règle de versionnage du contenu).

## Conséquences

- (+) Le temps d'entraînement va à ce qui se transfère : faits de base, stratégies, mémoire de travail, numératie du quotidien.
- (+) Plus de doublons commutatifs ni de règles déguisées en faits ; le volume d'items sert à la **variété des faits**, pas à la répétition d'un même produit.
- (+) Le contrôle par recalcul rend impossible de livrer durablement une question associée au mauvais résultat — il a immédiatement attrapé une erreur de génération réelle.
- (+) Les identifiants neufs évitent qu'un état de révision hérité fausse la progression d'un item changé.
- (−) Les six derniers paliers dépendent du **contexte** des énoncés : ils ne sont pas recalculables automatiquement, ils restent donc contrôlés en forme (réponse entière positive, pas de doublon).
- (−) L'estimation (« c'est plutôt 90 ou 100 ? ») n'est pas encore couverte : elle demandera des items à choix.
- (−) Le soroban/abaque mental, mentionné comme intéressant en rééducation, reste une piste non implémentée.
