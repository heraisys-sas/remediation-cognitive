# Nuit Déduction 2026-09-28 — brief chef d'orchestre

## Cadre commun (toutes voies)

- Dépôt : `/Users/olivierhz/.openclaw-autoclaw/agents/auto-designer/workspace/remediation-cognitive`
- Branche : `amelioration-deduction-20260927` (HEAD `377479e`). **Aucune fusion vers main.**
- **Seul l'intégrateur (coordinateur) pousse** ; les sous-agents ne font jamais `git push`.
- Copie interdite : `/Users/olivierhz/orthogone/remediation-cognitive` — ne jamais y toucher.
- **Préserver la modification locale non commitée de `tools/generer_deduction.py`** (elle étend le palier 3 avec 4 négations relatives ; en juger la pertinence, ne pas l'écraser).
- Ne pas redémarrer le serveur utilisateur.
- Règle produit (ADR-007) : une seule règle énoncée (chaque figure colorée posée une fois, une pièce par case) ; les phrases portent toute la résolution ; pas de règle Sudoku/latine cachée ; pas de placement direct ; solution unique ; résolution sans devinette ; aides progressives ; nouveaux IDs si contenu remplacé, historique conservé.
- **Interdit** : assimiler le nombre de tours du solveur à une difficulté clinique. La difficulté se mesure par : phrases nécessaires au premier placement, profondeur des chaînes de dépendances, redondances internes et entre phrases.
- Modèle : GLM-5.3-Flash partout (coordinateur et sous-agents). Aucun substitut.

## Jalons horaires (Europe/Paris)

| Heure | Événement |
|---|---|
| 17:20 | Lancement voie 1 (diagnostic) + voie 2 (correction) |
| 19:30 | Rapport diagnostic + sources livré (voie 1) |
| 22:00 | Défauts A + B corrigés et testés (voie 2, commit) |
| 23:30 | Défaut C corrigé et testé (voie 2, commit) |
| 00:15 | Échantillon 3 grilles/palier validé (tous contrôles verts) |
| 00:30 | Contenu complet régénéré + suite complète de tests verte, commits |
| 00:45 | Lancement revue indépendante (voie 3) |
| 02:15 | Rapport de revue livré ; correctifs éventuels jusqu'à 02:45 |
| 02:45 | **Gel des écritures** (tout est committé) |
| 02:50 | Intégrateur : push + checkpoint + rapport final sauvegardé |
| 02:50–03:00 | Revue de contrôle **lecture seule** (aucune écriture) |

En cas de retard sur un jalon : livrer l'état courant, documenter ce qui manque, ne jamais pousser le dépassement de l'échéance de 02:50.

## Voie 1 — Diagnostic & sources (17:20 → 19:30)

Livre : `.cluster/nuit-deduction-20260928/01_diagnostic.md` (factuel, court). Lecture seule sur le dépôt hormis ce rapport.

1. **Reproduction bornée du blocage de génération** (échec de la nuit du 27 : grammaires « négatif pur » palier 2 et « relatif pur » palier 3 bloquées 20–30 min sans résultat). Lancer `python3 tools/generer_deduction.py --dry-run --par-palier N` (N=2 puis 3) avec un budget de temps (couper à ~3 min par essai) ; caractériser le blocage (vivier vide ? solveur jamais complet ? boucle d'essais ?) avec quelques mesures.
2. **Verdict sur la modification locale** (`git diff tools/generer_deduction.py`, palier 3 + négations relatives) : garder / ajuster / annuler, avec justification (risque de reproduire une grammaire « pure » contre bénéfice de mixage).
3. **Recommandations de grammaire et de sélection par palier (1→4)** pour garantir : recoupements entre phrases ; aux paliers avancés, aucune phrase seule ne fixe de position et la première certitude exige au moins deux phrases ; pas de placement direct ; **génération faisable en temps borné** (bornes d'essais et de temps proposées).
4. **Sources réellement vérifiées** (page lue = source retenue ; sinon « non vérifiée ») :
   - https://www.orthoedition.com/materiels-ouvrages/elementaire-mon-cher-650 — ce que c'est, auteur, progression réelle ; **inspiration seulement, aucune copie de fiches**.
   - https://pubmed.ncbi.nlm.nih.gov/36594859/ — titre exact, population, résultats, limites.
   - Vérifier les ancres déjà listées dans `.cluster/nuit-deduction-20260927/sousagent_01_audit.md` (Middleton & Schwartz 2012 ; Chui et al. 2025 ; études APT ; Cochrane 2013) et ajouter les sources primaires des méthodes nommées sans citation : Levine (GMT), Wilson (PQRST), Meichenbaum (auto-instruction), Fasotti (TPM), Gollwitzer (intentions d'implémentation), Leonard/Wambaugh (SFA/PCA). Pour chaque source : population réelle de la preuve + ce qu'elle soutient et ne soutient pas. ~12 recherches web maximum.

## Voie 2 — Conception & correction (17:20 → 00:30, commits progressifs, jamais de push)

Ordre impératif : A → B → C → outil de mesure → échantillon → contenu complet → tests complets.

### Défaut A — `tools/deduction_commun.py`, `_vrai_binaire` (~ligne 157)

Les relations `pas-voisin-dessus` / `pas-voisin-dessous` sont **inversées** : chacune nie l'autre au lieu de nier sa positive. Reproduction : n=3, sujet case0, cible case3 → `voisin-dessus` True ET `pas-voisin-dessus` True simultanément.

- Correctif : `pas-voisin-dessus` = `not (i2 == i1 + n)` ; `pas-voisin-dessous` = `not (i2 == i1 - n)`.
- **Test obligatoire** : pour n=3 ET n=4, pour **toutes** les paires de cases distinctes, chaque négation doit être le complément exact de sa positive. Test écrit **indépendamment des libellés français** (paire positive↔négative déclarée par un appariement explicite des types, pas par lecture du nom). Inclure le cas de reproduction ci-dessus.

### Défaut B — `frontend/src/app.js`, `relationAtome` (~ligne 1793)

Les nouveaux types négatifs ne sont pas rendus (retour chaîne vide par défaut) : `pas-voisin-gauche`, `pas-voisin-droite`, `pas-voisin-dessus`, `pas-voisin-dessous`, `pas-a-droite-de`, `pas-a-gauche-de`, `pas-au-dessus-de`, `pas-en-dessous-de`.

- Couvrir **tous** ces types dans le rendu, formulations françaises correctes (« … n'est pas juste au-dessus du carré bleu », « … n'est pas plus à droite que le triangle vert »).
- **Validation sémantique indépendante + test du vrai rendu JS** (pas seulement l'existence des branches) : étendre `tools/verifier_phrases.js` — il exécute le vrai code de l'interface — avec (a) des phrases dorées exactes pour les 8 types, (b) un contrôle de sens par type sur tout le contenu (le libellé rendu doit dire ce que le type annonce, aucun « undefined », aucune phrase vide).

### Défaut C — `tools/generer_deduction.py`, `_selection` (~ligne 324)

La sélection gloutonne choisit les phrases les plus contraignantes **sans garantir le recoupement entre phrases**.

- Critères mesurés et bloquants à la génération, **aux paliers avancés (2, 3, 4)** ; décision documentée si un autre périmètre est retenu (avis de la voie 1 bienvenu) :
  1. pour **chaque phrase prise seule**, la propagation ne détermine **aucune** position (aucun domaine réduit à un singleton) ;
  2. la première certitude (premier domaine singleton en alimentant le solveur phrase par phrase, dans l'ordre présenté) exige **au moins deux phrases**.
- Ajouter le même contrôle côté dépôt (`tools/validate_items.py`, type `grille-deduction`) pour que le validateur refuse un contenu non conforme.
- Renforcer la sélection pour favoriser le recoupement (au minimum : filtres ci-dessus ; si le temps le permet, préférence pour les phrases qui se renforcent mutuellement dans le graphe de contraintes).
- **Ne jamais** utiliser le nombre de tours du solveur comme mesure de difficulté.

### Outil de mesure avant/après (`tools/mesurer_difficulte.py`)

Pour **toutes les grilles** (les 80 stockées avant régénération, puis le stock final) : nombre de phrases ; phrases nécessaires au premier placement (k) ; nombre de phrases qui, seules, fixent une position (attendu 0 aux paliers 2–4) ; phrases retirables sans perdre la déductibilité (redondance entre phrases, attendu 0) ; informations retirables dans une phrase sans perdre la déductibilité (redondance interne, mesurée). Sortie : tableau markdown + CSV dans `.cluster/nuit-deduction-20260928/`. Copier l'état « avant » dans `.cluster/nuit-deduction-20260928/contenu_avant/` **avant** toute régénération.

### Génération de contenu

1. **Échantillon d'abord** : 3 grilles par palier, tous contrôles verts, avant d'envisager le stock complet. Bornes strictes : si un palier ne converge pas (par exemple 10 min ou budget d'essais épuisé), **stop**, diagnostic bref, ajustement de grammaire (jamais de retour au placement direct), nouvel essai borné. Ne jamais laisser une génération tourner sans surveillance.
2. Stock complet : 20 grilles/palier. En cas d'échec borné sur un palier : conserver l'ancien stock de CE palier s'il passe tous les contrôles (y compris les nouveaux critères C), et le documenter (régénéré / conservé, palier par palier).
3. **Nouveaux IDs** pour tout contenu remplacé (jamais resservir un contenu remplacé), `date_creation` à jour, changement de contenu annoncé dans le message de commit (règle du contenu versionné). Graine déterministe mise à jour (20260928). README et descriptions de paliers harmonisés si la grammaire change.
4. Un générateur qui traîne = échec : toute génération passe par des budgets internes (temps et essais) et échoue proprement avec un message clair.

### Tests obligatoires (fin de voie, tous verts avant 00:30)

`python3 -m pytest -q` (complet) · `python3 tools/validate_items.py` · `python3 tools/verifier_reponses.py` · `python3 tools/verifier_interface.py` · `node tools/verifier_phrases.js` · `node --check frontend/src/app.js`. Vérification UI ciblée : au choix, court test de rendu via le harnais existant ou instance de serveur jetable sur un port libre (curl, arrêt immédiat — jamais le serveur utilisateur).

### Discipline de dépôt

- Commits incrémentaux français (marqués `[nuit-deduction]`), un par jalon (A+B, C, mesures, échantillon, contenu, tests).
- `git add` ciblé (jamais `git add -A` aveugle). Aucun `git push`. Aucune fusion vers main. Ne jamais toucher à `/Users/olivierhz/orthogone/remediation-cognitive`.

## Voie 3 — Revue indépendante (00:45 → 02:15)

Livre : `.cluster/nuit-deduction-20260928/03_revue_independante.md`. **Lecture seule** (aucune modification du dépôt hormis ce rapport), indépendante du générateur : ne pas se fier au code pour juger le sens.

1. **Vérification explicite des trois défauts** : A (complémentarité positivé/négativé sur toutes les paires, reproduction indépendante du libellé) ; B (rendu JS réel : phrases complètes et correctes pour tous les nouveaux types, contrôle de sens) ; C (critères mesurés effectifs sur **toutes** les grilles et leurs chaînes de dépendances ; premier placement exigeant plusieurs phrases aux paliers avancés ; aucun usage des tours solveur comme difficulté).
2. **Sens des phrases en français** : échantillon large des grilles livrées ; chaque type de relation doit s'écrire conformément à ce qu'il annonce ; repérer toute inversion, troncature, redondance d'information.
3. **Logique** : solution unique, déductibilité rejouée, aucune règle cachée (Sudoku/latine), pas de retour au placement direct, aides progressives (secours) intactes, ordre des phrases sans régularité révélatrice.
4. **Qualité de langue** : accords, articles, phrases complètes, longueur variable, absence d'informations inutiles.
5. Classement des constats : **bloquant** / mineur, avec localisation précise.

## Intégration (coordinateur, 02:15 → 03:00)

1. 02:15–02:45 : transmission des constats bloquants à la voie 2 pour correction (une seule écriture à la fois) ; sinon consolidation.
2. 02:45 : gel — tout est committé localement.
3. 02:50 : push de la branche + checkpoint + `.cluster/nuit-deduction-20260928/02_rapport_final.md` sauvegardé (livré vs incomplet ; branche et commits ; mesures avant/après ; sources ; tests réellement passés ; limites).
4. 02:50–03:00 : revue de contrôle **lecture seule** (relance des validateurs, aucun fichier modifié) ; si un bloquant apparaît : constat consigné, la livraison déclare l'incomplétude avec checkpoint (l'état poussé fait foi).
