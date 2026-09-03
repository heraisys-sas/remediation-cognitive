# Revue exécution — Sprint 1 (tests, serveur, cycle réel, risques code)

**Date** : 2026-09-03 ~21:30–21:50 (Europe/Paris) · **Revue** : agent de revue (aucun fichier du dépôt modifié)
**Périmètre vérifié** : moteur `engine/`, contenu `content/`, backend FastAPI `backend/`, interface `frontend/`, contrat `docs/30-technique/api-contract.md`.

---

## 1. Pytest — résultat exact

Commande : `python3 -m pytest -q` (depuis `remediation-cognitive/`)

```
........................................................................ [ 77%]
.....................                                                    [100%]
93 passed, 2 warnings in 0.47s
```

- Répartition collectée : **engine/tests = 55**, **backend/tests = 38** → 93 au total ✓ (conforme à l'annonce du sprint).
- 2 warnings uniquement (dépréciations starlette/httpx via TestClient, externes au dépôt — aucune action requise sprint 1).
- Vérifié en prime : la suite n'écrit pas dans le dépôt (`backend/tests/conftest.py` isole les données dans `tmp_path`) ; `backend/data/` reste absent après pytest ✓.

---

## 2. Serveur réel

- `python3 -m uvicorn backend.app.main:app --port 8765` lancé en arrière-plan depuis `remediation-cognitive/` → démarrage OK (log : `Application startup complete. Uvicorn running on http://127.0.0.1:8765`), écoute sur `127.0.0.1:8765`.
- Remarque : le port **8766 est occupé par AutoClaw lui-même** sur cette machine — si un futur lancement automatique choisit 8766, il échouera. 8765 est le bon choix par défaut.
- Second serveur de contrôle lancé depuis **CWD=`/`** (hors dépôt, `--app-dir`) : `/health` et `/ui` répondent identiquement → le montage statique et les chemins de contenu sont bien **indépendants du CWD** (`RACINE_PROJET` résolu depuis `__file__` dans `backend/app/domain/contenu.py`, réimporté par `main.py`). Les deux serveurs ont été tués en fin de revue (PID 60455 et 60666 vérifiés morts).

---

## 3. Cycle E2E complet (script python3 + urllib, sans dépendance)

Script : `.openclaw/tmp/e2e_revue.py` (hors dépôt). **25 vérifications, 24 passées, 1 échec** (détail §3.3).

### 3.1 Cycle nominal — ce qui a été observé

| Étape | Résultat observé |
|---|---|
| `GET /health` | `200 {"status": "ok"}` ✓ |
| `GET /api/entrainement/themes` | `200`, ids = `['calcul-mental', 'anglais', 'python']` ✓ |
| `POST /api/entrainement/calcul-mental/sessions` | `201`, `session_id` + **12 items** (tous palier 1, thème vierge) + `regles={'max_items': 12, 'duree_max_s': 600}` ✓ |
| Fuite de réponses au démarrage | Scan récursif complet du payload : **aucune clé `reponse` ni `attendue`** ✓ |
| Items vs contenu | Les 12 ids existent dans `content/entrainement/calcul-mental/paliers/palier-01.json`, réponses attendues lues dans ce fichier ✓ |
| Réponse 1 : `cm-2-2x1` = `2`, 950 ms | `200 {'correcte': True, 'attendue': 2, 'feedback': 'Bien joué, réponse correcte !'}` ✓ |
| Réponse 2 : `cm-2-1x2` = `2`, 1100 ms | `200 {'correcte': True, 'attendue': 2, ...}` ✓ |
| Réponse 3 (fausse) : `cm-2-2x2` = `1004`, 800 ms | `200 {'correcte': False, 'attendue': 4, 'feedback': 'Pas tout à fait — la réponse attendue s'affiche, on y reviendra.'}` ✓ |
| Item hors séance (`cm-9-9x9`) | `404 {'erreur': 'item_hors_seance', ...}` ✓ |
| `POST .../fin` | `200` — `correctes=2`, `taux_reussite=0.6667`, `arret_propose=False`, `motif_arret=null`, `sessions_restantes_aujourdhui=2` — **mais `items=12`** (voir §3.3) |
| Réponse après fin | `409 {'erreur': 'session_terminee'}` ✓ |
| Double `fin` | `409` ✓ |
| Session inconnue | `404 {'erreur': 'session_inconnue'}` ✓ |

Le garde-fou fatigue a aussi été observé en situation réelle : deux séances avec 3 réponses bidon (60 ms, tout faux) se terminent avec `arret_propose=True` (taux d'erreur 1.0 ≥ 0.40) — détection conforme au contrat, **proposition seulement** (la séance se termine normalement, rien n'est interrompu).

### 3.2 Garde-fous — ce qui a été observé

- **3 séances/jour** : séances 2 et 3 démarrées/répondues/terminées OK ; la **4ᵉ `POST sessions` renvoie bien `429 {'erreur': 'limite_sessions_atteinte', 'sessions_restantes_aujourdhui': 0}`** — corps exact du contrat ✓.
- **`GET /ui`** : `307` (redirection standard StaticFiles `/ui` → `/ui/`) puis `200 text/html; charset=utf-8`, contenu = le `<!doctype html>` de `frontend/index.html` (5 403 octets) ✓. Service statique conforme.
- **Périmètre bilan** : `GET /api/bilan` → `404`, `POST /api/bilan/sessions` → `404` ✓. Aucune route bilan enregistrée (`backend/app/api/bilan/__init__.py` est vide et aucun router n'est inclus) ; `StockageJSON` est strictement limité à `entrainement` ; aucune chaîne clinique dans les payloads observés (vocabulaire centralisé `messages.py`).

### 3.3 Échec constaté — incohérence du résumé de fin (séance partiellement répondue)

**Observé** : après avoir répondu à 3 items sur 12 servis, `POST .../fin` renvoie :

```json
{"resume": {"items": 12, "correctes": 2, "duree_s": 0, "taux_reussite": 0.667},
 "arret_propose": false, "motif_arret": null, "sessions_restantes_aujourdhui": 2}
```

**Problème** : `items=12` compte les items *servis*, `correctes=2` compte les réponses *envoyées*, `taux_reussite=0.67` est calculé sur les réponses *envoyées* (2/3). Le résumé est donc **mutuellement incohérent** (0.67 ≠ 2/12) et trompeur à l'affichage (« 12 items, 2 correctes » suggère 10 échecs au lieu d'1). Le critère de revue « items=3 » échoue.

**Cause racine (localisée, lecture de `backend/app/api/entrainement/service.py`)** : dans `demarrer()`, la boucle `while runner.prochain_item() is not None: pass` marque les 12 items comme servis d'un bloc (le contrat livre tous les items au démarrage), puis `SessionRunner.terminer()` retourne `items = self._index` (= servis) tandis que `correctes`/`taux_reussite` sont calculés sur `self._reponses` (= réponses effectives). Le cas « fin de séance avant d'avoir répondu à tout » n'est couvert par aucun test : `test_cycle_complet_avec_resume_coherent` répond aux 12 items, donc `items == nb_réponses` y est cohérent par construction.

**Effets en cascade** : l'historique de maîtrise persisté utilise `taux_reussite` (calculé sur réponses) → critère de maîtrise non faussé ✓ ; mais l'affichage utilisateur du résumé et le champ interne `erreurs` (12−2=10 au lieu de 1) sont faux. Les deux séances « bidon » de la §3.1 montrent le même motif (`items=12, correctes=0` après 3 réponses).

---

## 4. Risques code (lecture `backend/` + `engine/`) — classés par sévérité

### GRAVE

Aucun blocage fonctionnel, fuite de données ou violation de garde-fou détectée. (Le point 3.3 est le candidat le plus sérieux ; classé moyen car aucune donnée n'est corrompue et le critère de maîtrise n'est pas faussé — mais à traiter avant tout usage réel du résumé.)

### MOYEN

1. **Résumé de fin incohérent sur séance partielle** (détail §3.3) — `resume.items` ≠ dénominateur de `taux_reussite` ; champ `erreurs` interne faux. À corriger (ex. : `items` = nombre d'items répondus, ou distinguer `servis`/`repondus`) + test du cas partiel.
2. **Course (race condition) sur le compteur de séances/jour** : les endpoints FastAPI sont `def` synchrones → exécutés dans le threadpool ; `demarrer()` fait lire-puis-écrire le compteur (`lire_compteur` → … → `ecrire_compteur`) sans verrou. Deux POST simultanés peuvent passer sous la limite et dépasser 3 séances. Contexte familial mono-utilisateur → impact faible, mais le contrat présente ce garde-fou comme « non contournable ».
3. **Réponses dupliquées acceptées sur un item déjà répondu** : `repondre()` ne vérifie pas si l'item a déjà été répondu (choix assumé « reprises errorless » côté moteur), et chaque essai compte dans `correctes` du résumé. Un client (ou un utilisateur injoignable par l'UI) peut artificiellement gonfler `correctes` au-delà de `items` (ex. 3 items × 2 essais corrects → `correctes=6, items=12, taux=1.0`). Seule la **première** réponse alimente FSRS (`setdefault`) → SRS non faussé. Cohérence d'affichage et audit à clarifier.
4. **Baseline RT figée à 1000 ms** : `SessionRunner` est construit sans `baseline_rt_ms` → défaut 1000. Un utilisateur naturellement lent (RT moyen > 1250 ms, même 100 % de réussite) déclenchera `arret_propose=True` systématiquement (faux positif). La baseline réelle par utilisateur est prévue par le moteur mais pas encore branchée côté backend.

### MINEUR

5. **Séances en mémoire uniquement** : `_sessions` n'est jamais persisté ni purgé — redémarrage du serveur = séances en cours perdues (`404 session_inconnue`, message clair prévu) ; croissance mémoire non bornée sur process longuement vivant. Acceptable sprint 1, à noter pour la Phase 2.
6. **Montage statique évalué une seule fois** : `if frontend.is_dir()` au démarrage seulement — si `frontend/` est créé après le lancement, `/ui` reste 404 jusqu'au redémarrage (comportement documenté dans la docstring de `main.py`). Résolution du chemin elle-même : fiable, indépendante du CWD (vérifié en §2).
7. **Corruption de fichier JSON runtime non gérée** : `StockageJSON._lire_json` n'attrape que `FileNotFoundError` ; un `compteur-seances.json` corrompu lèverait `JSONDecodeError` → 500 sur tout démarrage de séance. Écriture atomique (temp + `os.replace`) déjà en place, risque faible.
8. **Séance vide possible** : si tous les items du palier courant sont déjà vus et non dus (FSRS), `selectionner_items` peut retourner 0 item → séance 0 item qui consomme quand même 1 des 3 sessions du jour (compteur incrémenté au démarrage). La maîtrise n'est pas historisée dans ce cas (`items <= 0` → return) ✓, mais l'utilisateur perd un quota sans exercice.
9. **Codes d'erreur couplés à `messages.texte`** : une clé manquante lèverait `KeyError` → 500. Registre actuellement complet (toutes les clés `erreur_*` du contrat existent) ; robustesse interne à surveiller lors d'ajouts.
10. **Contenu chargé en cache au premier accès** : modifier `content/` pendant l'exécution n'est pas pris en compte (choix documenté « figé pendant l'exécution ») ; redémarrage requis.
11. **Sans authentification** (contrat : usage familial mono-utilisateur, Phase 1) — uvicorn écoute par défaut sur 127.0.0.1 ; ne pas lancer avec `--host 0.0.0.0` sans ajout d'auth. Info, conforme au contrat actuel.

### Points vérifiés sains (aucun risque trouvé)

- **Correction serveur** : la réponse attendue ne quitte jamais le serveur avant soumission (scan E2E du payload de démarrage négatif ; `attendue` n'apparaît qu'après POST réponse) ✓.
- **Isolation des périmètres** : aucun endpoint ni stockage bilan ; `StockageJSON` valide le thème par regex `^[a-z0-9-]+$` (anti path-traversal) ; thème/séance croisés (`_session` exige `session.theme == theme`) → une séance d'un thème n'est pas joignable via un autre ✓.
- **Validation des entrées** : `temps_ms` négatif/non numérique → 422 ; bool rejeté par pydantic et par `corriger` ; réponses texte numériques acceptées (`"56"`), virgule française tolérée ✓.
- **Moteur engine/ réutilisé tel quel** (adaptation `ItemMoteur` côté backend uniquement) ; FSRS déterministe (fuzzing off), `planifier` immuable ; critère de maîtrise par palier avec réinitialisation au changement de palier ✓.

---

## 5. Effets de bord de la revue (transparence)

- **Aucun fichier suivi du dépôt modifié** (`git status` inchangé par la revue ; les `M`/`??` observés pré-existaient — sprint 1 non encore commité).
- L'E2E a fait écrire au serveur ses données runtime **gitignorées** (`data/` au `.gitignore`) : `backend/data/entrainement/calcul-mental/{cartes-fsrs.json, maitrise.json, compteur-seances.json}`. Conséquence : **le quota du jour 2026-09-03 pour calcul-mental est consommé (3/3)** — un utilisateur réel serait en 429 jusqu'à demain. Réinitialisation éventuelle (décision Owner) : supprimer `backend/data/entrainement/calcul-mental/`.
- Scripts de test stockés hors dépôt (`.openclaw/tmp/`) ; serveurs tués (ports 8765/8767 libérés, vérifié) ; le port 8766 est occupé par AutoClaw (ne pas l'utiliser).

---

## 6. Verdict

**PRÊT AVEC RÉSERVES** — 93/93 tests, cycle E2E nominal complet (démarrage → réponses → fin → dosage 429 → `/ui` → isolation bilan), garde-fous de correction serveur et de périmètre avérés en exécution réelle. Réserve principale : le résumé de fin est incohérent quand la séance se termine sans avoir répondu à tous les items servis (`items=12, correctes=2, taux=0.67`) — à corriger avant exposition utilisateur, avec le cas « séance partielle » en test. Réserves secondaires : course sur le compteur de séances, essais dupliqués comptés dans le résumé, baseline RT figée.
