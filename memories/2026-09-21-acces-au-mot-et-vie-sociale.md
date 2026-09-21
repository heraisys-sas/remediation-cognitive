# 2026-09-21 — Accès au mot et vie sociale (sprint 3)

## Demande

Suite à la note d'orientation : « implémente les exercices ». Contexte explicite : il ne s'agit pas de commercialiser mais d'évaluer la capacité à produire ce qui est demandé au meilleur de l'état de l'art, pour un **test isolé et confidentiel sous le contrôle d'une spécialiste**.

## Livré

- **Thème `evocation`** (« Retrouver le mot », 5 paliers × 10 = 50 items) : reconnaissance (3 propositions), rappel indicé (indices catégorie → attaque phonologique → forme écrite), rappel de la source (fiche temporisée puis question sur le contexte).
- **Thème `social`** (« Vie sociale », 4 paliers × 10 = 40 items) : vignettes d'émotion, réponses adaptées, lecture d'intention. Aucune image (pas de visage à droits) : les indices sont dans ce que dit ou fait la personne.
- **8 missions hors écran** + **carnet** (`/api/social/journal`) dans un stockage **séparé** (`backend/data/journal/`).
- **Aides progressives** : `contenu.indices` + champ `indice_utilise` ; l'essai voit sa réponse affichée → `assistee = true`, FSRS en échec, feedback neutre, jamais d'échec imposé (errorless). Résumé enrichi de `assistees` et `sans_aide`.
- **Contrôles** : validateur étendu (options ≥ 3 dont la réponse ; indices ≥ 2 sans jamais contenir la réponse ; fichiers de missions) ; `tools/verifier_reponses.py` (587 items, 0 anomalie) ; `tools/verifier_interface.py` (nouveau, cohérence identifiants interface ↔ HTML).
- **Tests** : 106 passed (10 nouveaux) ; essai de bout en bout sur serveur réel (7 thèmes, missions, note de carnet, séance d'accès au mot, `/ui` servi).
- **Docs** : ADR-004, contrat d'API (sprint 3), module-entraînement (deux sections), taxonomie (7 familles), CHANGELOG, READMEs de contenu.

## Pièges & apprentissages

- Le validateur a attrapé un vrai défaut de contenu : l'attaque phonologique du mot « clé » donnait la réponse (« clé… » contient « cle »). Règle utile : un indice de mot court doit rester partiel (« cl… »). Le contrôle « aucun indice ne contient la réponse » (normalisation accents/casse/espaces) est ce qui l'a détecté — le garder bloquant.
- Le test « forcer le palier » écrivait dans `tmp_path/data/entrainement/<theme>` alors que `StockageJSON(racine=tmp_path/"data")` écrit dans `tmp_path/data/<theme>` : bien relire la racine réelle avant de forger un état.
- L'essai assisté ne doit pas nourrir la baseline de temps (sinon la détection de fatigue compare des temps non comparables) : seul un rappel **correct et sans aide** alimente la médiane.
- Le journal contient des éléments de vie privée : stockage séparé dès le premier jour, aucune jointure avec les données de séance.
- Choix assumé : pas de visuels de visages (droits + consentement). La cognition sociale est travaillée sur des situations textuelles ; des visuels libres de droits pourront être ajoutés plus tard.

## Reste à faire

- Relecture orthophoniste formelle des 90 nouveaux items et des 8 missions.
- Errorless d'entrée de palier et prerequis anglais/Python (toujours reportés).
- Éventuel mode multi-profils si l'usage dépasse le foyer (carnet et stockages à revoir alors).
