# 2026-09-24 — Méthodes : approfondissement (va plus loin)

## Suite donnée à « va plus loin »

Quatre prolongements, tous dans la ligne « remédiation, pas évaluation » :

1. **PQRST ×2** — chaque texte est testé par **deux questions de mémoire**. On ne peut plus réussir en retenant une seule information : c'est le texte entier qui doit tenir.
2. **Vérification de plan** (palier 4) — le « Vérifier » du Goal Management Training : un plan mal ordonné est affiché, il faut **repérer l'étape mal placée**. C'était la composante manquante de GMT (on entraînait le but et les étapes, pas la vérification).
3. **Repérer l'information** (palier 5) — attention sélective écologique : un courrier, une notice ou une affichette s'affiche temporisé, et l'utilisateur cherche une information précise. Stratégie enseignée : repérer d'abord **ce que la question demande**, puis chercher seulement cela.
4. **Auto-instruction transversale** — un panneau « Méthode — avant de répondre » (voir / faire / vérifier) est désormais présent dans la séance, toutes familles confondues. La méthode n'est plus un exercice isolé : c'est un fil conducteur visible au moment où l'on répond.

## Détails d'implémentation

- Nouveaux types `plan-a-verifier` et `reperer-info`, tous deux à choix ; le plan est affiché en liste ordonnée au-dessus des propositions (petite extension de `rendreOptions`).
- `reperer-info` réutilise le mode d'affichage `texte` créé pour PQRST — aucun nouveau mécanisme d'interface.
- Le thème « Méthodes » passe à **5 paliers / 44 items**.

## Contrôles

**835 items / 0 erreur** ; **134 tests** (PQRST double, plan à vérifier, repérage d'information, et les précédents) ; garde-fous cliniques sans violation.

## Reste à faire

- Passage visuel des écrans (panneau Méthode, plan proposé, repérage d'information).
- Relecture orthophoniste.
- Pistes suivantes : mémoire prospective avec choix de l'aide externe adaptée ; « scripts » de conversations téléphoniques ; exercices de vitesse de traitement non-évaluatifs.
