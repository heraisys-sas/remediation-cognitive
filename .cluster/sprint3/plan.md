# Sprint 3 — Accès au mot et vie sociale

## Demande

« Implémente les exercices » — les deux familles de la note d'orientation (récupération d'un souvenir présent mais non remémoré ; rééducation sociale après isolement prolongé). Contexte : test isolé et confidentiel sous contrôle d'une spécialiste, pas une mise sur le marché.

## Périmètre retenu

1. **Thème `evocation`** — reconnaissance, rappel indicé à indices progressifs, rappel de la source (50 items, 5 paliers).
2. **Thème `social`** — vignettes d'émotion, réponses adaptées, lecture d'intention (40 items, 4 paliers).
3. **Missions hors écran + carnet** — 8 missions graduées, notes personnelles dans un stockage séparé.
4. **Aides progressives mesurées** — champ `indice_utilise`, essai « assisté » sans erreur imposée, résumé enrichi (`assistees`, `sans_aide`).

Hors périmètre assumé : visuels de visages (droits et consentement) — la cognition sociale est travaillée sur des situations textuelles ; missions réalisées hors écran.

## Décisions structurantes

- **ADR-004** — `contenu.options` (≥ 3 propositions dont la réponse), `contenu.indices` (≥ 2, jamais la réponse), champ `indice_utilise` et essai assisté, périmètre `/api/social` et stockage `backend/data/journal/`.
- La baseline de temps (fatigue) n'est alimentée que par les rappels **corrects et sans aide**.
- Le contenu est rédigé puis assemblé de façon déterministe (`tools/generer_evocation_social.py`, graine 20260920).

## Contrôles

- `tools/validate_items.py` — schéma, manifests, options, indices (0 erreur ; a détecté une fuite d'indice sur « clé »).
- `tools/verifier_reponses.py` — 587 items recalculés, 0 anomalie.
- `tools/verifier_interface.py` — identifiants demandés par l'interface ↔ présents dans l'HTML (nouveau).
- `python3 -m pytest -q` — 106 passed.
- Bout en bout sur serveur réel : 7 thèmes, missions, note de carnet, séance d'accès au mot, `/ui` servi.

## Délégation (cluster_bypass_reason)

Trois envois d'agents acceptés par la plateforme ont échoué à l'exécution (**FailoverError HTTP 403**, 0 jeton produit) : revue de conformité du contenu du sprint 2, vérification des réponses, recherche documentaire rappel/socialisation. Aucun livrable d'agent n'a été produit ; le travail a été mené en direct et la vérification remplacée par un script versionné dans le dépôt.

## Statut

Livré : contenu, serveur, interface, tests, documentation (ADR-004, contrat, specs, taxonomie, CHANGELOG, READMEs), rapport de sprint.
