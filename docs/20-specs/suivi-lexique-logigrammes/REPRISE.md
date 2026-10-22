# Deux exercices — checkpoint de reprise, 22 octobre 2026

Branche : feat/lexique-logigrammes ; checkout : /Users/olivierhz/orthogone/lexique-logigrammes ; base origin/dev 0ed9207. Ne pas modifier le checkout serveur ni Calcul mental/Déduction. Aucun historique personnel à migrer.

## Autorisation
Olivier demande l’implémentation avec sous-agents et traces persistantes permettant une reprise après épuisement du quota. Branche temporaire puis PR vers dev ; pas de livraison main implicite.

## Avis expert GPT-6 Astra
Adapter les deux tâches, priorité au logigramme comme support de stratégies. Pas de validation clinique propre de ces exercices ni de diagnostic à partir des scores. Début commun = recherche lexicale orthographique avec génération et double vérification ; pas nécessairement syllabe/préfixe. Logigramme = intégration relationnelle, déduction, organisation ; grille externe = compensation assumée, pas preuve d’entraînement de mémoire de travail. Niveau adulte sans pression temporelle. La progression ne se résume pas à des mots rares ou des indices longs. Enseigner préciser objectif, relever contraintes, traiter une étape, vérifier. Aucun transfert général promis.

Sources à vérifier/documenter : INCOG exécutif doi:10.1097/HTR.0000000000000834 ; Bertens 2015 PMID26346836 ; Vas 2015 PMID26018041. Lexique pour normes lexicales ; PCA aphasie distinct du jeu proposé.

## Répartition sans écritures concurrentes
- Agent lexical : générateur, nouveaux JSON lexicaux, tests et checkpoint LEXICAL.md uniquement ; proposition d’intégration dans son checkpoint.
- Agent logigramme : domaine/correcteur et générateur propres, JSON nouveaux, tests et checkpoint LOGIGRAMME.md uniquement.
- Agent intégration (ensuite) : catalogue, schéma, messages, UI, dispatch/service, validateurs, docs communes. Attend contrats des deux agents.

## Critères
Lexical : vrais mots, segment écrit commun, solutions alternatives explicites, aides graduées, corpus original progressif adulte, pas de correction sémantique d’un segment strict.
Logigramme : données originales, solution unique ET résolution déductive documentée sans deviner ; indices accessibles, aucune règle collective cachée ; tableau réversible et non rempli automatiquement ; aides de méthode.
Réutiliser infrastructure séances/feedback/aides/progression. Pas d’IA ni modèle nouveau nécessaires.

## À faire / ordre de reprise
1. Agents écrivent contrats et checkpoints AVANT travaux substantiels ; mettre à jour après chaque étape.
2. Intégration cohérente des nouveaux parcours avec isolation des historiques et identifiants inédits.
3. Tests ciblés puis suite/validateurs/JS, essai interface ; noter commandes, résultats, blocages exacts.
4. Revue, commit contenu explicitement annoncé, push et PR dev si réseau accessible. Ne pas annoncer livraison avant vérification.

État initial : worktree créé propre ; fetch GitHub réussi via accès réseau élevé. Dernière inspection : dev local ancien, travail donc basé sur origin/dev actualisé. Pas de code encore modifié au présent checkpoint.

## Contrôle parent en cours
- Plan initial commité : f075ebd.
- Trois sous-agents actifs : implementation_lexical, implementation_logigramme, integration_exercices ; écritures réparties comme ci-dessus.
- Node absent du PATH standard ; utiliser `PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH` pour pytest/Node. Aucun paquet installé.
- Premier pytest avec ce PATH : 530 réussis, 1 ignoré, échec unique validateur portant sur nouveaux indices lexicaux en cours (heuristique sous-chaîne). Rapport /private/tmp/lexique-baseline-tests.txt. Ce n’est pas une suite finale.
- Revue parent : corriger radio/râteau (accent incompatible) ; garder définitions comme indices et non dans énoncé initial ; pas aide première lettre si réponse monolettre. Éviter des logigrammes tous isomorphes (chaîne totale puis même élimination), demandé diversité réelle des graphes d’indices et test associé.
- Skill UI appliquée par intégrateur : /Users/olivierhz/orthogone/.agents/skills/ui-ux-pro-max/SKILL.md.

## Livraison locale vérifiée — 22 octobre 2026
- Implémentation terminée : Débuts de mots communs (36 paires, 3 paliers, Auto P2) ; Croiser les indices (12 logigrammes, 3 paliers, Auto P1).
- Les trois agents ont terminé ; aucun agent n’écrit encore. Correctifs de revue appliqués. Corps de solution privés ; correction stricte sans moteur sémantique pour ces deux types.
- `PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH python3 -m pytest -q` : **579 passed, 1 skipped** ; rapport /private/tmp/lexique-integration-tests-final.txt. Avertissements FastAPI/httpx préexistants.
- Validateurs : 1472 items, 0 erreur ; réponses 0 anomalie ; interface OK ; Ruff OK (binaire temporaire /private/tmp/orthogone-lint-20261022/bin/ruff).
- Playwright : **32 tests passent**, Chromium bureau/mobile et WebKit mobile/320px ; rapport /private/tmp/lexique-ui-complet.txt. Deux tests nouveaux couvrent saisie/correction/suivant et doublons/réversibilité/correction/absence de débordement. Serveur test éphémère, données utilisateur intactes. La dérogation de test explicite évite le quota du serveur partagé entre projets.
- Filtres accueil adaptés, versions des ressources modifiées incrémentées. SDK Apple, micro réel et voix non modifiés ni réévalués sur matériel.
- Limites : corpus pilote, relecture professionnelle à faire ; tableau v1 permet associations/inconnues, pas annotation d’exclusions. Aucune efficacité clinique propre ni transfert démontrés revendiqués.
- Prochaine action de reprise : vérifier Git/PR et CI sur cette branche ; consulter AVIS-CLINIQUE.md et checkpoints agents. Essayer manuellement les parcours puis intégrer vers dev après revue. Ne pas fusionner main automatiquement.
