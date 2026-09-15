# Spécification — Thèmes « memoire » et « concentration » (sprint 2)

Contrat de formes EXACT des items. Tous les items respectent `content/schema-item.json`
(module « entrainement », meta avec auteur/date_creation/relecture_ortho {statut: "a_revoir"}).
Génération déterministe : `random.Random(20260904)` — deux exécutions produisent des
fichiers identiques. Identifiants uniques sur tout content/.

Conventions d'identifiants : `me-<palier>-<famille>-<nn>` et `co-<palier>-<famille>-<nn>`
(famille ∈ empan, paires, nback, chaine, cascade, double, serie ; nn = 01, 02, …).
prerequis d'un palier N : `["<prefixe>-palier-<N-1>"]` (prefixe = me / co) — palier 1 : `[]`.
Meta.auteur : "generation-automatique (tools/generer_memo_concentration.py)".
date_creation : "2026-09-10".

## Structure commune des items à affichage temporisé

`contenu` = {
  "consigne": str,        # affichée AVANT le stimulus (prépare l'attention)
  "affichage": {...},     # voir modes ci-dessous
  "enonce": str,          # la QUESTION, affichée APRÈS la lecture temporisée
  "aide": null
}

Modes d'affichage :
- {"mode": "sequence", "duree_par_item_ms": int, "elements": [str, …]}
  → éléments montrés UN PAR UN (élément affiché duree_par_item_ms, puis 250 ms de
  blanc, puis suivant).
- {"mode": "liste", "duree_totale_ms": int, "elements": [[str, str], …]}
  → toutes les lignes affichées ensemble pendant duree_totale_ms.

## THÈME « memoire » — 8 paliers × 18 items (prefixe me)

Paliers (contenu exact) :
- P1 : 18 × empan-chiffres ENDROIT, longueur 3.
- P2 : 18 × empan ENDROIT, longueur 4.
- P3 : 10 × empan ENDROIT 5 + 8 × paires-associatives 2 paires.
- P4 : 9 × empan ENVERS 3 + 9 × empan ENDROIT 6.
- P5 : 10 × empan ENVERS 4 + 8 × n-back pas 2.
- P6 : 9 × empan ENVERS 5 + 9 × paires 3 paires.
- P7 : 8 × empan ENVERS 6 + 10 × n-back pas 3.
- P8 : 8 × paires 4 paires + 10 × n-back pas 4.

### empan (type "empan", fonctions_ciblees ["memoire-travail"])
- affichage sequence, duree_par_item_ms 800, elements = chiffres "0".."9" en chaînes,
  sans deux chiffres identiques consécutifs.
- ENDROIT : enonce "Tape la séquence de mémoire, dans l'ordre." ; reponse.valeur =
  chiffres concaténés dans l'ordre (str).
- ENVERS : enonce "Tape la séquence à l'envers (de mémoire)." ; reponse.valeur =
  chiffres concaténés INVERSÉS (str).
- Ex. P1 : contenu {"consigne": "Mémorise la séquence de chiffres.",
  "affichage": {"mode": "sequence", "duree_par_item_ms": 800, "elements": ["5","8","2"]},
  "enonce": "Tape la séquence de mémoire, dans l'ordre.", "aide": null},
  reponse {"valeur": "582"}.

### n-back (type "n-back", fonctions_ciblees ["memoire-travail", "attention-soutenue"])
- Sequence de lettres majuscules sans doublon adjacent, tirées de B K L M N P R T ;
  longueur = pas + 4 ; duree_par_item_ms 1200.
- consigne "Mémorise la séquence d'éléments." ;
  enonce = "Quel élément était {pas} positions avant la fin ? Tape-le."
  (pour pas=2, « 2 positions avant la fin » ; formulation générique f-string).
- reponse.valeur = élément à l'index (longueur - 1 - pas) (str, majuscule).
- cap_complexite : null (paliers 5, 7) — "séquences de 8 éléments maximum" au palier 8.

### paires-associatives (type "paires-associatives",
fonctions_ciblees ["memoire-travail", "memorisation-longue"])
- Mots tirés SANS répétition dans l'item du pool : LUNE, PONT, ARBRE, ROUE, FLEUR,
  TRAIN, PORTE, NUAGE, PIERRE, LIVRE, PLUIE, TABLE ; nombres entiers distincts 10..99.
