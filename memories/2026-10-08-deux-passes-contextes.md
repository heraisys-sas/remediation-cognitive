# Deux passes pour Retrouver le contexte — 2026-10-08

Demande finale : garder une première passe photo/question pour chaque message puis une seconde passe de toutes les questions sans photo. La demande initialement interprétée comme toutes les photos avant toute question a été corrigée par l’utilisateur ; cette approche n’est pas retenue.

Implémentation frontend : phaseContextes découverte/rappel pour les séances entièrement rappel-source illustrées. Premier passage existant ; dernier bouton Passer au rappel ; remise de l’index à zéro ; montrerItem saute la mémorisation au rappel. Une erreur de rappel ajoute le WebP dans le feedback, supprimé au prochain item. Aucun contexte révélé avant réponse au rappel. Pas de reprise errorless additionnelle sur cette séance ; autres parcours inchangés. Arrêt serveur ou utilisateur conservé.

Aucune modification d’API, de contenu ou d’assets dans ce complément. Les secondes réponses utilisent le mécanisme existant des essais supplémentaires. Résumé/FSRS ne mesurent pas séparément la seconde passe (ADR-035).

Validation : tools/test_serie_contextes.cjs (5 tests), backend/tests/test_contextes.py et suites ciblées (50 tests), Chrome à 375 px avec 10 photos/questions puis 10 questions sans photo, correction erronée illustrée, aucune image persistante au prochain item, aucun débordement. Node syntaxe et verifier_interface passent. Travail local sans commit ni push ; préserver les autres modifications du dépôt.

Intégration sur main refactorisé (#21) : logique déplacée dans session.js/state.js, scènes dans exercises/presentation.js, correction dans exercises/default.js, préférence dans preferences.js. Les tests Node lisent maintenant tous les scripts versionnés via frontend_source. Contrôle Chrome des deux passes et de la case de rejeu réussi sur cette structure.
