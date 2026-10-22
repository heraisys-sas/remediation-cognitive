# Intégration — checkpoint 22 octobre 2026

Responsable : agent integration_exercices. Avant modifications : lecture AGENTS et REPRISE réalisée ; skill ui-ux-pro-max appliquée. Propriété exclusive : catalogue, schéma, messages, dispatch/service/feedback, frontend, validateurs partagés, tests intégration, ADR/changelog. Aucun changement aux domaines/générateurs/JSON/tests isolés des autres agents, Calcul mental/Déduction ou données personnelles.

État courant : intégration implémentée, contrats raccordés. Aucun commit/push. Revue navigateur prise en charge par parent. Voir validation finale ci-dessous.

## Checkpoint implémenté
Catalogue deux cartes raccordé, schéma type logigramme, dispatch correcteurs dédiés, second essai logigramme. UI native tableau selects réversibles, indices visibles+lecture, retour inconnu, doublons signalés sans autosolution, verrou requête/feedback. Mots et définitions lexicaux exclus payload ; preuve déductive privée. Dictée manuelle lexical uniquement, auto évocation inchangée. ADR-052/changelog ajoutés. V1 ne marque pas les exclusions « impossible » : documenté ADR.

Tests ciblés : 4 passed (`PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH python3 -m pytest -q backend/tests/test_integration_lexique_logigrammes.py backend/tests/test_refactor_catalogue.py`). `python3 tools/verifier_reponses.py` : 1472 items, 0 anomalie. `python3 tools/verifier_interface.py` OK. `node --check frontend/src/exercises/logigrammes.js` OK. Validateur : heuristique lexicale segment corrigée mots entiers + mots reconstruits ; une erreur indice P3 signalée agent lexical. Suite complète en cours session exec 7377 ; sortie `/private/tmp/lexique-integration-tests.txt`. Pas encore essai navigateur.


## Validation finale de l’intégration
- Suite : `PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH python3 -m pytest -q` → 577 passed, 1 skipped, 1 failed (seule erreur indice lexical P3, agent lexical prévenu). Sortie : `/private/tmp/lexique-integration-tests-final.txt`.
- Test intégration complété ensuite : 5 passed, dont cycles séances→correction deux thèmes, second essai sans réponse, anti-fuite payload et validateur fragments (sous-chaîne tolérée, segment/mot complet interdit).
- Attendus historiques API mis à jour pour les deux cartes ; la clé `valeur` des références des contraintes logigramme est publique et ne constitue pas une solution. `associations`/`preuve_deductive` interdites dans stimulus.
- Filtres accueil raccordés : « Trouver ses mots » inclut début commun ; raisonnement inclut logigrammes. Parent prend tests Playwright `accueil.spec.cjs` et `lexique-logigrammes.spec.cjs`.
- Commande finale après correction corpus : relancer suite ci-dessus, `python3 tools/validate_items.py`, `python3 tools/verifier_reponses.py`, `python3 tools/verifier_interface.py`, `git diff --check`. Aucun blocage externe.
- Prompt de reprise : « Lire INTEGRATION.md et contrats voisins ; vérifier correction dernier indice lexical P3 auprès agent lexical, lancer validations et consulter essai navigateur parent. Ne modifier ni Calcul mental/Déduction ni données utilisateur. Ne pas commit/push sans accord parent. »

## Bilan final — code gelé
La dernière erreur était un faux positif : segment « dé » comparé sans accents à la préposition « de ». Le validateur dédié préserve maintenant les accents comme le correcteur (NFC/casefold), sans changer le corpus ni désactiver les contrôles généraux. Départ début commun fixé au palier 2 à la demande parent, assertion API ajoutée.

Validation finale après ces changements : **579 passed, 1 skipped**, 2 avertissements dépréciation FastAPI/Starlette, 35,62 s. Commande : `PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH python3 -m pytest -q` ; sortie `/private/tmp/lexique-integration-tests-final.txt`. `python3 tools/validate_items.py` : 1472 items, **0 erreur**. `python3 tools/verifier_reponses.py` : **0 anomalie**. `python3 tools/verifier_interface.py`, syntaxe JS nouveau rendu et `git diff --check` : OK. Parent assure essai navigateur et éventuelle suite Git. Aucun commit/push par agent intégration, aucun blocage code restant.
