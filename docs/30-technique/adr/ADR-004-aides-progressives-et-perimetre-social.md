# ADR-004 — Aides progressives, réponses à choisir et périmètre social

**Statut** : accepté (2026-09-21)

## Contexte

Deux besoins cliniques ne rentraient pas dans le format en vigueur :

1. **Entraîner la récupération**, pas seulement l'apprentissage : pour un contenu déjà su mais inaccessible, l'exercice doit proposer des **aides graduées** et mesurer **l'aide réellement nécessaire**. Le format d'item ne portait que `enonce`/`aide`, et l'API ne transmettait aucun indicateur d'aide.
2. **Rééduquer le lien social** après un isolement prolongé : la mise en situation réelle se prépare, se répète à froid et se note — mais une mission n'a pas de « bonne réponse », et le récit qui en découle est un élément de vie privée.

## Décision

**1. Format d'item étendu (contenu, validé par `tools/validate_items.py`)**

- `contenu.options` — propositions pour les types à choix (`reconnaissance`, `rappel-source`, `emotion-vignette`, `reponse-adaptee`, `lecture-intention`) : au moins trois propositions distinctes, dont la réponse attendue.
- `contenu.indices` — hiérarchie d'aides des items `rappel-indice` : au moins deux entrées `{type, texte}` (types `semantique`, `phonologique`, `orthographique`, `contextuel`). **Aucun indice ne doit contenir la réponse** : c'est un contrôle bloquant du validateur, la révélation complète étant un mode d'interface, jamais un indice de contenu.
- Types ajoutés : `rappel-indice`, `reconnaissance`, `rappel-source`, `emotion-vignette`, `reponse-adaptee`, `lecture-intention`.
- Fonctions ciblées ajoutées : `acces-lexical`, `recuperation`, `cognition-sociale`, `pragmatique`.

**2. Aide mesurée et essai « assisté » (API entraînement)**

- `POST /api/entrainement/{theme}/sessions/{sid}/reponses` accepte un champ optionnel `indice_utilise` (entier, `0` à `nb_indices + 1`).
- `indice_utilise = nb_indices + 1` signifie que la réponse a été **affichée** : l'essai est dit **assisté** — `correcte = false`, `assistee = true`, feedback neutre, carte FSRS notée en échec. Aucune erreur n'est commise par l'utilisateur (principe errorless) sans donner au moteur un faux signal de réussite.
- La réponse inclut désormais `assistee` ; le résumé de fin gagne `assistees` et `sans_aide` (nombre d'items retrouvés sans aucune aide) — présents uniquement pour les thèmes à indices.
- La baseline de temps (détection de fatigue) n'est alimentée que par les premières réponses **correctes et sans aide** : un essai aidé fausserait la comparaison.

**3. Périmètre social séparé (`/api/social`)**

- `GET /api/social/missions` — missions de préparation (contenu versionné `content/entrainement/social/missions.json`), sans réponse attendue.
- `GET|POST /api/social/journal` — carnet personnel de l'utilisateur.
- Stockage dédié : `backend/data/journal/journal.json`, **séparé** des données d'entraînement (ADR-002) car il contient des éléments de vie privée ; aucune jointure avec les données de séance.

## Conséquences

- (+) La récupération devient entraînable et mesurable (aide nécessaire, reprises sans erreur) ; les missions et le carnet existent hors du moteur de séance, donc sans fausser paliers, FSRS ou maîtrise.
- (+) Le principe errorless est respecté jusque dans l'interface : l'échec n'est jamais imposé, mais il n'est pas maquillé en réussite côté moteur.
- (+) Le carnet vit dans son propre stockage — un futur module de bilan n'aura pas à démêler des données personnelles.
- (−) Le contrat d'API et le schéma d'item s'étendent : compatibilité ascendante assurée (champ optionnel, champs de réponse additifs), mais toute modification ultérieure devra rester aussi prudente.
- (−) Le contenu devient plus exigeant à relire : indices à valider cliniquement (formulation, absence de fuite) — la relecture orthophoniste reste à faire.
- (−) Troisième périmètre de stockage à tenir isolé (entraînement, journal, bilan à venir).


## Suivi (2026-09-24)

Le **thème d'entraînement « vie sociale » a été retiré** (jugé trop simple à l'usage) et le
périmètre annexe a été renommé : `/api/social` → **`/api/missions`**, les missions vivant
désormais dans `content/missions/missions.json`. Le reste de la décision (aides progressives,
options, essai assisté, stockage séparé du carnet) reste inchangé et en vigueur.
