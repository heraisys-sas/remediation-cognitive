# Rapport sous-agent — Moteur adaptatif commun (Sprint 1)

**Date** : 2026-09-03 · **Périmètre** : `engine/` exclusivement · **Statut** : ✅ terminé, 55/55 tests verts

## Fichiers créés / modifiés

| Fichier | Action | Contenu |
|---|---|---|
| `engine/srs/fsrs.py` | réécrit (stub → implémentation) | Encapsulation du paquet officiel `fsrs` 6.3.2 : `CarteFSRS` (item_id + état FSRS interne), `planifier(carte, note, maintenant) -> (carte_mise_a_jour, echeance)`, `est_due(carte, maintenant) -> bool`, `to_dict`/`from_dict` pour la persistance backend |
| `engine/adaptive/rule.py` | complété | `ajuster_palier` conservée telle quelle ; ajout `calculer_taux_glissant(historique: list[bool], fenetre: int = 8) -> float` |
| `engine/session/runner.py` | réécrit (stub → implémentation) | `SessionRunner(items, max_items=12, duree_max_s=600, baseline_rt_ms=1000)` : `prochain_item()`, `enregistrer_reponse()` → dict de feedback, `doit_proposer_arret()` → bool, `terminer()` → dict résumé |
| `engine/mastery/criteria.py` | complété | `palier_maitrise` conservée telle quelle ; ajout `palier_maitrise_historique(historique, palier=None, seuil=0.9, sessions_consecutives=3)` pour le suivi par palier |
| `engine/tests/test_fsrs.py` | créé | 14 tests FSRS |
| `engine/tests/test_session.py` | créé | 20 tests runner |
| `engine/tests/test_adaptive.py` | étendu | 4 tests d'origine conservés + 6 tests fenêtre glissante |
| `engine/tests/test_mastery.py` | étendu | 3 tests d'origine conservés + 9 tests (dont suivi par palier) |

Aucun autre dossier touché (vérifié via `git status` : seules les modifications listées ci-dessus + fichiers non suivis préexistants). Aucun commit git effectué.

## Décisions prises

1. **Paquet `fsrs` installé avec succès** (`pip3 install fsrs` → v6.3.2, Python 3.13.1). Le **fallback SM-2 n'a pas été nécessaire** ; l'implémentation s'appuie entièrement sur la bibliothèque officielle, encapsulée (`fsrs.Card` jamais exposé).
2. **Planificateur déterministe** : `Scheduler(enable_fuzzing=False)` — les échéances sont reproductibles (exigence de testabilité et de suivi clinique). `desired_retention` reste au défaut FSRS (0.9) ; tout ajustement clinique devra passer par un ADR.
3. **Notes 1..4** mappées sur FSRS : 1 = encore (Again), 2 = difficile (Hard), 3 = bon (Good), 4 = facile (Easy).
4. **`planifier` immuable** : retourne une nouvelle `CarteFSRS`, ne mute pas la carte reçue (permet de brancher plusieurs futurs depuis la même carte ; facilité de test).
5. **Datetimes** : naïfs interprétés comme UTC ; toutes les échéances produites sont UTC-aware. `est_due` est inclusive (échéance exacte = due) ; une carte jamais planifiée est due.
6. **Fatigue = proposition seulement** (garde-fou clinique) : `doit_proposer_arret()` renvoie un booléen pur (RT moyen glissant > 1,25 × baseline OU taux d'erreur glissant ≥ 0,40) ; **aucun** appel du runner n'est bloqué par la fatigue — les seules conditions d'arrêt de service d'items sont le quota `max_items`, `duree_max_s` et la fin de liste. Un test dédié (`test_la_fatigue_ninterrompt_jamais_la_seance`) verrouille ce comportement.
7. **Fenêtre fatigue = 5 réponses** avec plancher anti-bruit de 3 réponses (pas d'alerte sur des données insuffisantes) — constantes module `FENETRE_FATIGUE`, `SEUIL_RT_FATIGUE`, `SEUIL_TAUX_ERREUR`, `MIN_REPONSES_FATIGUE`. Le taux d'erreur glissant réutilise `calculer_taux_glissant` du module adaptatif.
8. **Runner sans persistance** : les items sont injectés déjà sélectionnés (règle adaptative + FSRS en amont, responsabilité de l'appelant) ; chaque item expose `item_id` (attribut ou clé de dict) ; `depart` injectable pour tests déterministes ; validation fail-fast (item sans id, item non servi, temps_ms invalide, paramètres ≤ 0).
9. **Sérialisation** : `CarteFSRS.to_dict()/from_dict()` (item_id + état FSRS natif) — le backend reste seul responsable du stockage (ADR-002, aucune I/O dans le moteur).
10. **Suivi par palier (mastery)** : `palier_maitrise_historique` filtre les sessions par palier sur un historique chronologique `[(palier, taux)]` — un changement de palier réinitialise le comptage ; palier courant = le plus récent par défaut.
11. **Conventions** : docstrings/commentaires en français, identifiants de l'API public conformes à la mission et au code existant du dépôt (français : `planifier`, `est_due`…) ; zéro dépendance ajoutée hors `fsrs` (stdlib + `fsrs` + `pytest` pour les tests).

## Sortie pytest complète

Commande : `python3 -m pytest -q engine/tests` (depuis `remediation-cognitive/`)

```
.......................................................                  [100%]
55 passed in 0.07s
```

Suite complète du dépôt (`python3 -m pytest -q`, backend/tests + engine/tests) :

```
.......................................................                  [100%]
55 passed in 0.06s
```

Répartition : 14 tests FSRS (`test_fsrs.py`), 20 tests runner (`test_session.py`), 10 tests adaptatif (`test_adaptive.py`), 11 tests maîtrise (`test_mastery.py`).

## Couverture des exigences de test de la mission

- **FSRS** : échéance croît après rappel réussi (`test_echeance_croit_apres_rappel_reussi`), régresse/retombe après échec (`test_echeance_retombe_apres_echec`), `est_due` avant/à/après échéance + carte neuve due immédiatement, note facile > bon, difficulté baisse avec facile, immutabilité, notes invalides, datetime naïf, roundtrip sérialisation.
- **Runner** : arrêt PROPOSÉ jamais forcé (booléen unique, aucune exception, aucun blocage — 3 tests dédiés), seuils RT strictement supérieurs / erreur inclusive, anti-bruit, résumé cohérent (items/correctes/erreurs/duree_s/taux_reussite/rt_moyen_ms/alerte_fatigue), session vide, items en dict, validations.
- **Adaptatif** : fenêtre glissante (défaut 8, personnalisée, plus grande que l'historique, vide, bornes, fenêtre invalide).
- **Mastery** : 90 % × 3 sessions conservé, comptage par palier réinitialisé au changement, palier explicite, historique vide.