- affichage liste, duree_totale_ms = nb_paires × 4000, elements = [["LUNE","47"], …].
- consigne "Mémorise chaque paire mot–nombre." ;
  enonce = "Nombre associé à « {mot_sonde} » ?" (mot au hasard parmi les paires) ;
  reponse.valeur = str(nombre) de la paire sondée.

Manifest `content/entrainement/memoire/paliers.json` :
{"theme": "memoire", "paliers": [{"id": "me-palier-1", "description": "Empan 3 chiffres, endroit",
"prerequis": [], "fichier": "paliers/palier-01.json", "nb_items": 18}, …]}
— PAS de champ "table" (réservé au calcul-mental). Descriptions suggérées :
P1 "Empan 3 chiffres, endroit" ; P2 "Empan 4 chiffres, endroit" ;
P3 "Empan 5 + premières paires mot–nombre" ; P4 "Empan envers 3, endroit 6" ;
P5 "Envers 4 + sonde n-back (pas 2)" ; P6 "Envers 5 + paires 3" ;
P7 "Envers 6 + sonde n-back (pas 3)" ; P8 "Paires 4 + sonde n-back (pas 4)".

## THÈME « concentration » — 9 paliers × 18 items (prefixe co)

- P1 : 18 × chaine-calcul 3 opérations, termes 2..20.
- P2 : 18 × chaine-calcul 4 opérations, termes 2..20.
- P3 : 18 × cascade de soustractions (type chaine-calcul) : départ 60..99, pas 3..9,
  5 soustractions, résultat final ≥ 0 garanti.
- P4 : 18 × double-tache filtrage 5 éléments, question « somme des chiffres ».
- P5 : 12 × chaine 5 opérations termes 2..30 + 6 × serie-manquante arithmétique.
- P6 : 18 × double-tache 7 éléments, questions mixtes (somme / compte de lettres).
- P7 : 12 × chaine 6 opérations termes 2..40 + 6 × serie-manquante géométrique.
- P8 : 12 × chaine 7 opérations termes 2..50 + 6 × double-tache 9 éléments.
- P9 : 9 × chaine 7 opérations termes 2..60 (cap_complexite "7 opérations maximum")
  + 9 × serie-manquante alternée.

