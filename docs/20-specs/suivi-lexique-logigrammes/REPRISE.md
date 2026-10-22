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
