# 2026-09-15 — Enrichissement « mémoire & concentration » (sprint 2)

## Demande

Améliorer le logiciel avec des entraînements issus des techniques établies — neuropsychologie américaine (calcul sériel type PASAT, filtrage type d2, empan, n-back) et orthophonie française (apprentissage par paires, remédiation mnésique). Logique assimilée, matériel protégé non copié (ECPA/Pearson).

## Livré

- 2 thèmes, 306 items générés de façon déterministe (graine 20260904) : `memoire` 8 paliers × 18 (empan 3→6, paires 2→4, n-back 2→4), `concentration` 9 paliers × 18 (chaînes 3→7 opérations, cascades, double tâche 5→9, séries).
- Backend : `_SOURCES_PAR_THEME` +2, correction `memoire` (sans espaces/casse) et `concentration` (numérique), labels vocabulaires.
- Interface : phase de mémorisation (`zone-memo`, `afficherPhaseMemo`/`jouerAffichage`/`afficherQuestion`, `annulerMemo` sur tous les changements d'écran), styles sans déplacement (min-height réservés).
- Validateur multi-thèmes (cohérence calcul gated sur calcul-mental, `table` interdit hors calcul-mental, motif prerequis générique `^[a-z]+-palier-\d+$`).
- Tests : 99 passed (3 nouveaux). Validateur : 31 fichiers / 497 items / 0 erreur.
- Docs : fondements, protocoles (fatigue progressive dans le contenu), taxonomie, module-entraînement, contrat API (affichage temporisé + honnêteté stimulus).

## Pièges & apprentissages

- IDs générés sans zéro de padding sur le palier (`me-1-empan-01`, pas `me-01-…`) — cohérent avec le validateur (motif libre hors calcul-mental), mais garder en tête si on resserre les motifs un jour.
- Les manifests non calcul-mental n'ont pas de champ `table` — le validateur l'interdit désormais hors calcul-mental.
- Le temps de mémorisation est exclu de `temps_ms` : `etat.debutQuestion` n'est pris que quand la question s'affiche. `annulerMemo()` doit être appelé partout où l'on quitte l'écran (montrerItem, revenirAuxThemes, finirSeance) sous peine de timers zombies.
- Les sous-agents relancés (contenu + interface) ont fini par livrer : leurs diffs ont été intégrés tels quels (revue ligne à ligne), seuls les styles `.memo-*` manquaient — ajoutés à la main.
- `.cluster/enrichissement/spec.md` est hors du dépôt (racine workspace) — la spécification détaillée des paliers reste la référence si régénération.

## Reste à faire

- Relecture ortho/clinique `a_revoir` sur les 306 items.
- Errorless d'entrée de palier + prerequis anglais/Python (reportés).
- ADR-003 (React+Vite), requirements.txt, README dev.

## Suites (2026-09-20)

- **Vérification indépendante des réponses** : `tools/verifier_reponses.py` (nouveau) recalcule la réponse de chaque item depuis son énoncé — 497 items, 0 anomalie (séries à solution unique, bornes respectées, identifiants uniques). Contrôle à relancer après toute régénération de contenu.
- **Délégation indisponible** : les envois d'agents acceptés en début de session ont tous échoué à l'exécution (réponse 403 du fournisseur, 0 jeton produit) ; les lots livrés ont donc été relus et complétés à la main, et la vérification des réponses a été faite directement par script.
- **Demandes produit ouvertes** : exercices de récupération indicée (rappel d'un souvenir présent mais inaccessible) et exercices de remise en lien social après isolement prolongé — note d'orientation dans `DELIVERY/` (hors dépôt).

## 2026-09-26 — calcul mental : refonte de la progression

Demande : « inutile de faire la table des 10 et des 1 ; réfléchis à une approche plus
pédagogique ou clinique ».

- Constat : 9 paliers = 9 tables, chacune dans les deux sens (doublons commutatifs), énoncé
  réduit à un produit nu (« 2 × 1 »). Ni × 1 ni × 10 ne sont des faits à automatiser : ce sont
  des règles ; les driller ne construit rien.
- Nouvelle progression par familles : faits de base (compléments dans 10, doubles, +/- dans 20)
  → repères (compléments à 100, × 2 à × 5) → mémoire de travail (deux opérations) → numératie
  du quotidien (argent, quantités, durées). Énoncés en questions naturelles, aides de stratégie
  repliées, consigne de méthode au palier des deux opérations.
- Identifiants neufs (`cm2-`) pour ne pas hériter des états FSRS de l'ancien contenu (règle de
  versionnage). 157 items, 9 paliers.
- Ajout d'un **contrôle par recalcul** dans le validateur : il relit l'énoncé et refait le calcul.
  Il a attrapé une erreur réelle dès la première exécution (« article à 12 €, payé avec 10 € »
  → −2). Leçon confirmée : un contrôle qui ne partage pas le code du générateur trouve ce que
  l'auteur ne voit pas.

## 2026-09-26 (suite) — trois publics : dyscalculie, attention, lacunes

Demande : la même exigence doit servir la dyscalculie, le maintien de l'attention et les
lacunes sur certaines multiplications.

- **Dyscalculie** : palier « Sens du nombre » (comparer, situer, valeur de position,
  décomposer, doubler) — aucune opération : le socle de la représentation du nombre.
- **Lacunes** : palier « Faits difficiles (× 6 à × 9) » — les faits qui résistent, travaillés
  par stratégie (× 9 = × 10 − le nombre) ; la répétition espacée resservira ce qui est manqué.
  Noter le renversement : « × 10 », d'abord refusé comme table à driller, redevient utile
  comme **outil** pour calculer × 9.
- **Attention soutenue** : côté concentration, les séries vont de 3 à 7 opérations ; ce qui
  progresse est la longueur tenue, jamais la vitesse.
- **Contrôle indépendant étendu** (mêmes principes qu'ADR-011) : le validateur recalcule les
  séries de gauche à droite et les familles du sens du nombre. Test négatif : un total faussé
  est refusé.

## 2026-09-26 (soir) — autres séries + un contrôle qui mesurait dans le vide

Demande : « éventuellement via d'autres séries de test ».

- **Suites et erreurs** (palier 12) : continuer une suite, compter à rebours, repérer le nombre
  faux — attention soutenue et inhibition.
- **Faits à l'envers** (palier 13) : « 42 = 6 × ? », le fait cherché par l'autre bout.
- **Incident** : en étendant le contrôle par recalcul, je me suis aperçu que **plusieurs familles
  n'étaient pas vérifiées du tout** — un « ? » non échappé dans un motif de regex agit comme un
  quantificateur, le motif ne correspond jamais, et `_reponse_calculee` renvoyait None : le
  contrôle passait sans rien contrôler. Rien ne le signalait.
- Correctifs : motifs échappés ; **mesure de couverture** dans le validateur (part d'items
  réellement recalculés, seuil sur le thème — 92 % aujourd'hui, la famille « vie quotidienne »
  étant non calculable par nature) ; **test par forme d'énoncé** (`test_controle_calcul.py`).
- Leçon à garder : un contrôle doit **prouver qu'il a vérifié quelque chose** (couverture,
  compteur, test de la forme). Un silence n'est pas une validation.