### chaine-calcul (fonctions_ciblees ["attention-soutenue", "memoire-travail"] ;
cascade → ["attention-soutenue", "automatisation"])
- Expression arithmétique à N opérations, additions et soustractions uniquement —
  évaluée de gauche à droite (addition/soustraction : associativité gauche standard,
  donc l'écriture plate est non ambiguë). Résultat intermédiaire toujours ≥ 0 et ≤ 300.
- contenu {"enonce": "7 + 5 − 3 + 9", "aide": "Calcule de gauche à droite, étape par
  étape."} ; reponse {"valeur": 18} (int).
- cascade : enonce "78 − 7 − 7 − 7 − 7 − 7" ; reponse = départ − pas×5 (int ≥ 0).

### double-tache (type "double-tache",
fonctions_ciblees ["attention-divisee", "attention-selective"])
- Séquence mêlant lettres (A C E F G H J K L N R S T) et chiffres (1..9, zéro exclu),
  alternées sans deux chiffres consécutifs ; duree_par_item_ms 1000.
- Variante "somme" : ≥ 2 chiffres dans la séquence ; consigne "Tu verras une suite
  mêlant lettres et chiffres : prépare-toi à additionner les chiffres." ;
  enonce "Quelle était la somme des chiffres ?" ; reponse.valeur = somme (int).
- Variante "compte" : consigne "… prépare-toi à compter les lettres." ;
  enonce "Combien de lettres y avait-il ?" ; reponse.valeur = nombre de lettres (int).

### serie-manquante (fonctions_ciblees ["memoire-travail", "vitesse-traitement"])
- arithmétique (P5) : pas 2..9, 5 termes, départ 2..30, un terme manquant en position
  2 ou 3 (0-based 1..2) → enonce "3, 5, __, 9, 11" ; reponse = terme manquant (int).
- géométrique (P7) : ratio 2 ou 3, départ 1..6, 5 termes, manquant en position 2 ou 3.
- alternée (P9) : pas a puis b (a ≠ b, 1..5) alternés, départ 2..15, 6 termes,
  manquant en position 4 ou 5 (0-based 3..4).

Manifest `content/entrainement/concentration/paliers.json` : même structure,
prefixe co-palier-N. Descriptions : P1 "Chaîne de 3 opérations" ; P2 "Chaîne de 4
opérations" ; P3 "Cascade de soustractions" ; P4 "Double tâche : somme des chiffres" ;
P5 "Chaîne de 5 + premières séries" ; P6 "Double tâche 7 éléments" ;
P7 "Chaîne de 6 + séries géométriques" ; P8 "Chaîne de 7 + double tâche 9" ;
P9 "Chaînes longues et séries alternées".

## Backend

- `contenu.py` : _SOURCES_PAR_THEME += {"memoire": ("memoire/paliers", "palier-*.json"),
  "concentration": ("concentration/paliers", "palier-*.json")} (ordre : après python).
- `messages.py` : themes += "memoire": {"nom": "Mémoire", "description": "Empans de
  chiffres, séquences et associations — mémorisation progressive"} ;
  "concentration": {"nom": "Concentration", "description": "Calculs chaînés, double
  tâche et séries — une attention qui tient"}.
- `correction.py` : brancher "memoire" → comparaison de texte où l'on SUPPRIME tous
  les espaces (pas seulement les réduire) + casse ignorée ; "concentration" →
  comparaison numérique (réutiliser _corriger_numerique). calcul-mental/anglais/
  python inchangés.
- Tests : THEMES_ATTENDUS = 5 ; grading (memoire tolère espaces/casse ; concentration
  numérique) ; GET /themes expose les 5 ; cycle E2E mémoire (démarrer → répondre avec
  les valeurs attendues → résumé cohérent) ; payload de démarrage sans clé
  reponse/valeur sur TOUS les thèmes (l'affichage du stimulus est dans contenu,
  assumé et documenté au contrat).

## Frontend

- `index.html` : après l'article .carte-enonce, ajouter
  `<div id="zone-memo" class="zone-memo" hidden></div>`.
- `app.js` :
  - refs.zoneMemo = $("zone-memo") ;
  - montrerItem() : si contenu.affichage → PHASE MÉMO : enonce = contenu.consigne,
    formulaire caché, zoneMemo visible avec un bouton « Afficher » (et la mention
    courte de durée, ex. « 3 éléments · environ 3 s ») ; sinon chemin actuel direct.
  - Clic « Afficher » → lecture temporisée : mode sequence = un élément à la fois
    (duree_par_item_ms, puis 250 ms de blanc), indicateur discret « 2 / 5 » ;
    mode liste = toutes les lignes pendant duree_totale_ms ; bouton « Passer »
    disponible pendant la lecture.
  - Fin de lecture (ou « Passer ») → PHASE QUESTION : zoneMemo caché (le stimulus
    DISPARAÎT avant la saisie), enonce = contenu.enonce, formulaire visible, focus,
    etat.debutQuestion = Date.now() (le temps de mémorisation ne compte PAS dans
    temps_ms).
  - Toutes les minuteries stockées dans etat et annulées par annulerMemo(), appelé
    au début de montrerItem, dans revenirAuxThemes et dans finirSeance (aucune
    fuite de timer si l'utilisateur termine en plein affichage).
  - normaliserReponse : coercition numérique aussi pour theme.id === "concentration".
  - inputmode "numeric" pour les types production, chaine-calcul, serie-manquante,
    double-tache, empan, paires-associatives ; "text" sinon (n-back).
- `styles.css` (ajout, oklch sombre cohérent, AUCUNE animation) :
  .zone-memo (carte), .memo-entete, .memo-plateau (grand bloc centré), .memo-element
  (très grand, ex. clamp(3rem, 10vw, 5rem)), .memo-liste (lignes mot–nombre), 
  .memo-points (indicateur discret « 2 / 5 »), .memo-actions (boutons Afficher/Passer).

## Contrat (docs/30-technique/api-contract.md) — mises à jour
- GET /themes : 5 thèmes.
- Nouvelle section « Types d'exercices » : familles + affichage temporisé (consigne →
  stimulus → question) + note d'honnêteté : le stimulus des items temporisés voyage
  dans le payload client (usage familial mono-utilisateur assumé ; un mode
  serveur-poussé pourra venir plus tard).
- Règle 8 (durée max) déjà présente.
