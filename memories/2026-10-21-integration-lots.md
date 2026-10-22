# Intégration des lots cognitifs

Branche feat/lots-cognitifs-complets depuis la tête PR #27 (14c746b), travail
isolé dans /Users/olivierhz/orthogone/lots-cognitifs. Modifications existantes de
deduction-corrections conservées intégralement à leur emplacement ; aucune
modification de remediation-dev ni de son serveur.

Patch à trois voies et nouveaux fichiers repris : paliers mémoires, stratégies
V3, n-back V2, 126 ajouts de contenu, images contextuelles, sources/générateurs,
ADR-046 à 049. Conflits de changelog, scripts HTML et CSS résolus en conservant
les tests Playwright et tous les modules. Le retrait du graphe de PR #26 fait
également partie de ce patch et est désormais intégré dans dev.

518 pytest réussis, 1 ignoré ; 99 Node réussis. Les faux éléments DOM des tests
n-back/stratégies exposent dataset comme le navigateur. Les attentes Playwright
incluent désormais les deux cartes supplémentaires : 24 réussis (20,1 s).
Ruff 0.16.10 et validateurs contenu/réponses/interface conformes : 98 JSON,
1 424 items, 12 manifests, zéro erreur. Pas de test sur téléphone physique.

Séparer intégration dev de livraison main ; pas de fusion automatique PR #27.
Relecture professionnelle/essai de confort restent ouverts. Aucun nouveau
candidat sélectionné, aucune extension silencieuse du calendrier, aucun service
de transfert ni gestion d’utilisateurs ajouté.
