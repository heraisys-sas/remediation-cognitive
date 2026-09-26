# ADR-009 — Interface : ce que le navigateur exécute doit être ce qui est livré

**Statut** : accepté (2026-09-26)

## Contexte

Deux incidents d'affichage, deux fois un diagnostic cherché au mauvais endroit :

1. **Un script périmé en cache** exécuté avec le contenu courant : l'ancien formateur de phrases ne connaissait pas le nouveau format, et affichait des phrases tronquées (« … colonne du centre et . »). Le défaut a été imputé au contenu, qui était correct.
2. **Des propositions résiduelles entre rubriques** : la phase de mémorisation masquait le formulaire sans vider les zones de réponse ; les propositions du test quitté restaient affichées sous le test suivant. Le conteneur survivait d'un exercice à l'autre.

Dans les deux cas, le code source était juste : c'est **l'écart entre ce qui est écrit et ce qui s'exécute** qui produisait le bug.

## Décision

**1. Les fichiers de l'interface sont servis sans mise en cache** (`Cache-Control: no-cache, no-store, must-revalidate`) et l'URL des scripts porte une **version**, incrémentée à chaque modification de `frontend/src/`. Un navigateur ne peut donc plus exécuter un ancien script avec un nouveau contenu. En local, recharger ne coûte rien.

**2. À chaque nouvelle étape d'exercice — mémorisation comme question — toutes les zones de réponse sont vidées** par une fonction unique (choix, indices, génération, grille). Aucun conteneur partagé ne survit d'un exercice à l'autre : on ne compte pas sur « le remplissage suivant » pour effacer le précédent.

**3. Ces règles sont vérifiées automatiquement.** Le contrôle d'interface vérifie que le vidage couvre les quatre zones et qu'il est appelé dans les deux phases ; un test vérifie les en-têtes `no-store`. Un contrôle qui échoue bloque le dépôt.

**4. Le contenu affiché est contrôlé par le code réel, pas par relecture.** Un vérificateur exécute le **vrai formateur de phrases** de l'interface sur tout le contenu du thème et refuse une phrase vide, sans verbe, ou qui n'écrit pas ce que son type annonce.

## Conséquences

- (+) Un défaut d'affichage ne peut plus être confondu avec un défaut de contenu : la question « est-ce le fichier ou le navigateur ? » se règle en une commande.
- (+) Changer de rubrique ne laisse aucune trace du test précédent.
- (+) Les garde-fous sont exécutables : une régression de ce type est détectée en intégration continue locale, pas en usage réel.
- (−) Chaque modification de `frontend/src/` impose d'incrémenter la version des scripts (une ligne dans `index.html`).
- (−) Un contrôle de plus à faire tourner avant chaque dépôt (`verifier_interface.py`, `verifier_phrases.js`) : c'est le prix d'un diagnostic fiable.
