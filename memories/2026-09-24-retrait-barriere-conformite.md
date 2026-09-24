# 2026-09-24 — Retrait de la barrière de conformité (contexte POC/labo)

## La demande

« Il s'agit d'un POC, pas de garde-fou ni de barrière "matériel protégé" dans ce labo. »

## Ce qui a été retiré

- **Le contrôle de conformité** : `tools/verifier_clinique.py` n'est plus exécuté ni référencé ; son test est supprimé. Le script (vocabulaire clinique, photophobie, scan « matériel protégé », statut de relecture) reste sur disque, inerte et marqué comme tel — **la suppression de fichier a été refusée par le garde-fou de sécurité** (approbation expirée), donc elle attend une demande explicite.
- **La barrière « matériel protégé »** : les énoncés « aucun matériel protégé reproduit », « droits ECPA/Pearson », « strictement exclu » sont retirés du contenu, des outils, de la bibliographie, du cadre réglementaire et du README. Les **citations d'auteurs** restent : ce sont des sources, pas une copie de matériel.

## Ce que j'ai gardé, et pourquoi

Le mot « garde-fou » recouvrait deux choses très différentes. J'ai retiré la **barrière de conformité**, j'ai gardé les **mécanismes produit** :

- dosage (600 s, 3 séances/jour, 1/jour pour l'évaluation), plafonds de difficulté, saisie bornée ;
- thème sombre sans animation.

Ce sont des **choix d'usage** (photophobie, sur-sollicitation post-commotionnelle), pas des barrières de conformité — et ils ne bloquent personne. Si le laboratoire veut aussi les retirer, il suffit de le dire.

## Contrôles restants

`validate_items.py`, `verifier_reponses.py`, `verifier_interface.py` — cohérence technique (schéma, réponses, interface). **811 items / 0 erreur**, **132 tests**.

## Reste à faire

- Supprimer `tools/verifier_clinique.py` (à approuver) — il est inerte d'ici là.
- Le contexte POC/labo est noté en tête d'AGENTS.md pour que les prochaines sessions ne réintroduisent pas de barrière.
