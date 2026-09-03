# Contrat d'API — Sprint 1 (module Entraînement)

Base : `/api/entrainement` — périmètre **hors médical**. Format JSON. Pas d'authentification (usage familial mono-utilisateur, Phase 1). Correction **côté serveur** : la réponse attendue d'un item n'est jamais envoyée au client avant la soumission de la réponse utilisateur.

## Endpoints

### GET /health
`{"status": "ok"}`

### GET /api/entrainement/themes
`{"themes": [{"id": "calcul-mental", "nom": "Calcul mental", "description": "Tables et calcul rapide, paliers progressifs"}, ...]}`

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

Types du sprint : `production` (saisie libre), `prediction-sortie` (python : exécution mentale d'un snippet, cap 1 niveau d'imbrication en échantillon).
