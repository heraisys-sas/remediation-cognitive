# Rapport sous-agent API backend — Sprint 1 (module Entraînement)

Date : 2026-09-03 · Périmètre : **backend/ exclusivement** (aucune modification à engine/, content/, frontend/ ; aucun commit git).

## 1. Dépendances

`pip3 install fastapi uvicorn httpx pytest` → fastapi 0.141.1, uvicorn 0.52.4, httpx 0.28.1, pytest 9.1.1 (déjà présent : fsrs 6.x requis par engine/, Python 3.13.1). Vérifié par `python3 -c "import fastapi, httpx, uvicorn, pytest"`.

## 2. Fichiers créés / modifiés

**Créés :**
- `backend/app/domain/correction.py` — correction serveur `corriger(theme, item, reponse)` : calcul-mental → comparaison numérique (accepte `56` ou `"56"`, tolère la virgule décimale `"56,5"`, tolérance flottante 1e-9) ; anglais → texte insensible casse + trim (espaces internes réduits) ; python → **chaîne exacte trimmée** pour `production` comme `prediction-sortie` (cas sensitive ; la valeur attendue peut être str ou nombre, ex. `10`, `3.14`, `"abc"`).
- `backend/app/domain/selection.py` — `selectionner_items()` : items **dus** (`engine.srs.fsrs.est_due`) du palier courant d'abord, puis **nouveaux** (aucune carte persistée) du même palier, quota max 12 ; ordre déterministe (ordre du contenu) ; jamais d'item d'un autre palier.
- `backend/app/domain/contenu.py` — `ChargeurContenu` : mappe les thèmes API (`calcul-mental`, `anglais`, `python`) vers les fichiers de `content/entrainement/` (glob trié : 9 paliers calcul-mental, verbes-irreguliers.json, builtins.json), cache mémoire, chemins résolus depuis `__file__` (indépendants du CWD).
- `backend/app/storage/store.py` — `StockageJSON` : persistance JSON atomique (tmp + `os.replace`) sous `backend/data/entrainement/<theme>/` (gitignored via `data/`), répertoires créés à la volée, racine injectable pour les tests :
  - `cartes-fsrs.json` : état FSRS par item via `CarteFSRS.to_dict/from_dict` (engine tel quel) ;
  - `maitrise.json` : `palier_courant` + historique chronologique `(palier, taux)` ;
  - `compteur-seances.json` : `{date, nb_sessions}` avec remise à zéro au changement de date.
  - Garde anti-injection de chemin (`^[a-z0-9-]+$`) ; périmètre strictement « entraînement » (ADR-002).
- `backend/app/api/entrainement/service.py` — `GestionnaireSessions` : orchestration démarrer/répondre/terminer ; exceptions métier → codes du contrat ; application FSRS en fin de séance (réussite → note 3/Good, échec → note 1/Again) ; maîtrise via `engine.mastery.criteria.palier_maitrise_historique` (90 % × 3 consécutives → palier +1) ; séances en cours **en mémoire** (registre), persistées à la fin uniquement ; garde `terminee` pour les 409 après clôture.
- `backend/app/api/entrainement/router.py` — mapping HTTP pur du contrat (codes `erreur` machine fixés par le contrat ; prose issue de `domain.messages`).
- `backend/tests/conftest.py`, `backend/tests/test_correction.py`, `backend/tests/test_storage.py`, `backend/tests/test_entrainement_api.py` — 38 tests (voir §4).

