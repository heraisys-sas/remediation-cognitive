# Contrat d'API — Sprint 1 (module Entraînement)

Base : `/api/entrainement` — périmètre **hors médical**. Format JSON. Pas d'authentification (usage familial mono-utilisateur, Phase 1). Correction **côté serveur** : la réponse attendue d'un item n'est jamais envoyée au client avant la soumission de la réponse utilisateur.

## Endpoints

### GET /health
`{"status": "ok"}`

### GET /api/entrainement/themes
`{"themes": [{"id": "calcul-mental", "nom": "Calcul mental", "description": "Tables et calcul rapide, paliers progressifs"}, {"id": "anglais", …}, {"id": "python", …}, {"id": "memoire", "nom": "Mémoire", "description": "Empans de chiffres, séquences et associations — mémorisation progressive"}, {"id": "concentration", "nom": "Concentration", "description": "Calculs chaînés, double tâche et séries — une attention qui tient"}]}`

### POST /api/entrainement/{theme}/sessions
Démarre une séance. Sélection serveur : items dus (FSRS) d'abord, puis nouveaux du palier courant.
- `201` → `{"session_id": str, "items": [{"id": str, "type": str, "palier": int, "contenu": {...}}], "regles": {"max_items": 12, "duree_max_s": 600}}`
- `429` → `{"erreur": "limite_sessions_atteinte", "sessions_restantes_aujourdhui": 0}`

**Le payload `items` ne contient jamais `reponse`.**

### POST /api/entrainement/{theme}/sessions/{sid}/reponses
Corps : `{"item_id": str, "reponse": str|number, "temps_ms": int}`
- `200` → `{"correcte": bool, "attendue": str|number, "feedback": str}` (correction immédiate guidée)
- `404` session inconnue · `409` session déjà terminée · `404` item hors séance

### POST /api/entrainement/{theme}/sessions/{sid}/fin
Clôture la séance, applique FSRS + maîtrise, persiste.
- `200` → `{"resume": {"items": int, "correctes": int, "duree_s": int, "taux_reussite": float}, "arret_propose": bool, "motif_arret": null|"fatigue", "sessions_restantes_aujourdhui": int}`
- `409` si déjà terminée

## Règles serveur (garde-fous, non contournables)

