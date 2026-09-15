# Plan — Enrichissement des exercices : mémorisation & concentration (sprint 2)

## Demande
Les exercices doivent être plus centrés sur l'entraînement à la mémorisation et à la
concentration (ex. additions/soustractions chaînées bout à bout qui conduisent
progressivement à la fatigue), en s'appuyant sur les techniques d'entraînement
cérébral reconnues pour enrichir et complexifier — pas seulement sur le calcul simple.

## Réponse produit : 2 nouveaux thèmes, 6 nouvelles familles

Techniques mobilisées (fondements reconnus, implémentation originale — aucun test
clinique protégé copié) :

| Famille | Type d'item | Thème | Fonctions | Ancrage |
|---|---|---|---|---|
| Calcul chaîné (total courant) | `chaine-calcul` | concentration | attention soutenue + MDT | calcul continu avec accumulation (famille des tâches de calcul sériel — PASAT/logique assimilée, protocole NON copié : visuel, rythme libre, opérations variables) |
| Cascade de soustractions | `chaine-calcul` (variante) | concentration | attention soutenue + automatisation | soustraction sérielle à pas fixe (départ et pas variables) |
| Empan de chiffres (endroit/envers) | `empan` | mémoire | mémoire de travail | empan numérique classique, envers = manipulation |
| Sonde n-back (rappel temporel) | `n-back` | mémoire | mémoire de travail + attention soutenue | variante rappel du n-back (sonde, pas 2→4) |
| Double tâche de filtrage | `double-tache` | concentration | attention divisée + sélective | filtrage chiffres/lettres (logique d2-assimilée, original) |
| Séries à règle (nombre manquant) | `serie-manquante` | concentration | MDT + vitesse | suites arithmétiques/géométriques/alternées |
| Paires associatives mot–nombre | `paires-associatives` | mémoire | MDT + mémorisation longue | apprentissage par paires |

La fatigue progressive est **conçue dans le contenu** : la longueur des chaînes
(3 → 7 opérations) et la taille des empans (3 → 6 chiffres) croissent par palier —
la détection de fatigue existante (RT, erreurs) fait le reste.

## Contenu à générer (déterministe, graine fixe)
- Thème `memoire` : 8 paliers × 18 items = 144 (détail par palier dans spec.md)
- Thème `concentration` : 9 paliers × 18 items = 162 (détail dans spec.md)
- Total nouveau : 306 items ; format strictement conforme à `content/schema-item.json`
  (types ajoutés au schéma le 2026-09-10 : chaine-calcul, serie-manquante,
  paires-associatives).

## Lots

### Lot 1 [A] — Générateur + contenu + validateur (agent : contenu-memo-concentration)
- `tools/generer_memo_concentration.py` (stdlib, graine fixe 20260904) ;
  `content/entrainement/memoire/paliers/palier-01..08.json` + `paliers.json` ;
  `content/entrainement/concentration/paliers/palier-01..09.json` + `paliers.json` ;
  README des deux dossiers.
- `tools/validate_items.py` : manifests multi-thèmes (champ `table` exigé seulement
  pour calcul-mental ; `description` pour les autres), cohérence cm-* seulement pour
  calcul-mental, motif des refs de palier généralisé `^[a-z]+-palier-\d+$`.
- Revue : validateur 0 erreur sur ~500 items ; déterminisme (2 exécutions identiques).

### Lot 2 [B] — Backend (agent : backend-memo-concentration)
- `contenu.py` : thèmes `memoire` + `concentration` dans le registre.
- `messages.py` : libellés des 2 thèmes (vocabulaire neutre).
- `correction.py` : `memoire` → texte (suppression de TOUS les espaces + casse
  ignorée) ; `concentration` → numérique (existant réutilisé).
- Tests : THEMES_ATTENDUS = 5 thèmes ; grading memoire/concentration ; cycle E2E
  séance mémoire ; payload sans clé reponse/valeur (l'affichage temporisé du
  stimulus est assumé et documenté au contrat).
- Revue : pytest complet vert.

### Lot 3 [C] — Interface (agent : interface-memo-concentration)
- `index.html` : zone de mémorisation `#zone-memo` insérée après la carte énoncé.
- `app.js` : phase de mémorisation (consigne → bouton « Afficher » → lecture
  temporisée séquence/liste → question + saisie), bouton « Passer », annulation
  des minuteries (nouvel item, retour thèmes, fin de séance), `normaliserReponse`
  numérique aussi pour `concentration`, inputmode par type d'item.
- `styles.css` : styles zone-memo (oklch, zéro animation, contraste AA).
- Contrainte clinique : **le stimulus disparaît avant la phase de saisie**.
- Revue : jsdom checks + relecture des minuteries (pas de fuite de timer).

### Lot 4 [R1] — Revue exécution (agent : revue-execution-2)
E2E réel sur les 5 thèmes (y compris memoire et concentration), garde-fous,
pytest complet, risques code.

### Lot 5 [R2] — Revue conformité & ergonomie (agent : revue-conformite-2)
Garde-fous cliniques + ergonomie spécifique mémorisation (stimulus masqué à la
saisie, durées d'affichage raisonnables, vocabulaire neutre, pas de norme).

## Graphe
1 → 2, 3 → 4, 5 → intégration → livraison (rapport + push GitHub).

## cluster_bypass_reason (2026-09-10)
Impossible de déléguer aux sous-agents : le fournisseur de modèle renvoie
HTTP 403 sur les sessions d'agents (3 échecs sur 4 tentatives de dispatch,
0 token consommé : contenu-memo-concentration, interface-memo-concentration,
contenu relance ; seule l'interface relance reste sans verdict). Exécution
directe par l'orchestrateur, revue finale incluse, pour ne pas bloquer la
livraison — les rapports de revue resteront la contrepartie de traçabilité.

## Hypothèses (énoncées à la livraison)
- Le stimulus des items à affichage temporisé voyage dans le payload client
  (honnêteté assumée en usage familial mono-utilisateur ; note au contrat).
- Les durées d'affichage (800–1200 ms/élément, 4 s/paire) sont des défauts
  paramétrables, pas des constantes cliniques.
- Zéro copie de matériel protégé : PASAT/d2/MMSE ne sont pas reproduits
  (visuel, rythme libre, opérations et pas variables).
