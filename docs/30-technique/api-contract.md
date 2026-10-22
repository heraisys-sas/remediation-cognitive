# Contrat d'API — Sprint 1 (module Entraînement)

Base : `/api/entrainement` — périmètre **hors médical**. Format JSON. Pas d'authentification (usage familial mono-utilisateur, Phase 1). Correction **côté serveur** : la réponse attendue d'un item n'est jamais envoyée au client avant la soumission de la réponse utilisateur.

## Endpoints

### GET /health
`{"status": "ok"}`

### GET /api/entrainement/themes
Chaque thème porte `paliers` et, quand plusieurs tâches cohabitent sous une carte, `parcours`: `[{"id", "nom", "description"?, "paliers", "palier_depart"?}]`. Les parcours disposent d'une progression indépendante (ADR-023).

### POST /api/entrainement/{theme}/sessions
Démarre une séance. Sélection serveur : items dus (FSRS) d'abord, puis nouveaux du palier courant. Une progression neuve de Calcul mental commence au palier 5 ; après au moins huit réponses, une première séance sous 50 % ramène le prochain départ automatique au palier 3 (ADR-023). En Calcul mental, exercice court pratiqué volontairement, les places encore libres peuvent être complétées par les cartes non dues dont l'échéance est la plus proche : une troisième séance ne devient donc pas vide après épuisement des 14 à 19 items du palier. Exception pour les contenus à `etape_progression` (déduction) : réserver la moitié des places aux nouveautés disponibles dans l'ordre des étapes, et prioriser les révisions avancées (ADR-017). Les trois séances du critère de maîtrise doivent chacune comporter une réponse de l'étape finale ; elles sont suivies dans `historique_etapes`, séparément des anciens taux conservés.

**Corps facultatif** (`DemarrageOptionnel`) : `{"rejouer_palier": true}` — inclut les exercices déjà vus et non dus du palier choisi, avec le même quota et sans remise à zéro (ADR-036) ; `{"palier": N}` — essai sur un palier précis (la progression ne peut pas reculer) ; `{"parcours": "mots"}` — progression homogène choisie dans la carte ; `{"sans_limite_sessions": true}` — dérogation explicite au plafond de séances du jour, **accordée par le serveur pour tous les thèmes** (fenêtre du jour ou de la semaine selon la catégorie — ADR-021).

- `201` → `{"session_id": str, "parcours": str|null, "items": [{"id": str, "type": str, "palier": int, "contenu": {...}}], "regles": {"max_items": 12, "duree_max_s": 600}}` — les valeurs dépendent du thème (déduction : 6 exercices).
- `429` → `{"erreur": "limite_sessions_atteinte", "sessions_restantes_aujourdhui": 0}` — refus du plafond de la fenêtre ; une dérogation accordée le lève (ADR-021).

**Le payload `items` ne contient jamais `reponse`.**

### POST /api/entrainement/{theme}/sessions/{sid}/reponses
Corps : `{"item_id": str, "reponse": str|number, "temps_ms": int}`
- `200` → `{"correcte": bool, "attendue": str|number, "feedback": str}` (correction immédiate guidée)
- `404` session inconnue · `409` session déjà terminée · `404` item hors séance

### POST /api/entrainement/{theme}/sessions/{sid}/fin

*Idempotent* : si la séance est déjà terminée (double clic, ou clôture automatique par la durée maximale), l'appel renvoie `200` avec **le même résumé** — le client doit pouvoir afficher le résumé dans tous les cas.
Clôture la séance, applique FSRS + maîtrise, persiste.
- `200` → `{"resume": {"items": int, "correctes": int, "duree_s": int, "taux_reussite": float}, "arret_propose": bool, "motif_arret": null|"fatigue", "sessions_restantes_aujourdhui": int}`
- `409` seulement si la séance est close sans résumé conservé (cas devenu théorique)

## Règles serveur (garde-fous)

