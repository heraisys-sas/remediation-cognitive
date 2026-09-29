# ADR-016 — Déduction : la preuve exacte des phrases qui fixent seules une position

**Statut** : accepté (2026-09-29)

## Contexte

Le critère C (« les chaînes se recoupent ») bannit des paliers 2 à 4 toute phrase qui, prise seule, fixe une position : un placement direct déguisé, même sans type `case`. La détection reposait sur la seule propagation du solveur — incomplète : consistance d'arc à sens unique, sans l'unicité des cases. Verdict rendu après la nuit du 28 : « zéro phrase solo » au palier 3. Une énumération exhaustive indépendante a montré l'inverse : **19 phrases fautives dans 13 grilles sur 20** — des chaînes « diagonale, opposé, comparaison » qui fixent deux jetons d'un coup. Reproduction de référence : l'ex-df-3-03, première phrase → triangle rouge en case 8, cercle bleu en case 0 (le centre est exclu car deux jetons ne partagent pas une case).

Deux défauts de mesure s'y ajoutaient :

- le « k » publié était le **rang du premier préfixe** dans l'ordre de lecture — pas le nombre minimal de phrases à recouper ; il change au mélange, et le palier 1, décrit « dans l'ordre », est en réalité mélangé lui aussi ;
- la redondance interne était comptée à tort : la copie du premier atome conservait le champ `et` (retirer la dernière sous-information ne la retirait pas), et l'ancre n'était jamais testée.

## Décision

**1. Preuve exacte du « fixe seule ».** Une phrase fixe seule une position si celle-ci se répète dans **tous** les placements injectifs compatibles avec ses seules figures citées — énumération exhaustive avec cache, budget borné (100 000 visites) et **erreur explicite** si le budget est dépassé : un contrôle inachevé ne vaut jamais « pas de raccourci », et un faux zéro reste une erreur. La propagation binaire est complétée à la marge : réduction des **deux** extrémités d'une relation, appui interdit sur la même case (unicité), vocabulaire cité vérifié.

**2. Mesure honnête, sans prétention clinique.** `rang_lecture` : première certitude dans l'ordre présenté — dépend de l'ordre, n'est pas un minimum. `support_propage` : plus petit lot de 1 à 3 phrases qui détermine par propagation — **borne supérieure trouvée**, jamais un minimum prouvé. Redondances internes : chaque atome réellement retiré, ancre comprise, sans mutation.

**3. Contenu réparé, identifiants remplacés.** Les 13 grilles du palier 3 gardent leur solution ; chaque phrase solo est **scindée en deux chaînes de deux informations** qui partagent le maillon central (« ancre + opposé » et « opposé + comparaison ») — le croisement entre phrases restitue la déduction et aucune des deux ne fixe seule une position. Doublons exacts et chaînes scindées devenues redondantes retirés (vocabulaire requis protégé, plancher de quatre phrases). Nouveaux identifiants `dc-3-XX` (remplacement annoncé ; les `df-3-XX` remplacés ne seront pas réutilisés).

**4. Générateur aligné.** Types unaires retirés des relations du palier 3 (`pas-ligne`, `pas-colonne`, `pas-coin` sont des repères d'ancre) ; plancher de nettoyage ramené à quatre phrases (exigence du validateur) ; aide des paliers 2 à 4 réécrite autour du croisement ; descriptions des paliers corrigées — plus de promesse de séquence au palier 1, « moins de phrases » retiré du palier 4.

## Conséquences

- **Paliers 2 à 4 : zéro phrase solo sur tout le stock**, prouvé par énumération exacte et revérifié par un test indépendant (permutations brutes) rejoué sur le contenu du dépôt à chaque exécution des tests.
- Le **rapport de la nuit du 28 (commit `895efdf`) est dépassé sur le critère C** : ses conclusions reposaient sur la détection incomplète. L'historique est conservé ; un addendum est tracé dans `.cluster/nuit-deduction-20260928/` et la mesure du 29/09 fait foi (`.cluster/correction-deduction-20260929/`).
- Résidus assumés et mesurés : quatre grilles réparées gardent **une** phrase retirable chacune (leur contenu minimal tient en trois phrases ; le plancher de quatre phrases du validateur impose la quatrième) ; des chaînes scindées peuvent rester individuellement redondantes au sens de la mesure interne — documenté, non bloquant.
- Aucun indicateur publié n'est une mesure de difficulté clinique : la progression des paliers suit la grammaire (positif → négatif → relatif → complexe), pas une calibration.