**Modifiés :**
- `backend/app/main.py` — factory `creer_app(racine_donnees=None, dossier_frontend=None)` (injection pour tests) + `app = creer_app()` (cible uvicorn `backend.app.main:app`) ; `/health` conservé ; router entraînement branché ; montage statique `/ui` → `StaticFiles(directory=<racine>/frontend, html=True)` avec chemin résolu depuis `__file__`, **tolère l'absence du dossier** (pas de mount → 404) ; **aucun** router bilan/rééducation (aucune route n'existe pour ces préfixes).
- `backend/app/domain/messages.py` — module `entrainement` enrichi (libellés des thèmes, feedback correcte/incorrecte, messages d'erreur) — vocabulaire neutre/ludique, centralisé, aucune chaîne utilisateur ailleurs.
- `backend/app/domain/dosage.py` — constantes du contrat : `LIMITE_SESSIONS_JOUR = 3`, `MAX_ITEMS_PAR_SEANCE = 12`, `DUREE_MAX_SEANCE_S = 600`.
- `backend/app/api/entrainement/__init__.py` — export du router.

## 3. Décisions notables

1. **Adaptation engine sans le modifier** : `SessionRunner` attend des items exposant `item_id` ; le contenu utilise `id`. Adaptation locale via wrapper `ItemMoteur` côté backend.
2. **Tous les items servis au démarrage** : le contrat livre les items d'un bloc → `prochain_item()` est consommé à l'ouverture ; le moteur enregistre ensuite chaque réponse. La durée max (600 s) et le quota (12) restent des garde-fous moteur.
3. **Compteur journalier incrémenté au démarrage** (pas à la fin) : une séance entamée compte dans le dosage, qu'elle aille à son terme ou non → le 429 du contrat est exact (`sessions_restantes_aujourdhui: 0`), limite **par thème**.
4. **Séance vide non historisée** : si aucun item n'est disponible (tout vu, rien de dû), la séance démarre avec `items: []` (201) et n'ajoute pas de point `(palier, 0.0)` à l'historique de maîtrise (aucun signal) — la progression réelle passe par les items redevenus dus (répétition espacée).
5. **Palier borné au contenu** : `palier_courant = min(stocké, dernier palier du thème)` pour éviter des séances vides éternelles si le stockage dépasse le contenu (ex. anglais : 1 seul palier).
6. **Première réponse par item fait foi pour FSRS** ; les essais supplémentaires (reprises errorless) restent comptés dans le résumé moteur, conformément au contrat du `SessionRunner`.
7. **Erreur bodies** : 429 = corps exact du contrat ; 404/409/422 = `{"erreur": <code machine>, "message": <prose du vocabulaire>}` (`theme_inconnu`, `session_inconnue`, `session_terminee`, `item_hors_seance`, `reponse_invalide`).
8. **Fatigue** : uniquement `arret_propose`/`motif_arret` en fin de séance, issu de `SessionRunner.doit_proposer_arret()` — aucune route ne bloque ni n'interrompt (testé : 12 réponses fausses et lentes restent toutes acceptées).
9. **Vocabulaire** : libellés de thèmes ET messages de feedback/erreur dans `messages.py` (module `entrainement`) ; les codes `erreur` sont des identifiants machine fixés par le contrat, pas de la prose.
10. **Pas de routage par thread/lock** : usage familial mono-utilisateur ; le compteur lit-puis-incrémente sans verrou (course impossible en pratique, notée pour un futur multi-utilisateur).

## 4. Tests — `python3 -m pytest -q` (depuis remediation-cognitive/, backend/tests + engine/tests)

```
........................................................................ [ 77%]
.....................                                                    [100%]
93 passed, 2 warnings in 0.44s
```

(2 warnings = dépréciations internes starlette/httpx, hors code projet.)

Couverture backend (38 tests) :
- **test_entrainement_api.py** (18) : payload de démarrage conforme (`id/type/palier/contenu`, jamais `reponse`/`valeur` — vérification récursive sur les 3 thèmes) ; cycle complet 201 → réponses (correcte chaîne/numérique, fausse avec `attendue` révélée) → fin avec résumé cohérent (12 items, 11 correctes, taux 11/12, `arret_propose False`, restantes 2) + double fin → 409 + réponse après fin → 409 + vérification des 3 fichiers persistés ; 4ᵉ séance du jour → 429 corps exact + limite par thème ; arrêt proposé jamais forcé (12 réponses fausses/lentes toutes acceptées, fin 200, `motif_arret="fatigue"`) ; progression de palier 90 % × 3 séances parfaites → `palier_courant: 2` (avec simulation d'oubli par réécriture des échéances → round-trip FSRS vérifié + items dus servis en premier) ; 404 session inconnue, 404 item hors séance, 404 thème inconnu, 422 temps négatif ; aucun endpoint `/api/bilan` (GET/POST, 3 profondeurs → 404) ; montage `/ui` (fichier réel 200, dossier absent toléré, index.html servi).
- **test_correction.py** (11) : grader numérique ("56"/56/" 56 "/"56,5"/rejets), anglais (casse/trim/rejet), python exact (production + prediction-sortie, cas "10.0" ≠ 10, cas `0`), sélection (nouveaux + quota + filtrage palier, non-dus écartés, dus en premier, séance vide).
- **test_storage.py** (6) : cartes FSRS round-trip, répertoires créés à la volée, maîtrise défauts + round-trip, compteur du jour + rollover date, thème invalide refusé.
- **test_health + test_themes** : `{"status":"ok"}`, thèmes avec `id/nom/description`.

Smoke test manuel (uvicorn réel, port 8765) : `/health` → 200 `{"status":"ok"}` ; `/api/entrainement/themes` → 3 thèmes ; `/ui/tests/README.md` → 200 ; `/api/bilan` → 404. Aucun `backend/data/` créé hors séance réelle.

## 5. Contraintes respectées

- Uniquement `backend/` modifié (+ ce rapport dans `.cluster/sprint1/`) ; les `M` git sur `engine/` et les fichiers `frontend/`/`content/` non suivis proviennent des agents parallèles, pas de cette mission.
- Aucun commit git.
- Docstrings/commentaires en français, identifiants anglais, engine/ réutilisé tel quel (aucune signature manquante à contourner).
- Garde-fous : 3 séances/jour/thème (429), arret_propose jamais forcé, correction 100 % serveur, réponse attendue jamais dans le payload de démarrage, aucune donnée de bilan, aucun endpoint `/api/bilan`, stockage JSON hors dépôt.
