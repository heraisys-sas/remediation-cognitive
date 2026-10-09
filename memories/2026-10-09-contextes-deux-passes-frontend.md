# Contextes — deux passes, observations frontend

9 octobre 2026. Lot EX-REV-003, après GO utilisateur.

- Première réponse validée conservée indépendamment pour découverte après photo et rappel sans photo. Les futures questions ne deviennent pas des erreurs lors d’une sortie partielle.
- Résumé Contextes séparé par passe, sans total ni taux global. Parcours actuel en QCM : résultat décrit comme reconnaissance de source.
- Exposition première passe enregistrée après décodage effectif ; erreur de chargement tracée. Photo après erreur au rappel tracée après événement load, avec garde contre un écran déjà quitté. Bouton Afficher, scènes et rythme préexistants conservés.
- Extension frontend additive : observation_contextes sur POST réponses ; observations_contextes sur POST fin transmet seulement les faits de présentation/révélation/incident. La justesse cliente ne part pas dans le corps de clôture. Le parent réalise le contrat et la persistance serveur ; ne pas déduire une persistance autonome des seuls changements frontend.
- Aucune reprise notée après photo introduite : correction et photo permettent de comprendre l’erreur ; première réponse inchangée.
- Vérifications : 7 tests comportementaux Contextes, vérificateur session et vérificateur interface passent. Node du runtime Codex utilisé (node absent du PATH système).

## Intégration de persistance réalisée ensuite

- ADR-044 et contrat API ajoutés : journal atomique séparé `observations/<session_uuid>.json`, écrit dès chaque réponse Contextes documentée/checkpoint PQRST.
- API réponses et fin acceptent les observations optionnelles ; clôture retourne les observations Contextes. La première réponse et sa justesse viennent du serveur. La fusion des faits de fin est atomique et ne transmet aucune modification à FSRS ou aux historiques de maîtrise.
- Checkpoint PQRST : POST observations valide le protocole partiel sans noter ni appeler le runner. L’observation complète corrigée est conservée face aux checkpoints et reprises ultérieurs.
- Lecture après redémarrage assurée par le stockage ; aucune consultation historique utilisateur ni reprise de séance active ajoutée.
- 16 tests dédiés persistance/API passent. Suite complète initiale après intégration : 392 passed, 1 skipped (avant ajout des derniers cas atomiques et changement de métadonnées PQRST).
- Autorisation complémentaire parent : nouveaux protocoles `_pqrst` exclus de baseline RT et du résumé `sans_aide`, sans modifier FSRS ni anciens payloads/historiques. Test ciblé ajouté.
- Snapshot PQRST capturé avant nettoyage, sauvegarde checkpoint lancée ; fin attend la sauvegarde. Échec réseau conserve le snapshot dans une file locale indépendante de la réinitialisation de séance, avec réessai lors de clôture. Deux tests JS : conservation après erreur et attente du checkpoint en cours.
- Validation finale après intégration/checkpoint et exclusion mesures PQRST : 417 passed, 1 skipped ; 9 tests JS Contextes/checkpoint passent. Aucun calcul de délai de rappel affiché : seuls les horodatages effectivement observés sont enregistrés, sans durée supposée.

## Validation finale par le parent

Intégration et recette terminées : [journal de validation](2026-10-09-validation-finale-lot-1.md). Suite complète 417 réussis, 1 ignoré ; 9 tests Node, Ruff et contrôles locaux réussis. PQRST et série Contextes complète vérifiés sur serveur actualisé, journal durable conforme au résumé.
