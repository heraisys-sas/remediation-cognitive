# Sprint 4 — Empan de mots, rappel de séries, correctifs d'usage

## Demandes reçues

1. Le champ de réponse doit être vidé quand la question suivante s'affiche (bug).
2. Rythme d'affichage de l'empan de chiffres (« il me semble qu'il y a une pause de 2 secondes — corrige cela »).
3. Vérifier la complexification progressive et l'absence d'empan de mots.
4. Rappel libre (« quelle était la première série ? », « toutes les séries dont on se souvient ») et tentatives plus tard — avis demandé.
5. Regrouper Python et Anglais dans une section « Extra » en bas de l'accueil.

## Constats

- Champ de saisie : régression introduite au sprint 3 (bloc de remise à zéro supprimé en réécrivant l'affichage de la question) — corrigée, puis VÉRIFIÉE dans un navigateur réel, et couverte par un contrôle automatisé.
- « Pause de 2 s » : inexacte — 800 ms d'affichage + 250 ms de blanc. La formulation « environ 2 s » de l'interface prêtait à confusion : rythme désormais explicite, blanc réduit à 120 ms, borne 400–2000 ms validée sur le contenu.
- Progression : vérifiée sur les données (chiffres endroit 3→6, envers 3→6, paires 2→4, n-back 2→4).
- Empan de mots : absent — ajouté.

## Décisions

- ADR-005 : type `empan-mots` ; type `rappel-libre` avec `affichage.mode = "series"`, `delai_s`, `portee`, `reponse.seuil` ; correction au seuil ; invariantes de contenu (rythme, unicité des mots, cibles = séries affichées).
- Les seuils de rappel restent des repères de séance, jamais des scores.
- Section « Extra » : regroupement purement présentationnel (Python, Anglais), aucun changement d'API.

## Contrôles

- `tools/validate_items.py` — 691 items, 0 erreur. Deux défauts réels attrapés : indice phonologique révélant « clé » (sprint 3) et mot « panier » dupliqué dans le pool (sprint 4).
- `tools/verifier_reponses.py` — 691 items recalculés, 0 anomalie.
- `tools/verifier_interface.py` — identifiants + remise à zéro du champ de saisie.
- `python3 -m pytest -q` — 110 passed.
- Navigateur : champ vidé après « Suivant » ; accueil avec section « Extra » (Anglais, Python en bas).

## Délégation (cluster_bypass_reason)

La délégation à des sous-agents reste indisponible (échecs à l'exécution du fournisseur, HTTP 403, constatés aux sprints 2 et 3 : trois envois acceptés puis échoués, aucun livrable produit). Aucun envoi n'a été tenté sur ce sprint : le travail est itératif, principalement une correction d'interface et deux familles de contenu, et la vérification est assurée par des contrôles versionnés dans le dépôt.

## Statut

Livré : correctifs, contenu (104 nouveaux items), interface (Extra, séries, compte à rebours), contrôles, docs (ADR-005, contrat, specs, taxonomie, CHANGELOG, READMEs), rapport de sprint.