1. **Dosage** : max 12 items/séance ; durée max 600 s ; **3 séances/jour** (paramétrable dans `backend/app/domain/dosage.py`).
2. **Fatigue** : `arret_propose = true` si RT moyen glissant > 1,25 × baseline **ou** taux d'erreur ≥ 0,40 — **proposition uniquement, jamais d'interruption forcée**.
3. **Vocabulaire** : neutre, ludique modéré — centralisé dans `backend/app/domain/messages.py` ; aucun terme clinique.
4. **Aucune norme populationnelle** dans les réponses API.
5. **Périmètre** : aucun endpoint `/api/bilan` ce sprint ; aucune donnée de bilan stockée.
6. **Stockage** : fichiers JSON sous `backend/data/entrainement/` (hors dépôt, `.gitignore`) — decks FSRS, maîtrise par palier, compteur séances/jour.
7. **Durée max** : au-delà de 600 s, la séance est clôturée automatiquement côté serveur (garde-fou de dosage — ce n'est pas une interruption par la fatigue) ; toute réponse suivante reçoit 409 `session_terminee`, les réponses déjà enregistrées restent persistées.

## Forme d'un item (conforme à content/schema-item.json)

```json
{"id": "cm-8-7x8", "type": "production", "palier": 8, "theme": "calcul-mental",
 "contenu": {"enonce": "7 × 8", "aide": null}, "reponse": {"valeur": 56}}
```

Types du sprint 1 : `production` (saisie libre), `prediction-sortie` (python : exécution mentale d'un snippet).

## Types d'exercices — sprint 2 (mémorisation & concentration)

Nouveaux thèmes `memoire` et `concentration`, nouvelles familles : `chaine-calcul`
(chaînes d'additions/soustractions évaluées de gauche à droite — la longueur 3 → 7
opérations croît la charge de mémoire de travail et conduit progressivement à la
fatigue, détectée par le garde-fou existant), `serie-manquante` (suites
arithmétiques/géométriques/alternées), `paires-associatives` (mot–nombre), et
activation des types `empan`, `n-back` (sonde temporelle), `double-tache`
(filtrage chiffres/lettres) sur ces thèmes.

### Affichage temporisé (phase de mémorisation)

Les items de ces familles portent `contenu.affichage` :
- `{"mode": "sequence", "duree_par_item_ms": int, "elements": [str,…]}` — éléments
  montrés un par un (250 ms de blanc entre chaque) ;
- `{"mode": "liste", "duree_totale_ms": int, "elements": [[str, str],…]}` — toutes
  les lignes pendant la durée totale.

Déroulé imposé à l'interface : **consigne → stimulus temporisé → le stimulus
DISPARAÎT → question → saisie**. Le temps de mémorisation ne compte pas dans
`temps_ms`. Le garde-fou de durée (600 s) couvre la séance entière, affichage inclus.

### Note d'honnêteté sur le stimulus

Le stimulus des items temporisés (séquence de chiffres, paires…) voyage dans le
payload client : en usage familial mono-utilisateur c'est assumé (l'interface ne
l'affiche que pendant la phase de mémorisation) ; un mode serveur-poussé pourra
être étudié plus tard si le besoin apparaît.

## Sprint 3 — accès au mot, vie sociale, aides progressives (ADR-004)

### Thèmes supplémentaires

`evocation` (« Retrouver le mot ») et `social` (« Vie sociale ») rejoignent les thèmes exposés par
`GET /api/entrainement/themes` (sept thèmes au total). Nouveaux types d'items : `rappel-indice`,
`reconnaissance`, `rappel-source`, `emotion-vignette`, `reponse-adaptee`, `lecture-intention`.

### Choix de réponse (`contenu.options`)

Les items à choix portent leurs propositions dans `contenu.options` (au moins trois, distinctes, la
réponse attendue figurant obligatoirement parmi elles). L'interface envoie la **proposition
sélectionnée** comme `reponse` ; la comparaison est tolérante (casse, accents, espaces, guillemets).

### Indices progressifs et essai « assisté »

Les items `rappel-indice` portent `contenu.indices` : hiérarchie d'aides
(`{ "type": "semantique" | "phonologique" | "orthographique" | "contextuel", "texte": "…" }`).
Un indice **ne contient jamais la réponse** (contrôle bloquant du validateur) ; révéler tous les
indices puis afficher la réponse est un geste d'interface.

`POST /api/entrainement/{theme}/sessions/{session_id}/reponses` accepte un champ **optionnel** :

```json
{"item_id": "ev-2-rappel-01", "reponse": "", "temps_ms": 4200, "indice_utilise": 4}
```

- `indice_utilise` : nombre d'indices consultés (`0` = sans aide). Absent = `0`.
- `indice_utilise = nb_indices + 1` : la réponse a été **affichée** → essai **assisté**.
- Hors bornes (`> nb_indices + 1`) → `422 reponse_invalide`.

Réponse (champs additifs) :

```json
{"correcte": false, "assistee": true, "attendue": "verre", "feedback": "Voici la réponse — on la reverra bientôt, sans indice cette fois."}
```

Un essai assisté n'est **pas** un échec signalé à l'utilisateur, mais il n'est pas non plus une
réussite pour le moteur : carte FSRS notée en échec, non compté dans `resume.correctes`.

### Résumé de fin de séance (champs additifs)

```json
{"resume": {"items": 8, "correctes": 6, "assistees": 1, "sans_aide": 4, "duree_s": 214, "taux_reussite": 0.75},
 "arret_propose": false, "motif_arret": null, "sessions_restantes_aujourdhui": 2}
```

`assistees` et `sans_aide` ne sont présents que pour les thèmes portant des indices. `sans_aide`
compte les items retrouvés **sans aucune aide** — c'est la mesure de progrès pertinente pour
l'accès au mot (moins d'aides nécessaires), pas la vitesse.

La baseline de temps servant à la détection de fatigue n'est alimentée que par les premières
réponses correctes **et** sans aide.

### Périmètre `/api/social` — missions hors écran et carnet

Base : `/api/social`. Périmètre hors médical, mais **stockage séparé** des données d'entraînement.

- `GET /api/social/missions` → `{"missions": [{id, niveau, titre, pourquoi, etapes[], duree_estimee_min, repere}, …], "ressentis": ["facile", "moyen", "difficile", "inattendu"]}`.
  Une mission n'a **aucune réponse attendue** : c'est une préparation d'interaction réelle.
- `GET /api/social/journal` → `{"entrees": [{id, mission_id, texte, ressenti, date}, …]}` (ordre chronologique).
- `POST /api/social/journal` `{"mission_id": "ms-01", "texte": "…", "ressenti": "facile"}` → `201 {"entree": {…}}`.
  `404 mission_inconnue` si la mission n'existe pas ; `422 note_invalide` si le texte est vide ou
  dépasse 2 000 caractères.

Stockage : `backend/data/journal/journal.json` — séparé de `backend/data/entrainement/`, jamais
joint aux données de séance (ADR-002 / ADR-004), borné aux 500 notes les plus récentes.