1. **Dosage** : max 12 items/séance (6 pour la déduction, voir `dosage.parametres_seance`) ; durée max 600 s ; **3 séances/jour** par défaut pour l'entraînement, **6 pour Calcul mental**, **1 séance/semaine** pour l'évaluation (semaine calendaire, lundi–dimanche ; paramétrable dans `backend/app/domain/dosage.py`) ; la limite d'un thème peut être **levée pour sa fenêtre en cours par une dérogation explicite** (`sans_limite_sessions` — ADR-021) ; le compteur continue de compter les séances jouées.
2. **Fatigue** : `arret_propose = true` si RT moyen glissant > 1,25 × baseline **ou** taux d'erreur ≥ 0,40 — **proposition uniquement, jamais d'interruption forcée**.
3. **Vocabulaire** : neutre, ludique modéré — centralisé dans `backend/app/domain/messages.py` ; aucun terme clinique.
4. **Aucune norme populationnelle** dans les réponses API.
5. **Périmètre** : aucun endpoint `/api/bilan` ce sprint ; aucune donnée de bilan stockée.
6. **Stockage** : fichiers JSON sous `backend/data/entrainement/` (hors dépôt, `.gitignore`) — decks FSRS, maîtrise par palier, compteur séances/jour. Un parcours utilise un dossier propre (`memoire--mots`) ; le compteur du quota reste celui du thème parent.
7. **Durée max (600 s)** : la réponse **en cours est toujours conservée** — on ne refuse jamais le travail fait. La durée est **proposée** (ADR-010) : `arret_propose: true`, `motif_arret: "duree"`, renvoyé **une seule fois** ; la séance reste ouverte, la personne décide de continuer ou de terminer. Le code de clôture automatique subsiste pour un thème qui demanderait un jour une limite ferme (`seance_terminee: true`, réponse suivante en 409).

## Forme d'un item (conforme à content/schema-item.json)

```json
{"id": "cm-8-7x8", "type": "production", "palier": 8, "theme": "calcul-mental",
 "contenu": {"enonce": "7 × 8", "aide": null}, "reponse": {"valeur": 56}}
```

Types du sprint 1 : `production` (saisie libre), `prediction-sortie` (python : exécution mentale d'un snippet).

## Types d'exercices — sprint 2 (mémorisation)

Le thème `memoire` active les types `empan`, `n-back` (sonde temporelle) et
`paires-associatives` (mot–nombre). L'ancien thème `concentration` et ses types
propres ont été retirés le 2026-10-01.

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

## Sprint 3 — accès au mot, aides progressives (ADR-004)

### Thèmes supplémentaires

`evocation` (« Retrouver le mot ») rejoint les thèmes exposés par
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
 "arret_propose": false, "motif_arret": null, "sessions_restantes_aujourdhui": 2, "fenetre_sessions": "jour"}
