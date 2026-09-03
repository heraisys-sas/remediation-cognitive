# Rapport lot contenu — sprint 1 (calcul mental + échantillons)

Date : 2026-09-03 · Agent : contenu (sous-agent) · Périmètre modifié : `content/` et `tools/` uniquement, aucun commit.

## Livrables

### 1. `tools/generate_items.py` — générateur calcul mental (stdlib uniquement)

- 9 paliers Kumon-like dans l'ordre imposé : ×2, ×5, ×10, ×3, ×4, ×6, ×7, ×8, ×9.
- Chaque palier couvre **toute la table dans les deux sens** (`a × b` et `b × a`, facteurs croisés 1..10) avec déduplication du carré → **19 items uniques par palier** (10 couples + 9 symétriques, le carré `n × n` une seule fois).
- Format strictement conforme à `content/schema-item.json` : `id` (`cm-<table>-<a>x<b>`, ex. `cm-7-7x8`), `type: production`, `module: entrainement`, `theme: calcul-mental`, `fonctions_ciblees: ["automatisation"]`, `palier`, `prerequis`, `cap_complexite: null`, `contenu {enonce: "7 × 8", aide: null}` (signe × U+00D7), `reponse {valeur: 56}`, `meta {auteur, date_creation, relecture_ortho {statut: a_revoir}}`.
- Options : `--dry-run` (simulation), `--date AAAA-MM-JJ` (défaut figé `2026-09-03` → régénération déterministe d'un contenu versionné).
- Docstrings en français, identifiants en anglais (conventions du dépôt).

### 2. Contenu généré — `content/entrainement/calcul-mental/`

| Fichier | Contenu | Items |
|---|---|---|
| `paliers/palier-01.json` | table ×2 | 19 |
| `paliers/palier-02.json` | table ×5 | 19 |
| `paliers/palier-03.json` | table ×10 | 19 |
| `paliers/palier-04.json` | table ×3 | 19 |
| `paliers/palier-05.json` | table ×4 | 19 |
| `paliers/palier-06.json` | table ×6 | 19 |
| `paliers/palier-07.json` | table ×7 | 19 |
| `paliers/palier-08.json` | table ×8 | 19 |
| `paliers/palier-09.json` | table ×9 | 19 |
| `paliers.json` | manifest ordonné (id, table, prerequis, fichier, nb_items) | 9 entrées |

**Total : 171 items de calcul mental.** Le manifest chaîne chaque palier au précédent (`cm-palier-N` a pour prerequis `cm-palier-(N-1)` ; palier 1 sans prerequis). Les items d'un palier portent le même prerequis.

### 3. Échantillons de généricité (formats autres que calcul mental)

- `content/entrainement/anglais/verbes-irreguliers.json` — **10 items** `production`, `theme: anglais/verbes-irreguliers`, `fonctions_ciblees: ["memorisation-longue"]`, énoncé `go → prétérit ?`, réponse texte (`went`). Verbes choisis à prétérit unique et non ambigu (go, have, make, take, come, see, give, find, think, tell).
- `content/entrainement/python/commandes/builtins.json` — **10 items** couvrant les 10 builtins demandés (len, sorted, enumerate, zip, sum, min, max, round, str.join, range) :
  - 5 × `production` (palier 1) : description → nom de la commande (ex. « Commande qui renvoie le nombre d'éléments d'une liste » → `len`) ;
  - 5 × `prediction-sortie` (palier 2, format le plus cognitif selon la spec) : snippet d'**une ligne, un seul niveau d'imbrication** (cap projet : 2 documenté dans `cap_complexite`), ex. `''.join(['a', 'b', 'c'])` → `abc`, `round(3.14159, 2)` → `3.14`.
- Réponses typées différemment (texte, entier, flottant) pour prouver que `reponse.valeur` n'est pas cantonné au numérique.

### 4. `tools/validate_items.py` — validateur minimal (stdlib uniquement, zéro dépendance)

Vérifie : champs requis et champs inconnus (`additionalProperties: false` du schéma), enums (`module`, `type`, `fonctions_ciblees`, statut de relecture — lus directement dans `schema-item.json`), motif de l'`id` + **unicité globale sur tout `content/`**, `palier` entier ≥ 1, `prerequis` tableau de chaînes avec résolution des références `cm-palier-N`, `cap_complexite` chaîne/null, `contenu`/`reponse` objets, dates ISO de `meta`.

Cohérence palier/manifest (thème `calcul-mental`) : existence du palier dans le manifest, `id` conforme à `cm-<table>-<a>x<b>` avec la table du manifest, un facteur = table, **réponse = a × b**, `nb_items` du manifest = comptage réel, numéros de palier portés par les items. Un manifest est reconnu par sa liste `paliers` ; exit code 0/1.

**Test négatif** (copie jetable hors dépôt, 10 altérations injectées) : les 13 erreurs attendues sont détectées — champ inconnu, module/type/fonction/statut hors enum, doublon d'id inter-fichiers, réponse ≠ a×b, palier 0, id non conforme au motif du thème, prerequis fantôme, JSON cassé (signalé proprement, exit=1). Correction apportée à la suite de ce test : les fichiers JSON non parsables sont désormais signalés sans exception au lieu d'un `KeyError`.

## Sortie complète du validateur (dépôt réel)

```
Validation du contenu : 12 fichier(s) JSON sous content/
Schéma de référence : content/schema-item.json
[OK]     content/entrainement/anglais/verbes-irreguliers.json (10 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-01.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-02.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-03.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-04.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-05.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-06.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-07.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-08.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers/palier-09.json (19 item(s))
[OK]     content/entrainement/calcul-mental/paliers.json (manifest)
[OK]     content/entrainement/python/commandes/builtins.json (10 item(s))
Bilan : 12 fichier(s), 191 item(s), 1 manifest(s), 0 erreur(s).
```

Total contenu : **191 items** (171 calcul mental + 10 anglais + 10 Python), 0 erreur.

## Décisions et choix

1. **19 items/palier (et non ~20 exacts)** : la consigne « deux sens + déduplication » donne 10 couples × 2 sens − 1 carré = 19 ; conforme à « ~20 ».
2. **Chevauchement inter-paliers assumé** : `2×5` existe au palier 1 (`cm-2-2x5`) et au palier 2 (`cm-5-5x2`) — exigence « chaque palier couvre toute la table dans les deux sens » ; les ids distincts évitent toute collision.
3. **Ids de paliers = `cm-palier-1…9`** : espace de noms dédié, utilisables comme concepts dans le graphe de connaissances (`prerequis` des items et du manifest pointent vers eux). À harmoniser plus tard si `backend/app/kg/` fixe une autre convention.
4. **`date_creation` figée par défaut** (`2026-09-03`) : une régénération ne fait pas glisser les métadonnées d'un contenu versionné ; `--date` permet l'override.
5. **`meta.auteur`** : `generation-automatique (tools/generate_items.py)` pour le contenu généré, `agent-sprint1` pour les échantillons rédigés à la main — traçabilité de l'origine.
6. **builtins.json à la racine de `commandes/`** (conforme à la consigne) alors qu'existe déjà le dossier `commandes/builtins/` (README seul) : coexistence sans conflit, à réconcilier éventuellement lors de l'intégration.
7. **Paliers 1/2 pour les échantillons Python** : production avant prédiction de sortie, progression conforme à la spec (`errorless → production → prédiction`) ; `prerequis` laissé vide faute de convention d'ids de concepts pour l'anglais/Python.
8. **Originalité** : contenu 100 % procédural ou facts de langue/standard Python — aucun item issu de matériel protégé (ECPA/Pearson, GREFEX, TEA-Ch). Relecture orthophoniste posée à `a_revoir` partout.
9. **Sécurité d'exécution** : le test négatif a d'abord tenté un `rm -rf` sur la copie jetable — refusé par le Safety Guard ; refait en créant un répertoire frais sans aucune suppression.

## Hors périmètre / à noter pour l'orchestrateur

- Aucun commit effectué ; `git status` montre aussi des fichiers modifiés par d'autres lots (`engine/`, `docs/30-technique/api-contract.md`) — non touchés par ce lot.
- Le validateur ne gère pas encore les formats `qcm`, `restitution-errorless`, etc. au-delà des checks génériques du schéma (non requis à ce stade).
