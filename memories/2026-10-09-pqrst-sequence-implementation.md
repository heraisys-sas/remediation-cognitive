# 2026-10-09 — PQRST séquencé

Lot autorisé après spécifications v1.1. Implémentation dans `frontend/src/exercises/sequence.js`, correcteur/normaliseur dans `backend/app/domain/correction/sequence.py`, textes centralisés `messages.PQRST_INTERFACE`, contrat [ADR-043](../docs/30-technique/adr/ADR-043-pqrst-sequence-et-observations.md). Aucun corpus, ID, historique ou fichier moteur modifié.

Départ volontaire puis P/Q/R/S/T successifs ; retrait DOM du texte/des notes et arrêt voix ; résumé après S conservé et retiré avant T ; deux questions T successives sans correction intermédiaire ; retour final neutre par étape. Question personnelle non notée. Modèle S local = comparaison, jamais note de seuil avant serveur ; accompagnement ADR-027 reste après correction finale.

Premières réponses et essais aidés séparés, absence explicite, maximum une relecture par rappel ; une relecture T1 s’applique aussi à la condition de T2. Pause/onglet masquent les supports ; reprise interrompue tracée. Les brouillons non validés restent en mémoire pendant pause mais ne sont pas inclus dans le checkpoint.

Normaliseur `normaliser_observation_pqrst` borné, sans notation pour checkpoint ; payload historique sans `_pqrst` inchangé. Champ `reprise_apres_correction` distingue les reprises d’un texte déjà corrigé dans la séance. Le gestionnaire/service, l’endpoint d’observation et la persistance sont intégrés par le lot résultats ; les hooks de sortie/nettoyage sont coordonnés avec le parent/lot Contexte. Échec réseau ou fermeture brutale ne doivent pas être présentés comme une sauvegarde réussie.

Validation ciblée : 38 tests passent (nouveaux cas PQRST et régressions méthodes, accompagnement, handlers). Les vérifications d’intégration/service et la recette visuelle sont réalisées avec le parent. Limites conservées : correcteur de reformulation borné, aucune mesure de capacité, aucune dictée automatique nouvelle dans ces champs, aucun résultat ancien requalifié en rappel masqué.

## Validation finale par le parent

Intégration et recette terminées : [journal de validation](2026-10-09-validation-finale-lot-1.md). Suite complète 417 réussis, 1 ignoré ; 9 tests Node, Ruff et contrôles locaux réussis. PQRST et série Contextes complète vérifiés sur serveur actualisé, journal durable conforme au résumé.