```

`sessions_restantes_aujourdhui` reste le décompte, dans la **fenêtre du thème** (`fenetre_sessions` : `jour` pour l'entraînement, `semaine` pour l'évaluation).

`assistees` et `sans_aide` ne sont présents que pour les thèmes portant des indices. `sans_aide`
compte les items retrouvés **sans aucune aide** — c'est la mesure de progrès pertinente pour
l'accès au mot (moins d'aides nécessaires), pas la vitesse.

La baseline de temps servant à la détection de fatigue n'est alimentée que par les premières
réponses correctes **et** sans aide.

### Périmètre `/api/missions` — missions dans la vraie vie et carnet

> Le thème d'entraînement « vie sociale » a été retiré (trop simple) ; les missions d'interaction réelle sont conservées. Les routes ont suivi le renommage : `/api/social` → `/api/missions`.

Base : `/api/missions`. Périmètre hors médical, mais **stockage séparé** des données d'entraînement.

- `GET /api/missions` → `{"missions": [{id, niveau, titre, pourquoi, etapes[], duree_estimee_min, repere}, …], "ressentis": ["facile", "moyen", "difficile", "inattendu"]}`.
  Une mission n'a **aucune réponse attendue** : c'est une préparation d'interaction réelle.
- `GET /api/missions/journal` → `{"entrees": [{id, mission_id, texte, ressenti, date}, …]}` (ordre chronologique).
- `POST /api/missions/journal` `{"mission_id": "ms-01", "texte": "…", "ressenti": "facile"}` → `201 {"entree": {…}}`.
  `404 mission_inconnue` si la mission n'existe pas ; `422 note_invalide` si le texte est vide ou
  dépasse 2 000 caractères.

Stockage : `backend/data/journal/journal.json` — séparé de `backend/data/entrainement/`, jamais
joint aux données de séance (ADR-002 / ADR-004), borné aux 500 notes les plus récentes.

## Sprint 4 — empan de mots, rappel libre de séries, rythme d'affichage (ADR-005)

### Empan de mots (`empan-mots`, thème `memoire`, paliers 9 à 12)

Séquence de mots affichés un par un (`mode: "sequence"`, 2 s visibles puis 2 s de
blanc par élément), à
retranscrire **dans l'ordre** (ou à l'envers selon l'énoncé). La comparaison est
ordonnée et tolérante à la saisie : accents, casse et ponctuation ignorés, ordre
significatif.

### Rappel libre (`rappel-libre`, thème `rappel-series`)

```json
{
  "type": "rappel-libre",
  "contenu": {
    "consigne": "Mémorise chaque série de mots, l'une après l'autre.",
    "affichage": {
      "mode": "series",
      "series": [["chat", "lune", "porte"], ["table", "nuage", "crayon"]],
      "duree_par_item_ms": 2000,
      "pause_item_ms": 2000,
      "pause_serie_ms": 3000
    },
    "delai_s": 20,
    "portee": "toutes-series",
    "enonce": "Écris tous les mots dont tu te souviens, toutes séries confondues, séparés par des espaces.",
    "aide": "Note d'abord les mots qui viennent sans effort, puis cherche les autres."
  },
  "reponse": { "valeur": ["chat", "lune", "porte", "table", "nuage", "crayon"], "seuil": 0.6 }
}
```

- `affichage.mode: "series"` — les séries sont présentées l'une après l'autre, avec
  une pause entre elles ; un mot ne peut pas apparaître dans deux séries.
- `delai_s` — attente (0 à 180 s) entre l'affichage et la question : **rappel
  différé**. L'interface affiche un compte à rebours et laisse passer l'attente.
- `portee` — `toutes-series` (rappel de l'ensemble) ou `premiere-serie`.
- `reponse.valeur` — **liste** des mots cibles ; `reponse.seuil` — part de mots à
  retrouver (0,25 à 1).

Correction serveur : réussite si `mots retrouvés / cibles ≥ seuil`. Ordre
indifférent, accents et casse ignorés, pluriel simple (`mot` + « s ») toléré, mots
en trop sans pénalité. La réponse renvoie `attendue` sous forme de **liste**, ce qui
permet à l'interface d'afficher « Retrouvés : n sur m » puis les mots manquants —
jamais une note, jamais une norme.

### Invariantes de contenu ajoutées au validateur

- séquences et séries : **2000 ms d'affichage puis 2000 ms de blanc** par élément ;
- aucun mot dupliqué dans une séquence ni entre les séries d'un même item ;
- les cibles déclarées correspondent exactement aux séries affichées (selon la portée) ;
- seuil et délai bornés ; modes d'affichage connus (`sequence`, `liste`, `series`).

## Sprint 5 — programme d'entraînement (ADR-006)

### GET /api/programme

Renvoie le programme de 8 semaines, le **plan du jour** et les règles de progression.
La date de début est posée au premier appel et **n'est plus jamais déplacée** par la
suite (relire le programme ne décale pas le calendrier).

```json
{
  "programme": { "titre": "Programme de 8 semaines", "duree_semaines": 8, "semaines": [ … ], "regles": { … } },
  "date_debut": "2026-09-22",
  "aujourd_hui": {
    "semaine": 1, "jour": 1, "type": "seance", "duree_min": 6,
    "themes": ["calcul-mental"], "themes_extra": [],
    "plafond_palier": { "calcul-mental": 2, "memoire": 2, "…": 2 },
    "jour_depuis_debut": 1, "jours_restants": 55, "termine": false
  },
  "regles": { "progression": "…", "fatigue": "…", "jours_manques": "…", "alternance": "…", "duree": "…", "recul": "…" }
}
```

- `type` : `seance` (un thème), `legere` (journée courte, `themes: ["au-choix"]` et
  `themes_extra` proposés), `repos` (aucun thème).
- Hors période : `aujourd_hui.type` vaut `a_venir` (avant la date de début) ou
  `termine` (après la huitième semaine, jamais prolongée d'office).

**Le programme ne contraint rien** : `plafond_palier` est une borne haute de
difficulté pour la semaine. L'avancement réel d'un palier reste décidé par la
maîtrise (90 % × 3 séances) et par la tolérance à la fatigue. Aucun taux
d'observance ni de complétion n'est calculé — ce ne serait pas une mesure clinique.

Stockage : `backend/data/programme/programme.json` (hors dépôt), limité à la date de
début — périmètre entraînement, aucune donnée de santé (ADR-002).


## Extension 2026-10-01 (ADR-022)

Catégorie de thème `cible` pour les exercices ciblés (trois séances/jour). Nouveaux thèmes `series-entendues`, `actualiser-consigne`, `comparer-documents`, `reperer-essentiel`. Les trois derniers acceptent une réponse objet : clés des champs/messages, valeurs textuelles. Après soumission, `detail_fonctionnel` décrit les lignes (`label`, `correcte`, `attendue`, `explication`) et les compteurs `omissions`/`fausses_selections` du filtrage. Le reste du contrat séance/fin est inchangé.

Extension du 2 octobre : le type `reprise-interrompue` de Garder le cap reçoit `{points: {id: "valide"|"reprendre"}, reprise: id, interruption: texte}`. `interruption` atteste seulement que le détour a été accompli et n’est pas noté. Le retour `detail_fonctionnel` corrige les quatre points et le point de reprise.

### Propriétés d’interface des thèmes (ADR-037)

Chaque thème de `GET /api/entrainement/themes` fournit aussi `interface` :
`extra` (section d’appoint), `francais` (prononciation française), `dictee`
(réponse dictée autorisée par la nature du thème). Le serveur dérive ces trois
booléens du catalogue ; le client continue de vérifier les capacités du poste.

## Scènes de contexte — mémorisation puis rappel (ADR-039)

POST …/reponses accepte `memorisation: bool` (défaut false). True est réservé aux items `rappel-source` ayant une image, avant leur réponse de rappel : correction immédiate et attendue retournées, aucune inscription dans moteur/FSRS/maîtrise/baseline. Hors de ce périmètre : 422. Le client l’envoie pendant la découverte ; le rappel final utilise la réponse ordinaire et détermine le résumé et la progression. Un arrêt avant ce rappel retourne zéro item répondu, pas un score de découverte. Les résultats historiques antérieurs ne sont pas recalculés.
## Observations de protocole — ADR-043 / ADR-044

Extensions optionnelles, compatibles avec les clients existants :

- `POST /api/entrainement/{theme}/sessions/{session_id}/reponses` : `observation_contextes` objet optionnel pour `rappel-source`, `{passe: "decouverte" | "rappel", ordre: entier 1..nombre_items, presentee_ms?: entier, exposition_ms?: entier, incident_photo?: bool}`. Les horodatages déclarés sont des millisecondes depuis l’époque, bornées à `0..10^14`. Ordre = position réelle de l’item livré. Le rappel documenté exige une réponse de découverte enregistrée. Justesse et première réponse sont calculées/conservées par le serveur.
- `POST …/fin` : corps facultatif `{observations_contextes: {decouverte?: [faits], rappel?: [faits]}}`. Chaque fait contient `item_id`, `passe`, `ordre`, et facultativement les horodatages précédents, `presentee`, `incident_photo`, `photo_apres_erreur`, `photo_revelee_ms`. Révélation autorisée uniquement après une erreur initiale de rappel. Les champs de réponse/justesse clients sont ignorés. IDs, ordre, types, doublons et taille sont contrôlés ; incohérence = 422 `reponse_invalide`. Réponse de clôture Contextes seule : champ additif `observations_contextes` contenant faits et `premiere_reponse` serveur `{reponse,correcte,aide,temps_ms,validee_ms}`. Les autres payloads de clôture restent inchangés.
- `POST …/observations` : `{item_id: str, reponse: dict}` pour `pqrst-mise-en-oeuvre` seulement. Le protocole `_pqrst` de l’ADR-043 est validé en mode partiel, enregistré localement sans notation, sans FSRS et sans runner ; réponse 200 `{enregistree: true}`. Métadonnées invalides = 422 ; séance/item inconnus = 404 ; séance clôturée = 409. Les observations complètes corrigées proviennent de `POST …/reponses` et sont conservées face aux checkpoints ultérieurs.

Le journal local est persisté à chaque réponse/checkpoint et relisible par le stockage après redémarrage. Il n’autorise ni reprise d’une séance active ni consultation par une nouvelle route GET. Les historiques antérieurs ne sont pas migrés.

Pour les nouveaux payloads PQRST `_pqrst`, la durée totale du protocole n’alimente pas `temps_reference`, et le résultat après modèle n’alimente pas `resume.sans_aide`. Les anciens payloads et historiques restent inchangés, ainsi que la première réponse par item et FSRS. Avant nettoyage de la séquence, le navigateur conserve un snapshot ; la clôture attend sa sauvegarde. Un échec réseau garde ce snapshot en mémoire pour le réessai de clôture.

## Pratiques guidées de mémoire immédiate — ADR-045

Périmètre local d’entraînement distinct du moteur adaptatif : `/api/memoires-immediates`. Aucun historique existant n’est modifié.

- `POST /sessions` : `{parcours: "code"|"chemin"|"changement"|"objets", parametres?: {...}, sans_limite_sessions?: false}` → 201 `{session_id, parcours, version, parametres, essai:{id,index,stimulus}}`.
- `POST /sessions/{uuid}/reponses` : `{essai_id,reponse,observations?:{},assistee?:false}` → `{correction,essai_suivant:null|essai,terminee}`. `terminee` indique la fin du bloc de quatre essais ; fermeture persistée uniquement par `/fin`. Réponse `null` = absence déclarée ; chaîne vide non validée rejetée. Retry identique idempotent ; tentative différente sur une première réponse verrouillée → 409.
- `POST /sessions/{uuid}/aide` : `{essai_id}` après première réponse → `{essai,assistee:true}`. Nouvelle réponse avec `assistee:true`, indépendante de la première et explicitement après correction.
- `POST /sessions/{uuid}/interruption` : `{essai_id,phase:"pret"|"exposition"|"masque"|"reponse",observations?:{}}` → `{essai}` de remplacement au même rang. Retry retourne le remplacement existant.
- `POST /sessions/{uuid}/fin` : fermeture idempotente → `{session_id,parcours,version,parametres,terminee,observations:[{essai_id,index,premiere,aide,interruption,remplace}]}`. Enregistrement première `{reponse,correction,observations,validee}` ou `null` ; aide séparée ; interruption sans score.

Paramètres : `longueur` 2–12 code, 2–9 chemin, 2–5 changement, 2–6 objets ; départ code 4, autres 3. `modalite` visuelle, auditive permise uniquement pour le code. `condition` forme/couleur/association fixe dans un bloc de changement. `signal_ms` 500–10000 (code 2000, chemin 1500), `intervalle_ms` 0–5000 (code 1000, chemin 500), `exposition_ms` 1000–30000 (changement 5000, objets 6000), `masque_ms` 0–10000 (changement 1500, objets 1000, code/chemin 0).

Stimulus : code `{chiffres:["0","4","7"]}` ; chemin `{positions:[{id,x,y}],trajet:[ids]}` ; changement `{avant:[{position,forme,couleur}],apres:[...],palette:{couleur:hex}}` ; objets `{positions:[{id,x,y}],objets:[{id,nom}],modele:{objet:position},reserve:[objets]}`. Modèles nécessaires à la présentation, retirés du DOM par le client après encodage.

Réponses : code texte préservant zéro initial (espaces/tirets tolérés), chemin liste de positions, changement `{decision:"identique"|"different",localisation:[positions],localisation_absente?:bool}`, objets mapping objet→position unique, partiel autorisé. Correction : suite entière/positions/contenu retrouvés ; détection/rejet correct/fausse alerte/changement manqué et localisation séparée ; associations exactes/erronées/non placées et permutation. Aucun résultat composite.

Observations facultatives : clés terminant en `_ms`, nombres finis 0–86400000 ; `modalite`, `voix`, `phase`, `raison`, textes de 120 caractères maximum ; `audio_indisponible`, `absence_declaree`, booléens. Données déclarées par le navigateur, pas de journal de frappe. Erreurs : 422 paramètres/réponse invalides, 404 UUID inconnu, 409 essai verrouillé/indisponible, 429 troisième bloc déjà ouvert sans dérogation. Aucun endpoint de bilan.

Une interruption peut inclure `assistee:true` (booléen strict) : une aide ouverte est marquée interrompue sans score, la première réponse reste intacte. Retour `{essai:prochain_essai_initial|null,assistee_interrompue:true}` ; aucun nouveau stimulus assisté, aucune revalidation de cette aide. Retry idempotent. Si aucun essai initial ne reste, fermer le bloc par `/fin`.

### Progression des mémoires immédiates — protocole v2

Création : `progression: bool` strict, défaut false pour compatibilité. True accepte seulement `modalite`/`condition` comme paramètres fournis ; réglages numériques libres : 422. Le serveur choisit les paramètres du palier et retourne `progression: {version,condition,palier,total,reussites}`. Paramètres effectifs supplémentaires : `repetitions` bool pour code, `plateau_etendu` bool pour chemin. Le journal conserve les paramètres et le palier de chaque bloc. La progression se reconstruit sur les blocs terminés, sans comptage double de /fin ou de retries. Les blocs incomplets/aidés/interrompus et anciens blocs sans progression ne font pas avancer. Deux blocs à ≥3/4 exacts font monter, deux à ≤1/4 font descendre ; sinon maintien. Modalités code et conditions changement séparées. Voir [paliers](../20-specs/paliers-memoires-immediates.md).


## Stratégies appliquées — pratique originale V3

Protocole `strategies-appliquees-v3`, douze scénarios versionnés par parcours. Les contenus et journaux V1/V2 restent résolus sans réinterprétation. Les journaux sont isolés dans `strategies`, sans écriture dans FSRS ni les anciens historiques ; décision [ADR-047](adr/ADR-047-strategies-appliquees.md).

`POST /api/strategies/sessions` : `parcours` plan/rappel/message/temps, `condition` avec-note/sans-note uniquement pour message (avec-note par défaut), `sans_limite_sessions` booléen strict facultatif. Réponse 201 : session_id/parcours/version/condition/scenario/phase/donnees, avec l’ID dans `scenario.id` ; 429 après trois ouvertures quotidiennes, tous parcours stratégies confondus, sans dérogation. La journée est déterminée par la date UTC de création.

Sous verrou, le serveur choisit la variante suivant la dernière ouverture persistée du même parcours, dans un cycle de douze. Rotation indépendante des résultats, partagée entre conditions de note et conservée au redémarrage. Une ouverture interrompue participe à la rotation ; un nouvel appel de création n’est pas un retry idempotent. Le journal archive `version` et `scenario_id` ; le contenu reste dans la banque versionnée. Les journaux V1 sans ID résolvent leur scénario original et conservent leur version et correction horaire historiques.

`POST /api/strategies/sessions/{id}/etapes` : etape_id UUID, action, donnees. Transitions et clés autorisées validées, premières réponses verrouillées. Retry exact renvoie réponse durable identique ; changement du payload sous même ID ou transition indisponible 409, champs non admis 422. Réponse : phase et données publiques, scénario mis à jour, résultat seulement après correction. Message supprimé après encodage ; restitution non renvoyée avant correction ; rappel masqué tant que non consulté.

Actions plan : plan_initial/reviser (ordre), executer (action_id), verifier/terminer. Rappel : configurer (piece_id/rappel), intercaler (action_id), consulter_rappel, joindre (piece_id), terminer. Message : masquer (note_presente seulement), restituer (quoi/quand/absence), agir (action_id/heure), consulter_note, reecouter. Temps : estimer (secondes), classer (document_id/categorie), comparer (duree_active_secondes/duree_ecoulee_secondes/pauses_secondes/attente_interface_secondes), marge (secondes). Pause/reprendre/incident/aide communs sans données supplémentaires. Les identifiants de pièces, actions intercalées, documents, catégories et choix sont ceux du scénario reçu.

`comparer` accepte `attente_interface_secondes` facultatif, égal à zéro par défaut. Les durées déclarées doivent être numériques, entre 0 et 86 400 s, avec actif + pauses + attente interface = écoulé à 0,1 s près. Un incident ou une capture incohérente laisse la comparaison absente ; l’écart disponible est actif moins estimation. Ces valeurs décrivent l’horloge locale déclarée par le client, pas une latence réseau ou une mesure clinique contrôlée.

`POST /api/strategies/sessions/{id}/fin` : clôture idempotente ; session_id/parcours/version/scenario_id/condition, statut termine ou interrompu, observations/aides/pauses, correction seulement si le parcours a atteint la phase correction. Notes personnelles jamais acceptées. Voir [version servie](../20-specs/strategies-appliquees.md) pour phases, interprétation et limites.

## N-back visuel — observation distincte

`POST /api/nback/sessions` : `{n?: entier strict1..3, sans_limite_sessions?: bool strict}`, crée un bloc V2, défautn1, condition `observation-sans-feedback`, n+15présentations,15décisions/cinqcorrespondances. Quota trois ouvertures par jour UTC, dérogation explicite. Réponse 201 : `session_id/version/condition/n/total/position/phase/terminee`. Aucun historique, attendu ou séquence avant fin. `symbole` présent uniquement aux phases `initialisation` et `decision`.

`POST /api/nback/sessions/{id}/etapes` : UUID `etape_id`, `action`, `donnees`. Actions `commencer` (ready→initialisation, n premières positions sans réponse), `suivant` (initialisation→decision ou neutre→position suivante/résultat), `repondre` avec decision identique/different/absence (decision→neutre), `interrompre` avec raison pause/masquage/fatigue/sortie (clôture partielle). Une durée d’exposition locale facultative peut être déclarée : numérique finie 0–86400s, sans interprétation de temps de réaction ; l’interface V1 n’envoie pas de mesure. Champs inattendus 422, transitions impossibles 409. Rejeu exact d’un UUID renvoie l’accusé durable ; contenu différent sous même UUID 409.

Dernier `suivant` et interruption clôturent atomiquement. `POST /api/nback/sessions/{id}/fin` clôture idempotente avec motif sortie si encore actif ; renvoie le payload public terminal. Résultat : compte des décisions validées, cibles/non-cibles observées et absences par catégorie, détections/manqués/rejets/fausses alertes, premières décisions avec attendu recalculé, seules présentations déjà atteintes, rythme auto-rythmé et statut. Données propres à cette tâche, jamais injectées dans l’ancien exercice ou FSRS. Voir [spécification](../20-specs/nback.md) et ADR-048.

V2 : référence de correction exactement n places avant ; anti-doublon canonique sous verrou pourmême n/condition, archivesV1 incluses. Après1000collisions,503 sansjournal supplémentaire. RésultatV2 trace les lags proches horsn, leurres pournon-cibles et coïncidencesauxiliaires pourcibles ; les champsV1 restent conservés.

### Dosage des contextes illustrés — enrichissement du 10 octobre

Le parcours evocation/memoire-source expose une banque de vingt scènes versionnées, avec quota effectif maximal de dix items par séance (palier local 1). Le contrat de découverte `memorisation` et rappel final reste inchangé ; seul le rappel final alimente FSRS/maîtrise. Ajouter du contenu ne double pas le nombre de scènes d’une série. Voir ADR-049.

### Extension ADR-052 — nouveaux exercices

Thèmes `debut-commun` (type `rappel-indice`) et `logigrammes` (type `logigramme`). Les contraintes publiques logigrammes référencent des catégories et valeurs : `contenu.categories=[{id,label,valeurs}]`, `contenu.contraintes=[{type,gauche:{categorie,valeur},droite:{categorie,valeur},texte}]`. La réponse est un objet `{horaire:{categorie:valeur}}` ou sa sérialisation JSON. La première erreur permet un second essai avec `attendue:null`. La solution et la preuve déductive restent privées jusqu’au feedback. Les mots complets et définitions de contrôle du début commun ne sont jamais sérialisés dans le stimulus public.
