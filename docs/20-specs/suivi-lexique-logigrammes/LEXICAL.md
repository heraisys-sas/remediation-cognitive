# Début commun — checkpoint lexical

Contrat proposé (22 octobre 2026) : thème `debut-commun`, type existant `rappel-indice`, ids `dc-1-01`… ; trois fichiers `content/entrainement/debut-commun/paliers/palier-01.json`… (12 items chacun). `reponse.valeur` = segment écrit, `reponse.variantes` = liste explicite (vide autorisée). `contenu.debut_commun` = `{terminaisons: [str,str], mots: [str,str], genres: ["m"|"f",...], definitions: [str,str]}` ; chaque mot est exactement segment + terminaison. `enonce` fournit les deux fins et définitions ; pas de dépendance à un rendu nouveau. `indices` : deux sémantiques, puis première lettre. Correction proposée : `backend.app.domain.debut_commun.est_correct(item, saisie)` égalité NFC/casefold/trim uniquement ; accents distinctifs conservés, pas de similarité sémantique. Les variantes éventuelles doivent reconstruire deux mots explicitement documentés (aucune actuellement).

Progression : 1 objets concrets et longueur donnée ; 2 noms quotidiens variés, recherche sans longueur ; 3 notions et double contrainte contextuelle, sans mots artificiellement rares. POC complémentaire au travail après TBI ; aucune validation de thérapie spécifique ni transfert général promis. Relecture professionnelle non effectuée.

État : contrat établi avant code. Générateur, corpus, correcteur et tests à créer. Aucun fichier partagé modifié.

Reprise : « Lire LEXICAL.md ; générer et tester Début commun, puis intégrer le contrat sans modifier Calcul mental/Déduction. »
Commandes prévues : `python3 tools/generer_debut_commun.py` ; `python3 -m pytest -q backend/tests/test_debut_commun.py`.

## Implémentation achevée

- `tools/generer_debut_commun.py` créé : corpus original déterministe 36 paires, 3 × 12, aides sémantiques contextualisées puis lettre ; aucun autre contenu régénéré.
- `content/entrainement/debut-commun/paliers/palier-01.json`, `palier-02.json`, `palier-03.json` créés et conformes à la sortie du générateur.
- `backend/app/domain/debut_commun.py` créé : `est_correct(item, saisie)`, NFC/casse/espaces périphériques, accents conservés, aucune comparaison sémantique.
- `backend/tests/test_debut_commun.py` créé : 3 tests passent (reconstruction, orthographe stricte/alternatives, stabilité JSON), 22 octobre 2026. Deux avertissements existants FastAPI/httpx/anyio.
- Ce checkpoint mis à jour ; aucun commit effectué.

Révision du contrat après revue parent : l’énoncé expose seulement les fins et genres (longueur au palier 1). Les définitions ne sont accessibles que via aides. Les champs `mots` ET `definitions` doivent être retirés du payload public par l’intégrateur ; conserver `terminaisons` et `genres`. Première lettre jamais égale au segment entier (tous les segments ont au moins deux lettres). Paire radio/râteau rejetée à la relecture car accents incompatibles ; remplacée par rideau/rivière. Le segment `é` a été remplacé par `épi` (épice/épicerie).

Attention : les tests vérifient les relations de données, ils ne constituent pas une validation lexicographique ni clinique. Relecture informelle manuelle des 72 noms réalisée ; statut professionnel reste `a_revoir`. Aucune alternative supplémentaire identifiée et acceptée implicitement : variantes vides ; toute alternative nouvelle doit inclure une justification des deux noms avant ajout.

Commandes exécutées avec succès : `python3 tools/generer_debut_commun.py` ; `python3 -m pytest -q backend/tests/test_debut_commun.py` → **3 passed**.

Restant à l’intégrateur : manifeste, catalogue, correction dispatch, suppression données solution du client, aides et validateurs (la détection de sous-chaînes courtes dans les aides produit de faux positifs pour ces segments), tests bout en bout. Aucun fichier partagé touché par l’agent lexical.
