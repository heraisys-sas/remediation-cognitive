# Changelog

Format : [date] — [périmètre] — description. Les retours informels de l'orthophoniste sont journalisés ici, sans caution clinique.

## 2026-09-26 · Calcul mental : d'autres séries, et un contrôle qui vérifie sa couverture

Suite au principe « éventuellement via d'autres séries de test » : deux familles ajoutées, et une leçon d'outillage.

- **Suites et erreurs (palier 12)** — continuer une suite, compter à rebours, et **repérer le nombre qui ne suit pas** : attention soutenue et inhibition appliquées aux nombres.
- **Faits à l'envers (palier 13)** — « 42 = 6 × ? » : le fait cherché par l'autre bout, souvent plus révélateur d'une lacune que le produit direct.
- **Incident d'outillage, corrigé** : le contrôle par recalcul était devenu **silencieusement inopérant** pour plusieurs familles (un « ? » non échappé dans mes motifs). Un contrôle qui ne contrôle rien est plus dangereux que pas de contrôle. Le validateur **mesure désormais sa couverture** (92 % des items du thème sont recalculés ; seule la famille « vie quotidienne » échappe au calcul automatique) et un **test vérifie chaque forme d'énoncé**.
- Programme mis à jour (13 paliers) ; README et ADR-012 à jour.
- **Contrôles** — 934 items / 0 erreur ; 164 tests.

## 2026-09-26 · Calcul mental : dyscalculie, attention soutenue, lacunes ciblées

Demande : appliquer la même approche à la **dyscalculie**, aux problèmes de **maintien de l'attention** et aux **lacunes sur certaines multiplications**.

- **Dyscalculie — palier « Sens du nombre »** (nouveau) : comparer deux nombres, situer sur la ligne numérique, lire la valeur de position, décomposer, doubler. Aucune opération : c'est le socle de la représentation du nombre, qui manque avant les faits.
- **Lacunes ciblées — palier « Faits difficiles (× 6 à × 9) »** (nouveau) : les faits qui résistent (7 × 8, 8 × 9, 9 × 9, carrés), travaillés par **stratégie** et non par récitation (« × 9 = × 10 − le nombre », « × 8 = double de × 4 »). La sélection par répétition espacée resservira d'abord ce qui est manqué.
- **Maintien de l'attention** — thème *concentration* : les séries vont de 3 à 7 opérations avec aide de méthode ; ce qui progresse est la **longueur tenue**, jamais la vitesse.
- **Contrôle indépendant étendu** : le validateur recalcule désormais aussi les **séries** (évaluation de gauche à droite) et les familles du sens du nombre. Test négatif concluant (un total faussé est refusé).
- Programme mis à jour (11 paliers de calcul mental) ; **ADR-012** écrit ; README du thème et `AGENTS.md` à jour.
- **Contrôles** — 898 items / 0 erreur ; 162 tests.

## 2026-09-26 · Calcul mental : progression refondue (plus de tables de 1 ni de 10)

Demande : « inutile de faire la table des 10 et des 1 — réfléchis à une approche plus pédagogique ou clinique ».

- **Pourquoi c'était inutile** : × 1 et × 10 ne sont pas des faits à automatiser mais des **règles** ; les paliers couvraient en outre chaque table dans les deux sens (doublons commutatifs) et posaient un produit nu (« 2 × 1 »), forme scolaire peu utile à un adulte.
- **Nouvelle progression (9 paliers, 157 items)** : compléments dans 10 → doubles et presque-doubles → additions puis soustractions dans 20 → compléments à 100 → multiplications utiles (× 2 à × 5) → deux opérations enchaînées → argent (totaux, rendu) → quantités et durées. Les énoncés sont des questions naturelles.
- **Stratégies enseignées** : aide repliée sur les paliers concernés (le moyen, jamais le résultat) et consigne de méthode au palier des deux opérations.
- **Contrôle indépendant** : le validateur relit chaque énoncé et **recalcule la réponse** (opérations, compléments, montants) — il a immédiatement attrapé une erreur de génération réelle (« un article à 12 €, payé avec 10 € » → −2).
- **Identifiants neufs (`cm2-`)** : le contenu revu n'hérite pas des états de révision de l'ancien.
- **ADR-011** écrit ; protocoles, spec du module et README du thème mis à jour.
- **Contrôles** — 861 items / 0 erreur ; 162 tests.

## 2026-09-26 · Montants : « 180 € » reconnu pour « 180 euros »

Signalement : au thème méthodes, une réponse dictée « 180 € » n'était pas reconnue pour l'attente « 180 euros » (et la dictée peut aussi rendre « cent quatre-vingts euros »).

- **Cause** : le symbole « € » et l'abréviation « eur » n'étaient pas rapprochés du mot « euros » ; et les nombres composés en toutes lettres (« cent quatre-vingts ») étaient convertis mot à mot, donc cassés (« 100 quatre-vingts »).
- **Corrigé** : normalisation **déterministe** des montants et quantités — symbole, abréviation, nombre en toutes lettres (« cent quatre-vingts euros » = « 180 euros »), pour les euros comme pour les unités courantes (litres, kilos, jours…). « 280 € » reste différent de « 180 euros ».
- **Précision sur le moteur sémantique** : dans « méthodes », les réponses sont des **propositions à choisir** — le filet sémantique y est volontairement écarté (ADR-008), car les autres propositions sont des leurres proches. Pour une valeur (montant, heure, nombre), c'est l'équivalence déterministe qui doit juger, pas un moteur statistique.
- **Contrôles** — 12 cas d'équivalence et de différence, dont l'item réellement signalé ; 162 tests, 875 items, 0 erreur.

## 2026-09-26 · Réponse fausse acceptée : « vendredi soir » pour « jeudi soir »

Signalement : au quotidien, une réponse avec le **mauvais jour** a été acceptée.

- **Cause** : le filet sémantique (empreintes du poste) compare le **sens** — et « vendredi soir » ressemble à « jeudi soir » (proximité 0,85). Le défaut était plus large : « jeudi matin » passait pour « jeudi soir » (0,81) et « 14 h 30 » pour « 15 h 30 » (**0,999**).
- **Corrigé** : le filet ne **traverse jamais un jalon de sens** — jours, mois, moments de la journée, nombres (chiffres ou en toutes lettres ; « un/une » exclu, ce sont le plus souvent des articles). Dès que les jalons diffèrent, seule la comparaison normalisée compte.
- La tolérance de sens reste utile là où elle a du sens : « la cave » pour « la porte de la cave » (aucun jalon).
- Une variante acceptable se **déclare dans l'item** (`reponse.variantes`), plutôt que d'être devinée.
- **Contrôles** — 5 nouveaux tests (jalons différents refusés, jalons détectés, reformulation sans jalon acceptée, item réel du quotidien, heures distinctes) ; 158 tests, 875 items, 0 erreur.

## 2026-09-26 · Déduction : plus aucune régularité dans l'ordre des phrases

Signalement : la phrase qui parle de « coin » arrivait toujours en premier, avec le doute légitime que d'autres régularités du même genre subsistent plus loin.

- **Constat, plus large que signalé** : dans **chaque** palier, les 20 grilles commençaient par le même type de phrase (coin au palier 1, diagonale au 2, pas-diagonale au 3, coin au 4) — les phrases du vocabulaire obligatoire étaient placées en premier par le générateur.
- **Corrigé** : l'ordre des phrases est **tiré au sort** pour chaque grille. Vérifié après régénération : le type en tête varie, et **aucune position n'est figée** (auparavant la position 1 était toujours « coin », etc.).
- **Contrôle ajouté** : le validateur refuse désormais un palier dont plus de 60 % des grilles commencent par le même type de phrase, ou qui n'offre pas au moins trois types en tête. Test négatif fait : le contrôle échoue si l'on rétablit l'ancien ordre.
- **Remplacement de contenu (thème `deduction`)** — les 80 grilles sont régénérées (mêmes placements distincts).
- **Contrôles** — 875 items / 0 erreur ; 153 tests ; phrases rendues sans anomalie.

## 2026-09-26 · Durée maximale proposée partout (ADR-010)

Demande : « même souplesse partout ».

- Au-delà de dix minutes, **tous les thèmes** proposent l'arrêt au lieu de fermer la séance : la proposition est envoyée une seule fois, la séance reste ouverte, la personne décide (bouton « Terminer la séance »). La réponse en cours est toujours conservée.
- Le garde-fou de sur-sollicitation reste la **limite de séances par jour** (3 en entraînement) et le **nombre d'exercices par séance** (12, 6 pour la déduction).
- Le code de clôture automatique subsiste, pour un thème qui demanderait un jour une limite ferme.
- **ADR-010** ajouté ; ADR-007 annoté (la partie « durée proposée » n'est plus propre à la déduction) ; protocoles et contrat d'API mis à jour.
- **Contrôles** — test de durée réécrit (proposition, poursuite possible, fin rejouable, réponse après fin en 409) ; 153 tests, 875 items, 0 erreur.

## 2026-09-26 · Décisions écrites : ADR-007, ADR-008, ADR-009

Les quiproquos de la journée sont figés noir sur blanc, pour qu'ils ne se rejouent pas.

- **ADR-007 — Déduction : la résolution tient dans les phrases.** Une seule règle énoncée (chaque figure colorée posée une fois, une case = une figure), les phrases portent la résolution (chaînes, plusieurs informations), aucune phrase redondante, le solveur juge la déductibilité, deux contrôles indépendants (sens français, rendu), dosage propre au thème (6 grilles, 10 minutes proposées).
- **ADR-008 — Réponses : la forme ne fait pas la justesse.** Équivalences (heures, nombres, variantes, faute de frappe), moteur sémantique local (empreintes Apple, repli lexical) **jamais** appliqué aux choix multiples, aucune validation par modèle à l'exécution, chaque tolérance verrouillée par un test.
- **ADR-009 — Interface : ce qui s'exécute = ce qui est livré.** Fichiers sans cache et scripts versionnés, zones de réponse vidées à chaque étape, ces règles vérifiées automatiquement, et le rendu du contenu contrôlé par le **vrai** code de l'interface.
- Aucun code modifié ; `AGENTS.md` référence les trois nouvelles décisions.

## 2026-09-26 · Déduction : dix minutes proposées, six grilles par séance

Précision demandée : garder dix minutes **proposées**, et moins d'exercices par séquence.

- **Durée proposée** : pour la déduction, la séance ne se ferme plus d'elle-même au bout de dix minutes — elle **propose** l'arrêt, une seule fois, et la personne décide (« tu peux t'arrêter là (bouton « Terminer la séance ») ou continuer »). S'arrêter au milieu d'une grille serait brutal, et le cadre clinique veut que l'arrêt soit proposé, jamais imposé.
- **Six grilles par séance** pour la déduction (déjà en place), durée maximale inchangée à dix minutes ; les autres thèmes gardent le garde-fou de durée ferme et douze exercices.
- La réponse en cours reste **toujours** conservée, dans tous les cas.
- **Contrôles** — nouveau test (proposition renvoyée une seule fois, séance encore ouverte, arrêt explicite possible) ; 153 tests, 875 items, 0 erreur.

## 2026-09-26 · Déduction : six grilles par séance (même durée de 10 min)

Demande : moins de tests par séance pour la déduction, et une durée allongée.

- **Ce que dit la documentation clinique** : séance courte **≤ 10 min** (cadre d'usage), 5-10 min (protocoles), arrêt proposé jamais imposé. Douze grilles de raisonnement ne tiennent pas dans dix minutes.
- **Décision** : on ajuste le **nombre d'exercices**, pas la durée — **six grilles par séance** pour la déduction, durée maximale inchangée à 10 minutes (le garde-fou anti sur-sollicitation reste). Allonger à 15 minutes serait une exception au cadre clinique : à documenter explicitement si tu la veux.
- **Mécanisme** : paramètres de séance par thème (`dosage.parametres_seance`), les autres thèmes gardent 12 exercices / 10 minutes. Une séance de déduction se termine donc par son contenu, et non par le minuteur.
- **Documentation** : protocoles cliniques (tableau de dosage par thème), contrat d'API, README du thème.
- **Contrôles** — nouveau test (6 items, 600 s, les autres thèmes inchangés) ; 152 tests, 875 items, 0 erreur.

## 2026-09-26 · Déduction : impossible de valider au 4ᵉ test (409 en cours de séance)

Signalement : au 4ᵉ exercice d'une séance de déduction, « la séance n'est plus disponible » et un 409 côté serveur.

- **Cause** : le garde-fou de durée (10 minutes, dosage clinique) **rejetait la réponse en cours** au lieu de clore la séance. Les grilles de déduction étant longues, la limite tombait au milieu d'un exercice : la personne voyait son travail refusé.
- **Corrigé** : la réponse arrivée après la limite est **enregistrée** (FSRS, maîtrise, baseline) *puis* la séance se clôt ; la réponse porte `seance_terminee: true` et l'interface affiche « Séance terminée : la durée maximale est atteinte. Ta réponse est enregistrée. » puis propose le résumé. Une réponse *suivante* reçoit 409 — la séance est bien close.
- **Fin de séance idempotente** : `POST …/fin` sur une séance déjà close renvoie **le même résumé** (200) au lieu d'un conflit. L'interface peut donc toujours afficher le résumé, y compris après une clôture automatique. Contrat d'API mis à jour.
- **Contrôles** — deux tests adaptés à la nouvelle règle (réponse après la limite conservée, fin idempotente) ; 151 tests, 875 items, 0 erreur.

## 2026-09-26 · Réponses : toutes les façons de dire l'heure

Signalement : « 15 heures » refusé pour un item attendant « 15 h » (thème méthodes).

- **Cause** : le normalisateur d'heures coupait le mot « heures » en deux (« 15 heures » devenait « 15heures »). Seules les écritures « 15h », « 15 h » et « 15:00 » passaient.
- **Corrigé** : toutes les façons françaises de dire l'heure sont ramenées à la même forme — « 15 heures », « quinze heures », « 15 heures 30 », « 3 heures et demie », « 15 heures moins le quart », « midi », « midi et demi », « 8 heures du soir » (20 h), « 15 heures du matin ». L'exercice porte sur le raisonnement, pas sur l'écriture de l'heure.
- **Moteur sémantique du poste** branché sur les réponses **libres** de « méthodes » (reformulations acceptées via les empreintes Apple). Il est volontairement **écarté des choix multiples** : les autres propositions sont des leurres proches par construction.
- **Tests** — 4 nouveaux cas (équivalences, différences, item réel, garde-fou des choix).

## 2026-09-25 · Changement de rubrique : les propositions du test précédent restaient affichées

Signalement : en passant de « Retrouver le mot » à « Méthodes » (et inversement), les propositions du test quitté restaient visibles sous le nouveau test.

- **Cause** : la phase de mémorisation masquait le formulaire mais ne vidait pas les **zones de réponse**. Les propositions du test précédent — et, plus largement, une grille de déduction ou les invites d'analyse de mot — restaient affichées jusqu'à la première question du test suivant.
- **Corrigé** : une fonction unique `viderZonesReponse()` vide les quatre zones concernées (choix, indices, génération, grille) ; elle est appelée à **chaque nouvelle étape** (mémorisation et question).
- **Garde-fou** : le contrôle d'interface vérifie désormais que le vidage couvre les quatre zones et qu'il est bien appelé dans les deux phases. Test négatif réalisé : en retirant l'appel, le contrôle échoue.
- **Contrôles** — 875 items / 0 erreur ; 147 tests.

## 2026-09-25 · Déduction : diagonales, coins, « à l'opposé de », et zéro phrase redondante

Demande : enrichir le vocabulaire des phrases et supprimer les indications redondantes.

- **Nouveau vocabulaire** — `coin` (positif), `diagonale` (descendante) et `diagonale-inverse` (montante) avec leurs formes négatives, `voisin-diagonale` (« touche … en diagonale »), et `oppose` (« à l'opposé de … », case symétrique par rapport au centre).
- **Présence garantie** — le choix laissé libre sacrifiait ce vocabulaire rare au profit de chaînes plus longues : chaque palier doit désormais contenir au moins une phrase de chaque forme demandée (coin au palier 1, diagonales en 2, négations diagonales en 3, « à l'opposé » en 4), et ces phrases sont protégées du nettoyage.
- **Zéro phrase redondante** — passe de minimalisation : toute phrase retirable sans perdre la solution est supprimée. Vérifié indépendamment : retirer n'importe quelle phrase casse la déductibilité.
- **Contrôles de sens étendus** aux nouveaux types (coin, diagonales, opposé, voisinage diagonal), côté validateur comme côté interface.
- **Remplacement de contenu (thème `deduction`)** — les 80 grilles sont régénérées.
- **Contrôles** — 875 items / 0 erreur ; 719 phrases / 1135 informations rendues sans anomalie ; 147 tests.

## 2026-09-25 · Déduction : relations de voisinage inversées (grilles insolubles)

Signalement : « la solution inverse le haut et le bas par rapport à ce que décrivent les phrases ».

- **Cause** : les quatre relations de voisinage étaient inversées entre le nom de l'indice et sa signification — « voisin-dessus » exigeait que la figure citée soit **au-dessus** du sujet, donc la phrase disait le contraire de la solution. Les grilles des paliers 1, 2 et 4 étaient **insolubles** ; le palier 3 était épargné (il n'utilise pas le voisinage).
- **Corrigé** : convention unique et documentée dans le moteur — « Le carré bleu est juste à gauche du cercle rouge » se vérifie par « le cercle rouge est une colonne à droite du carré bleu » (idem dessus/dessous).
- **Nouveau contrôle de sens** dans le validateur : chaque phrase est relue **selon son sens français**, indépendamment du solveur. Il a immédiatement signalé les 540 phrases contradictoires du contenu fautif, puis 0 après régénération.
- **Garde-fou d'interface** : le vérificateur de phrases contrôle que chaque type de relation s'écrit bien ce qu'il annonce (« voisin-dessus » ne peut pas produire « en dessous »).
- **Remplacement de contenu (thème `deduction`)** — les 80 grilles sont régénérées avec la convention corrigée.
- **Contrôles** — 875 items / 0 erreur ; 147 tests.

## 2026-09-25 · Interface : URL de script versionnée (fin des scripts périmés)

Le script restait en cache du navigateur malgré la correction : le serveur en cours d'exécution datait d'avant les en-têtes anti-cache.

- **URL versionnée** dans `index.html` (`src/app.js?v=…`, à incrémenter après toute modification) : le navigateur ne peut plus réutiliser un ancien script, même sans redémarrer le serveur.
- Contrôlé sur une instance neuve : `index.html` annonce la version, et `src/app.js` part avec `Cache-Control: no-cache, no-store, must-revalidate`.
- Rappel d'exploitation : après une modification de `frontend/src/`, relancer le serveur puis recharger la page (Cmd + Option + R).

## 2026-09-25 · Déduction : phrases tronquées (script périmé en cache) + négations perdues

Signalement : « Le triangle vert est dans la colonne du centre et . » — phrase incomplète, tableau impossible à remplir.

- **Cause première** : le navigateur exécutait une **version périmée du script** avec le **contenu courant**. L'ancien formateur ne connaissait pas le nouveau format de phrase (`et` devenu liste) et produisait « … et . ». Correctif de fond : l'interface est servie **sans mise en cache** (`Cache-Control: no-store`) — un script périmé ne peut plus se mélanger au contenu. Deux tests verrouillent les en-têtes.
- **Bug réel trouvé en vérifiant** : le nouveau formateur de phrases **perdait les négations** il aurait écrit « Le carré rouge dans un coin » au lieu de « n'est pas dans un coin ». Corrigé, avec les compléments de prédicat et le verbe assemblés au même endroit.
- **Langue** : en 4×4, « sur la ligne de la deuxième » devient « sur la ligne 2 » ; la relation de comparaison se dit « sur la même ligne que le carré vert, à sa gauche ».
- **Nouveau contrôle** : `tools/verifier_phrases.js` rend **toutes les phrases du contenu** avec le vrai code de l'interface et refuse une phrase vide, sans verbe ou avec `undefined`. 700 phrases vérifiées.
- **Contrôles** — 875 items / 0 erreur ; 147 tests.

## 2026-09-25 · Déduction : les phrases contiennent la résolution (fin de la règle inventée)

Retour de conception : la règle « chaque figure et chaque couleur une fois par ligne et par colonne » n'est **pas** une règle de l'exercice. Elle avait été ajoutée pour que peu de phrases suffisent, et elle rendait la grille impossible à reconstruire honnêtement. Corrigé en profondeur.

- **Une seule règle désormais** : chaque figure colorée se pose une fois, une case ne contient qu'une figure. Tout le reste vient des phrases ; la consigne le dit ainsi.
- **Phrases en chaîne** — un repère, puis des relations d'une figure à la suivante : « Le carré rouge est sur la ligne du bas, est juste à droite du cercle vert, qui est juste au-dessus du cercle rouge. » Trois informations et plus par phrase, donc **moins de phrases** (4 au palier 1, 8 aux paliers 2-3, 15 en 4×4).
- **Le solveur juge avec la seule règle énoncée** : la déductibilité est prouvée sans aucune règle ajoutée. Sélection gloutonne pilotée par le solveur (la phrase qui détermine le plus de cases).
- **Paliers différenciés** : 1 chaînes longues de voisinage ; 2 relations variées ; 3 repères négatifs et relations lâches (élimination) ; 4 grille 4×4.
- **Remplacement de contenu (thème `deduction`)** — les 80 grilles sont régénérées ; placements tous distincts. L'univers passe de 72 solutions 3×3 à 9! = 362 880 : le stock n'est plus limité.
- **Validateur** : plus de contrôle de ligne/colonne ; refus d'un placement direct, d'une phrase à une seule information ou d'une phrase sans relation.
- **Contrôles** — 875 items / 0 erreur ; 145 tests.

## 2026-09-25 · Déduction : palette qui se grise

- **Les figures déjà posées sont grisées** dans la palette et ne sont plus sélectionnables : on ne peut pas placer deux fois la même figure colorée. Elles redeviennent disponibles dès qu'on les retire de la grille (clic sur la case occupée, ou « Vider la grille »).
- **Poser sur une case occupée** remplace le jeton et libère l'ancien ; après chaque pose, la sélection se vide.

## 2026-09-25 · Outil d'essai : rouvrir la journée

- **`tools/reinitialiser_seances.py`** — remet à zéro le compteur de séances du jour, pour un thème ou pour tous (`--dry-run` disponible). Le dosage clinique (3 séances/jour en entraînement, 1 en évaluation) n'est pas modifié : l'outil sert à poursuivre les essais sans attendre le lendemain, et ne touche ni aux cartes de révision, ni aux courbes de maîtrise, ni au journal.

## 2026-09-25 · Déduction : phrases à deux informations, règles énoncées, brouillon cliquable

Retour d'usage : « les indices sont insuffisants pour reconstruire l'ensemble du tableau, il n'y a pas plusieurs indices par phrase, aucune déduction n'est provoquée ». Trois causes, trois corrections.

- **Règles enfin énoncées** — la consigne dit maintenant ce que le puzzle exige vraiment : chaque figure une fois par ligne **et** par colonne, chaque couleur aussi, donc chaque figure colorée une seule fois. Sans ces règles, les dernières cases étaient réellement ambiguës : c'était la cause de l'impression d'insuffisance.
- **Chaque phrase porte deux informations** — les placements directs à recopier disparaissent (sauf trois ancres de départ en 4×4). Les phrases croisent désormais deux contraintes sur la même figure (« sur la ligne du haut, mais pas dans la colonne de gauche ») ou relient deux figures (« juste à gauche de », « plus à droite que », « pas sur la même ligne que »). Nouveaux types : `pas-ligne`, `pas-colonne`, `a-droite-de`, `a-gauche-de`, `au-dessus-de`, `en-dessous-de`, et le champ `et` qui compose deux informations.
- **Le tableau de déduction** — le brouillon papier du logigramme devient un outil cliquable sous la grille : une ligne par figure colorée, une colonne par case, un clic pour marquer ✗ (impossible) ou ✓ (certain). C'est la mémoire de travail externalisée, comme le veut la pratique orthophonique.
- **Remplacement de contenu (thème `deduction`)** — les 80 grilles sont régénérées avec la nouvelle grammaire ; identifiants, paliers et solutions restent distincts (80 solutions différentes).
- **Difficulté croissante** — palier 1 : croisements ligne × colonne ; palier 2 : relations entre figures ; palier 3 : négations et conditionnel ; palier 4 : 4×4 avec ancres de départ.
- **Contrôles** — 875 items / 0 erreur ; 145 tests.

## 2026-09-25 · Déduction : toujours résoluble, et un stock pour trois mois

- **Grilles garanties déductibles** — un solveur de déduction (propagation de contraintes, sans hypothèse) juge chaque puzzle à la génération : les indices sont ajoutés **jusqu'à ce que le solveur termine**. Une grille qu'on ne peut pas reconstruire par raisonnement pur n'est plus livrable — le générateur l'écarte, le validateur la refuse, un test rejoue le solveur sur chaque grille du dépôt.
- **Remplacement de contenu (thème `deduction` uniquement)** — les 16 grilles précédentes sont remplacées par **80 grilles** (20 par palier), régénérées avec la même graine et le même schéma ; les identifiants (`de-p-00`) et les paliers sont inchangés, les jeux d'indices sont plus complets (5-7 phrases en 3×3, 11-14 en 4×4).
- **Aucune solution resservie** — l'univers des solutions est fini (72 grilles 3×3, 6 912 en 4×4) ; une même solution n'apparaît jamais deux fois dans le thème (60/72 utilisées en 3×3).
- **Difficulté croissante** — palier 1 : indices de position ; palier 2 : relationnels ; palier 3 : négatifs et conditionnels ; palier 4 : grille 4×4.
- **Contrôles** — 875 items / 0 erreur ; 144 tests.

## 2026-09-25 · Dictée : la réponse s'écrit en direct

- **Transcription au fur et à mesure** — pendant la dictée, ce qui est entendu s'affiche **dans le champ de réponse** au fil de la parole (résultats provisoires), puis le texte définitif remplace le provisoire. On voit donc ce qui a été compris **avant** de valider.
- **Rien n'est écrasé** — le texte déjà saisi avant la dictée est conservé et complété.
- **Repère visuel** — le champ s'entoure d'un liseré pendant l'écoute.
- **Rappel de confidentialité** — selon le navigateur, la reconnaissance peut être **sur l'appareil** (Safari/Siri) ou passer par un service distant (Chrome utilise souvent les serveurs de Google). Pour un usage sensible, préférer un navigateur en mode « sur l'appareil », comme indiqué dans `docs/30-technique/pistes-extension-ia.md`.
- **Contrôles** — 811 items / 0 erreur ; 143 tests.

## 2026-09-25 · Réponses dictées : les nombres en lettres sont compris

- **Bug corrigé** — une réponse donnée à voix haute dans un exercice de calcul (« six ») était refusée alors que 6 était attendu. La comparaison numérique n'acceptait que les chiffres ; elle comprend désormais les **nombres en toutes lettres** (« six » = 6, « quarante-deux » = 42, « quatre-vingt-dix-sept » = 97, « deux cent trente » = 230), y compris avec la ponctuation finale qu'ajoute la dictée (« six. »).
- **Portée** — calcul mental, concentration (chaînes, cascades, double tâche, séries) et estimation de durée. « sept » pour 8 reste refusé, comme « banane ».
- **À savoir** — la reconnaissance **sémantique** (empreintes de phrases) est active, mais elle ne sert qu'aux réponses **en texte** : pour les nombres, c'est cette conversion déterministe qui s'applique (mesuré : « deux »/« 2 » ne sont proches qu'à 0,33 pour le modèle, alors que la conversion est exacte).
- **Contrôles** — 811 items / 0 erreur ; **143 tests**.

## 2026-09-25 · Lecture automatique par défaut, désactivable à tout moment

- **Lecture par défaut** — tout ce qui s'affiche se dit : la consigne pendant la mémorisation, le stimulus (texte, liste, fiche) à l'affichage, puis la question.
- **Case bien placée** — une case « Lecture automatique » accompagne le bouton « Écouter », en haut de la zone d'exercice (toujours au même endroit, sans défilement). La décocher coupe la lecture **immédiatement** ; la recocher la rétablit aussitôt.
- **Le réglage est gardé** d'une séance à l'autre (`localStorage`) ; par défaut : activé. Le bouton « Écouter » reste disponible indépendamment du réglage.
- **Contrôles** — 811 items / 0 erreur ; 140 tests.

## 2026-09-25 · Consignes : dites une fois, pas répétées à chaque question

- **Constat** — la consigne de méthode (« focalise-toi sur le qui, quoi, comment »…) revenait à chaque question, à l'écrit comme à l'oral : rébarbatif, et cela noie la question elle-même.
- **Correctif** — l'audio ne lit plus que la **question** ; la consigne de méthode n'est **affichée qu'une fois par type d'exercice dans la séance** (ensuite, une phrase courte du type « Mémorise le contenu affiché. » suffit). Le rappel de méthode reste disponible à tout moment dans le panneau « Méthode — avant de répondre ».
- **Effet** — la séance s'allège : la première occurrence d'un type porte la méthode, les suivantes ne portent que l'exercice.
- **Contrôles** — 811 items / 0 erreur ; 140 tests.

## 2026-09-25 · Écoute : plus de fuite d'indice, et ergonomie de la mémorisation

- **Bug corrigé** — « Écouter » lisait la **question** pendant la phase de mémorisation : la réponse était donc suggérée avant même d'avoir vu le stimulus (signalé sur « au quotidien », mais le défaut concernait toutes les familles à stimulus). Le bouton lit désormais **ce qui est affiché** : la consigne pendant la mémorisation, puis la consigne et la question une fois affichées.
- **Ergonomie** — le stimulus (texte PQRST, liste de paires, fiche à retenir) se **lit automatiquement** au clic sur « Afficher » : on écoute ce qu'on lit. Les séquences (empans, double tâche) restent visuelles — leur rythme est trop précis pour être doublé par une voix.
- **Libellé** — le bouton s'appelle simplement « 🔊 Écouter », avec une infobulle qui dit ce qu'il lit.
- **Contrôles** — **811 items / 0 erreur** ; **140 tests**.

## 2026-09-25 · Couche de capacités du poste (local) — sens, voix, écoute

- **Similarité sémantique hors ligne** — `backend/app/domain/capacites.py` utilise les **empreintes de phrases d'Apple** (`NLEmbedding`) quand elles existent, sinon une comparaison lexicale (sans aucune dépendance). Seuil **0,78**, calibré sur cas réels (paraphrases 0,80–0,90 ; distracteurs 0,42–0,68).
- **La correction juge le sens** — un synonyme est accepté en accès lexical (« bicyclette » pour « vélo », « toubib » pour « médecin ») et une formulation proche en prise de message (« la cave » pour « la porte de la cave »). Une réponse éloignée reste refusée.
- **Voix du système** — synthèse par `say`/`afconvert` (macOS), PowerShell/SAPI (Windows), `espeak` (Linux) ; **dictée assurée côté client** par l'API du navigateur, qui s'appuie sur les moteurs de l'OS. Tout **local** : aucune donnée ne quitte le poste.
- **API** — `GET /api/capacites`, `POST /api/capacites/similarite`, `POST /api/capacites/synthese`.
- **Interface** — boutons « Répondre à voix haute » et « Écouter la consigne », masqués si le poste ne les propose pas ; repli clavier toujours possible.
- **Portabilité** — aucun paquet obligatoire ; sur macOS, `pyobjc-framework-NaturalLanguage` active les empreintes. `docs/30-technique/pistes-extension-ia.md` mis à jour (local vs serveur, capacités par plateforme, étape suivante : ONNX).
- **Contrôles** — **811 items / 0 erreur** ; **140 tests**.

## 2026-09-25 · Reconnaissance des réponses : tolérance élargie

- **Correctif** — « 15h » n'était pas accepté pour « 15 h » : la normalisation des heures exigeait des minutes. Elle couvre maintenant l'heure seule et l'heure pleine (« 15 h » = « 15h » = « 15:00 » = « 15h00 »), dans **toutes** les familles concernées (méthodes, vie quotidienne, accès au mot), et plus seulement la prise de message.
- **Capacité d'auteur** — un item peut déclarer `reponse.variantes` (synonymes, autre écriture) : « bicyclette » est accepté pour « vélo », « frigo » pour « réfrigérateur ». Contrôlé par le validateur.
- **Faute de frappe tolérée** (accès lexical) — une petite faute reste acceptée (distance 1, ou 2 pour un mot long) : l'exercice porte sur la mémoire, pas sur l'orthographe. Un pluriel passe (« marteaux » pour « marteau »).
- **Pistes d'extension IA** — nouvelle note `docs/30-technique/pistes-extension-ia.md` : du moteur de tolérance (déjà là) aux empreintes sémantiques locales, à la voix et à la génération de contenu.
- **Contrôles** — **811 items / 0 erreur** ; **134 tests**.

## 2026-09-24 · Retrait de la barrière de conformité (contexte POC / laboratoire)

- **Contexte acté** — ce dépôt est un **POC de laboratoire** : pas de garde-fou bloquant, pas de barrière « matériel protégé ». La règle est notée en tête du guide du dépôt.
- **Contrôle de conformité retiré** — `tools/verifier_clinique.py` n'est plus exécuté ni référencé, et son test est supprimé. Le fichier reste sur disque (inert, marqué comme tel) en attendant approbation pour sa suppression — le garde-fou de sécurité a refusé la suppression de fichier ce tour-ci.
- **Énoncés neutralisés** — les mentions « aucun matériel protégé reproduit », « droits ECPA/Pearson », « strictement exclu » disparaissent du contenu, des outils, de la bibliographie, du cadre réglementaire et du README ; les citations d'auteurs restent (ce sont des sources).
- **Conservé volontairement** — les mécanismes **produit** que le mot « garde-fou » recouvrait aussi : dosage (600 s, 3 séances/jour, 1 pour l'évaluation), plafonds de difficulté, saisie bornée, thème sombre sans animation. Ce sont des choix d'usage, pas des barrières.
- **Contrôles restants** — `validate_items.py`, `verifier_reponses.py`, `verifier_interface.py` (cohérence technique) : **811 items / 0 erreur**, **132 tests**.

## 2026-09-24 · Retrait du thème « vie sociale », missions conservées et renommées

- **Thème retiré** — l'entraînement « vie sociale » (vignettes d'émotion, réponses adaptées, lecture d'intention ; 4 paliers, 40 items) est supprimé : jugé **trop simple à l'usage**, et redondant avec les missions.
- **Missions conservées, section renommée** — les 8 missions hors écran passent de « Missions hors écran » à **« Missions dans la vraie vie »**, avec un intitulé qui dit *pourquoi* elles existent : ce n'est pas l'exercice à l'écran qui rétablit le lien, c'est l'action réelle. Le texte d'introduction et `content/missions/README.md` explicitent les raisons (érosion des automatismes, anticipation négative, exposition progressive).
- **Contenu réorganisé** — les missions quittent `content/entrainement/social/` pour `content/missions/` ; le périmètre API `/api/social` devient **`/api/missions`** (`GET /api/missions`, `GET|POST /api/missions/journal`).
- **Programme de 8 semaines** — la rotation ne propose plus le thème retiré et intègre les thèmes actuels (quotidien, méthodes, déduction) ; plafonds de paliers mis à jour.
- **Documentation** — taxonomie, cadre d'usage, spécifications, contrat d'API et ADR-004 (annoté) mis à jour ; README dédié aux missions.
- **Contrôles** — **811 items / 0 erreur** ; **133 tests**.

## 2026-09-24 · Déduction — méthode des logic grids (taxonomie complète, aucun indice décoratif)

- **Recherche** — les puzzles de logique classiques suivent une taxonomie d'indices (*true/false*, *multi-elimination*, *neither/nor*, *either/or*, *greater/lesser*) et deux règles de qualité : **chaque combinaison est unique** et **aucune référence n'est répétée inutilement** dans les indices.
- **Taxonomie implémentée** — directs (`case`), ligne/colonne, relationnels (`voisin-*`, `comparaison`, `autre-ligne`, `autre-colonne`), négatifs (`pas-coin`, `pas-bord`, `ni-ni`) et **conditionnels** (`si-alors`). Chacun porte deux informations.
- **Plus d'indice décoratif** — le générateur ne complète plus avec des « règles » répétées : les indices sont ceux qui lèvent réellement une ambiguïté (4 à 9 par grille selon les cas). La règle générale reste dans la consigne.
- **Méthode de résolution enseignée** — la consigne porte la stratégie : noter les certitudes, barrer les impossibilités, recouper les indices reliant deux figures.
- **Bug corrigé** — les indices `voisin-gauche`/`voisin-droite` étaient inversés entre la construction et le test, et le solveur ne vérifiait pas que la solution survivante était bien celle visée : des indices pouvaient contredire la solution stockée. Les deux sont corrigés (le second est désormais vérifié).
- **Contrôles** — **851 items / 0 erreur** ; **135 tests**.

## 2026-09-24 · Déduction — indices à deux informations (retour d'usage)

- **Règle clarifiée** — chaque **figure colorée** (un carré bleu, un cercle rouge…) apparaît **une seule fois** dans la grille. La solution est un couple de carrés latins **orthogonaux** : c'est cette unicité qui rend les indices non ambigus.
- **Indices à deux informations** — chaque phrase nomme une figure colorée **et** indique soit sa position (« le carré bleu est en haut à gauche »), soit sa relation à une autre figure colorée (« le carré vert est juste en dessous du cercle bleu »), soit une élimination (« n'est pas dans un coin »). Nouveaux types : `case`, `ligne`, `colonne`, `voisin-gauche/droite/dessus/dessous`, `pas-coin`, `pas-bord`.
- **Validateur** — contrôle supplémentaire : chaque figure colorée unique dans la grille ; les indices à deux informations sont vérifiés comme vrais pour la solution.
- **Affichage** — libellés accentués (« carré ») dans l'interface.
- **Contrôles** — **851 items / 0 erreur** ; **135 tests** (dont l'unicité des figures colorées et la véracité des nouveaux indices).

## 2026-09-24 · Au quotidien — aide externe et pression du temps (paliers 7 et 8)

- **Aide externe adaptée** (palier 7, mémoire prospective) — choisir le bon support pour ne pas oublier : alarme au bon moment, objet déplacé au bon endroit, dossier sur le chemin de sortie. Règle enseignée : une aide est efficace quand elle est **au bon endroit, au bon moment, et visible juste avant l'action** — « compter sur sa mémoire » ou « noter dans un carnet qu'on ne relit pas » n'en sont pas.
- **Gestion de la pression du temps** (palier 8, vitesse en situation) — décider vite de l'essentiel quand le temps presse. Choix de conception : **pas d'exercice chronométré** (fatigant, anxiogène, transfert faible), mais la stratégie qui aide réellement en situation (simplifier, prioriser, préparer), dans l'esprit du *Time Pressure Management*.
- **Contrôles** — **851 items / 0 erreur** ; **135 tests** (aide externe, pression du temps).

## 2026-09-24 · Méthodes — approfondissement (PQRST ×2, vérification de plan, repérage d'info)

- **PQRST** — chaque texte est désormais testé par **deux questions de mémoire** (12 items au lieu de 6) : on ne peut pas réussir en retenant une seule information.
- **Vérification de plan** (nouveau, palier 4) — le « Vérifier » de GMT : un plan mal ordonné est affiché et l'utilisateur doit **repérer l'étape mal placée**. C'est la composante de vérification qui manquait.
- **Repérer l'information** (nouveau, palier 5) — attention sélective en situation : un court document (courrier, notice, affichette) s'affiche temporisé, et l'utilisateur cherche l'information demandée. Stratégie enseignée : repérer d'abord ce que la question demande.
- **Auto-instruction transversale** — un panneau « Méthode — avant de répondre » (trois questions) est disponible à tout moment pendant les séances, toutes familles confondues : la méthode cesse d'être un exercice isolé.
- **Contrôles** — **835 items / 0 erreur** ; **134 tests** (PQRST double, plan à vérifier, repérage d'information).

## 2026-09-24 · Évaluation vs entraînement + quatre méthodes de remédiation

- **Section « Évaluation »** — les thèmes sont catégorisés : les mesures (mémoire, concentration, rappel de séries) sont sorties de l'entraînement et regroupées dans une section dédiée, plafonnée à **une séance par jour** (répéter une mesure la fausse). L'entraînement de remédiation garde son dosage (3 séances/jour). API : chaque thème expose sa `categorie`.
- **SFA / PCA** — enrichissement de « retrouver le mot » (paliers 6 et 7) : l'utilisateur **génère lui-même les attributs** (catégorie, usage, lieu → ou premier son, syllabes, rime) puis nomme le mot. Les attributs ne sont pas notés — c'est leur génération qui fait le travail.
- **Méthodes** (nouveau thème, 22 items) — **PQRST** (mémoire de textes : lire avec une intention et se tester), **Goal Management Training** (but → plan d'étapes → vérification), **auto-instruction de Meichenbaum** (quelle question se poser avant d'agir).
- **Interface** — section « Évaluation » sur l'accueil, mode d'affichage « texte » (PQRST), zone de génération guidée (SFA/PCA), auto-instruction comme fil conducteur rappelé dans les consignes.
- **Contrôles** — **813 items / 0 erreur** ; **132 tests** (catégories, limite d'évaluation à 1 séance/jour, PQRST/GMT/auto-instruction, SFA/PCA).
- **Réserves** — passage visuel des nouveaux écrans à faire ; relecture orthophoniste à faire.

## 2026-09-24 · Déduction — suite : grille 4×4, indices de secours, nouveaux types

- **Grille 4×4** — nouveau palier 4 du thème « Déduction » : 4 figures (cercle, carré, triangle, losange) × 4 couleurs (rouge, bleu, vert, jaune), carré latin d'ordre 4, **12 indices** à recouper. Le solveur d'unicité travaille désormais **par dimension** (figures / couleurs), ce qui rend la 4×4 rapide et exacte.
- **Indices de secours** — chaque grille porte 3 indices supplémentaires (`contenu.indices`), révélés un par un par le bouton « Un indice » de l'interface : aide progressive, jamais une punition.
- **Nouveaux types d'indices** — « dans un coin » et « sur le bord » (coin/bord, figure et couleur), injectés quand ils apportent de l'information ; palier 2 enrichi d'indices de ligne/colonne.
- **Interface** — grille et palette désormais à taille dynamique (3×3 ou 4×4), glyphe losange et couleur jaune ajoutés, feedback des cases justes/fausses adapté à la taille.
- **Contrôles** — validateur généralisé à N (carré latin d'ordre 3 ou 4, indices principaux et de secours vrais) ; **779 items / 0 erreur** ; 124 tests au vert.
- **À vérifier** — passage visuel de la grille 4×4 et du bouton « Un indice » dans le navigateur ; relecture orthophoniste.

## 2026-09-24 · Déduction — grille logique 3×3 (figures × couleurs)

- **Nouvel exercice** — thème « Déduction » (12 grilles, 3 paliers) : grille 3×3 à remplir avec 3 figures et 3 couleurs, chaque figure et chaque couleur une fois par ligne et par colonne (carré latin), à résoudre en **recoupant six indices** (directs → ligne/colonne → négatifs). Sollicite raisonnement, mémoire de travail et fonctions exécutives.
- **Garanties** — chaque indice est vrai pour la solution (contrôle du validateur) ; les six indices déterminent la solution **de façon unique** (solveur intégré au générateur `tools/generer_deduction.py` : la génération échoue en cas d'ambiguïté).
- **Interface** — palette de 9 jetons (figure × couleur), placement par clic, bouton « Vider la grille », correction qui affiche les cases justes et fausses. La solution ne fuit jamais avant validation (test de non-divulgation).
- **Contrôles** — validateur 64 fichiers / **775 items / 0 erreur** ; réponses recalculées 0 anomalie ; garde-fous cliniques sans violation ; **124 tests** (2 nouveaux : correction exacte/inexacte, cohérence des indices avec la solution).
- **À vérifier** — l'interaction de placement est nouvelle : un passage visuel dans le navigateur reste à faire ; relecture orthophoniste à faire.

## 2026-09-23 · Remédiation — exercices fonctionnels (retournement de cadrage)

- **Constat d'orthophoniste** — les exercices précédents (empan, n-back, chaînes de calcul, séries) sont des **entraînements aux tests d'évaluation**, pas de la remédiation : ils mesurent une fonction, s'y entraîner transfère peu à la vie quotidienne. Retournement acté dans `docs/10-clinique/remediation.md` : on ne développe plus d'exercice d'allure évaluative ; on remédie la fonction **dans des situations de vie, avec des stratégies**, pour qu'elle se transfère. Les épreuves existantes seront **déplacées vers une section « évaluation »** quand ce module existera (elles restent utiles comme repères de progression).
- **Premier lot fonctionnel** — nouveau thème « Au quotidien » (3 paliers, 36 items) : **prise de message** (mémoire de travail : retenir qui/quoi/quand puis répondre), **étape suivante** (planification : choisir la prochaine étape d'une tâche), **estimation de durée** (anticipation, acceptée dans une fourchette). Chaque consigne enseigne une stratégie (regrouper, ordonner, comparer à une situation vécue).
- **Format et correction** — types `prise-message`, `etape-suivante`, `estimation-temps` ; fonctions `fonctions-executives` et `memoire-prospective` ; correction par fourchette pour l'estimation ; validateur : la réponse d'un prise-message doit figurer dans le message affiché (contrôle bloquant — a attrapé une réponse dérivée « celui de 16 h 42 » non présente telle quelle).
- **Contrôles** — validateur 57 fichiers / 727 items / 0 erreur ; réponses recalculées 0 anomalie ; garde-fous cliniques sans violation ; **121 tests** (3 nouveaux sur le thème).
- **Réserves** — relecture orthophoniste à faire ; les familles suivantes (par où commencer, remettre les étapes dans l'ordre, repérer une info dans un courrier, mémoire prospective) restent à construire ; le déplacement des épreuves vers « évaluation » est documenté mais non réalisé (à faire quand le module bilan existera).

## 2026-09-23 · Clinique — garde-fous automatisés, cadre d'usage et repères d'orientation

- **Contrôle clinique automatisé** — nouveau `tools/verifier_clinique.py` : vérifie sur le code et le contenu réels (1) que le vocabulaire non médical ne contient aucun terme clinique ou normatif, (2) le thème sombre sans animation et le respect de `prefers-reduced-motion` (photophobie), (3) qu'aucun instrument protégé (PASAT, MMSE, MoCA, ECPA, Pearson, Raven, GREFEX, TEA-Ch, BCEFA, RL/RI, 15 mots de Rey…) n'apparaît dans le contenu des items, (4) que chaque item porte un statut de relecture et qu'un « valide_informel » est daté. Résultat : aucune violation, 691 items à revoir.
- **Cadre d'usage** — nouveau `docs/10-clinique/cadre-usage.md` : ce que le logiciel est / n'est pas, précautions par famille d'exercices, signes d'alerte non diagnostiques, statuts de relecture. Référence pour la relecture orthophoniste.
- **Repères dans l'application** — bouton « Repères — quand en parler » sur l'accueil : quatre situations génériques (difficulté croissante, maux de tête aggravés, humeur/sommeil dégradés, gêne au quotidien) qui invitent à en parler à un professionnel, sans jamais poser de diagnostic.
- **Tests** — 4 nouveaux tests verrouillent les outils de contrôle (validateur, réponses, interface, clinique) ; **118 tests** au total.
- **Rappel de périmètre** — le contrôle clinique automatisé ne remplace pas la relecture orthophoniste ni l'usage réel : il garantit les garde-fous, pas la validité clinique.

## 2026-09-22 · Correctif — stabilité du contenu généré (isolation des tirages)

- **Constat (revue de commits)** — au sprint 4, l'ajout des paliers d'empan de mots a consommé 72 tirages sur un générateur aléatoire **partagé entre thèmes** : le thème `concentration`, généré ensuite, a été **réécrit à identifiants constants** (161 items sur 162, contenu différent, structure identique). Passé inaperçu car le message de commit ne parlait que d'ajouts.
- **Correctif** — tirages désormais **isolés par `thème:famille`** (`random.Random(f"{GRAINE}:{thème}:{famille}")`) dans `tools/generer_memo_concentration.py` et `tools/generer_evocation_social.py` ; `generer_rappel_series.py` déjà isolé par construction (une seule famille). Vérifié : générer un thème ne change plus les tirages d'un autre, ni ceux d'une autre famille.
- **Conséquence assumée** — cette isolation a elle-même **remplacé** du contenu : mémoire 216/216 items, concentration 162/162, evocation 24/50 (ordre des propositions), social 32/40 ; calcul mental et rappel de séries intactes. Aucune donnée d'usage n'existant à cette date, la décision est sans effet pour un utilisateur ; elle est consignée ici et dans `docs/30-technique/contenu-versionne.md`.
- **Règle écrite** — nouvelle page `docs/30-technique/contenu-versionne.md` : isolation des tirages, extension en fin de famille, **aucune régénération d'un contenu déjà servi** (remplacer les identifiants si nécessaire), modification annoncée dans le commit, contrôles obligatoires après génération. AGENTS.md pointe vers cette règle.
- **Contrôles** — validateur 53 fichiers / 691 items / 0 erreur ; réponses recalculées 0 anomalie ; 114 tests verts ; déterminisme confirmé (deux exécutions successives → empreinte identique).

## 2026-09-22 · Sprint 5 — programme d'entraînement de 8 semaines

- **Contenu** — `content/programmes/8-semaines.json` : 8 semaines × 7 jours (5 séances, 1 journée légère, 1 jour de repos), durée de 6 à 9 minutes selon la semaine, rotation des thèmes avec décalage hebdomadaire, **plafond de palier** par thème et par semaine (borne haute, jamais objectif). Généré par `tools/generer_programme.py`, validé par `tools/validate_items.py` (structure, thèmes réels, plafonds ≤ paliers disponibles, séance = un thème, repos sans thème).
- **API** — `GET /api/programme` : programme complet + **plan du jour** + règles. La date de début est posée au premier appel et ne bouge plus ; au-delà de la huitième semaine, le programme est « terminé » sans prolongation d'office. Stockage dédié (`backend/data/programme/`) limité à la date de début (ADR-006).
- **Interface** — bouton « Programme de 8 semaines » sur l'accueil (avec les missions) et écran dédié : plan du jour avec démarrage direct du thème proposé, vue d'ensemble des huit semaines, règles en clair.
- **Complexification** — encadrée par les bonnes pratiques : la maîtrise prime sur le calendrier, la fatigue est respectée, une journée manquée ne se rattrape pas, et après deux séances sous 50 % de réussite le palier courant est repris.
- **Vérification** — 114 tests verts (4 nouveaux sur le programme : plan du jour, avancement calendaire, stabilité de la date de début, fin de programme) ; validateur 53 fichiers / 691 items / 0 erreur.
- **Réserves** — relecture orthophoniste à faire ; aucun taux d'observance ni de complétion n'est calculé (ce ne serait pas une mesure clinique).

## 2026-09-22 · Sprint 4 — empan de mots, rappel de séries et correctifs d'usage

- **Correctifs** — le champ de saisie est de nouveau vidé à chaque nouvelle question (régression du sprint 3, vérifiée dans un navigateur) ; le rythme de présentation est rendu explicite (« 3 éléments · un toutes les 0,92 s ») et le blanc inter-éléments passe à 120 ms, ce qui lève l'ambiguïté d'un « environ 2 s » qui pouvait se lire comme une pause.
- **Empan de mots** — nouveaux paliers 9 à 12 du thème mémoire : 3 → 5 mots à l'endroit, puis 3 et 4 mots à l'envers (72 items). L'ordre est significatif ; la saisie est tolérante aux accents et à la casse.
- **Thème « Rappel de séries »** — 4 paliers, 32 items : une série de 4 mots, puis deux et trois séries avec rappel **de l'ensemble**, puis **rappel différé** (20 s d'attente, question sur toutes les séries ou sur la première seulement). Réussite au **seuil** déclaré par l'item ; l'interface affiche les mots retrouvés et manquants.
- **Interface** — section « Extra » regroupant Python et Anglais en bas de l'écran d'accueil ; compte à rebours visible (et passable) pour le rappel différé ; bandeau de série pendant l'affichage ; bilan de rappel sans jugement.
- **Contrôles** — validateur enrichi (rythme d'affichage borné 400–2000 ms, empan de mots, rappel libre : séries, portée, seuil, délai, unicité des mots) ; `tools/verifier_reponses.py` étendu ; **691 items, 0 anomalie** ; 110 tests verts.
- **Docs** — ADR-005, contrat d'API (rappel libre, mode « series », attente), module-entraînement, taxonomie, README de contenu.
- **Réserves** — relecture orthophoniste à faire ; le rappel partiel reste un repère de travail, jamais un score de mémoire.

## 2026-09-21 · Sprint 3 — accès au mot et vie sociale (90 items + 8 missions)

- **Contenu** — deux nouveaux thèmes : `evocation` (« Retrouver le mot » : reconnaissance, rappel indicé à indices progressifs, rappel de la source — 5 paliers × 10) et `social` (« Vie sociale » : vignettes d'émotion, réponses adaptées, lecture d'intention — 4 paliers × 10), plus 8 missions hors écran. Total : **587 items** ; validateur 0 erreur (contrôle bloquant : aucun indice ne contient la réponse, la réponse figure toujours parmi les propositions).
- **Familles d'exercices** — récupération indicée (catégorie → attaque phonologique → forme écrite), reconnaissance, mémoire de la source, cognition sociale et pragmatique. Matériel original ; principes issus des familles classiques, aucun contenu protégé reproduit.
- **API** — ouverture du champ optionnel `indice_utilise` (essai « assisté » quand la réponse est affichée : aucune erreur commise, mais FSRS en échec et taux de réussite non gonflé) ; résumé enrichi de `assistees` et `sans_aide` ; nouveau périmètre `/api/social` (missions + carnet) avec **stockage séparé** (`backend/data/journal/`) — ADR-004.
- **Interface** — propositions cliquables, indices révélés un par un (« Un indice » puis « Voir la réponse »), écran « Missions hors écran » avec préparation, note de retour et carnet ; contrôle de cohérence interface ↔ HTML automatisé (`tools/verifier_interface.py`).
- **Tests** — 106 passed (dont 10 nouveaux : tolérance accents/casse, essai assisté, bornes d'indice, missions, carnet, isolation des stockages) ; contrôle de bout en bout sur serveur réel (7 thèmes, missions, note de carnet, séance d'accès au mot, `/ui` servi).
- **Réserves** — relecture orthophoniste des 90 items et des 8 missions à faire (`a_revoir`) ; le carnet reste local et mono-utilisateur.

## 2026-09-20 · Vérification des réponses de contenu

- **Outil** — `tools/verifier_reponses.py` : recalcule la réponse attendue de chaque item depuis son énoncé (empan endroit/envers, n-back, paires associatives, chaînes et cascades, double tâche, séries à règle avec unicité de la solution) et compare au fichier ; lecture seule, code de sortie 1 en cas d'anomalie. Résultat sur le contenu actuel : 497 items, **0 anomalie**, identifiants uniques.
- **Usage** — à relancer après toute régénération de contenu, en complément de `tools/validate_items.py` (structure et schéma).

## 2026-09-15 · Sprint 2 — mémorisation & concentration (306 items)

- **Contenu** — deux nouveaux thèmes : `memoire` (8 paliers × 18 = 144 items : empan endroit/envers 3→6 chiffres, paires associatives mot–nombre 2→4, sonde n-back N=2→4) et `concentration` (9 paliers × 18 = 162 items : calcul chaîné 3→7 opérations, cascades de soustractions, double tâche de filtrage 5→9 éléments, séries à règle). Génération déterministe (graine 20260904, `tools/generer_memo_concentration.py`) ; validateur multi-thèmes (31 fichiers, 497 items, 0 erreur) ; familles classiques d'entraînement cognitif implémentées en original — logique assimilée (PASAT, d2), aucun matériel protégé copié.
- **API** — correction par thème étendue : `memoire` = texte sans espaces/casse (empans tapés avec espaces valides), `concentration` = numérique ; types `chaine-calcul`, `serie-manquante`, `paires-associatives` au schéma ; `contenu.affichage` (sequence/liste) documenté au contrat — le temps de mémorisation ne compte pas dans `temps_ms`, note d'honnêteté sur le stimulus présent dans le payload (usage mono-utilisateur assumé).
- **Interface** — phase de mémorisation sur `/ui` : consigne → « Afficher » → stimulus temporisé (élément par élément ou liste, bouton « Passer ») → stimulus masqué → question → saisie ; clavier numérique étendu aux nouveaux types ; zéro déplacement de mise en page (espaces réservés), dark oklch inchangé.
- **Tests** — 99 passed (96 + 3 : correction mémoire tolérante, correction concentration numérique, cycle E2E mémoire avec affichage temporisé) ; validateur 0 erreur.
- **Docs** — fondements (familles classiques), protocoles (fatigue progressive conçue dans le contenu), taxonomie (table familles/fonctions), module-entraînement (Mémoire/Concentration), contrat API.
- **Réserves** — relecture orthographique `a_revoir` sur les 306 items générés ; prerequis anglais/python inchangés ; ADR-003 (front vanilla → React+Vite) toujours à formaliser.

## 2026-09-03 · Sprint 1 — cycle calcul mental jouable

- **Moteur** — FSRS 6.3.2 (paquet officiel) encapsulé derrière `engine/srs/fsrs.py` ; `SessionRunner` (12 items / 600 s, fatigue = proposition seulement) ; maîtrise 90 % × 3 avec historique par palier ; fenêtre glissante ±1 palier.
- **Contenu** — 191 items : 9 paliers de calcul mental (×2, ×5, ×10, ×3, ×4, ×6, ×7, ×8, ×9 ; 19 items/palier) + échantillons anglais (10 verbes) et Python (10 builtins, production + prédiction de sortie) ; validateur sans dépendance (`tools/validate_items.py`, 0 erreur) ; 100 % original.
- **API** — contrat figé (`docs/30-technique/api-contract.md`) : thèmes, démarrage de séance (sélection due FSRS + nouveaux, réponse attendue jamais exposée), correction serveur par thème, fin de séance (FSRS + maîtrise + persistance JSON sous `backend/data/entrainement/`) ; garde-fous serveur : 3 séances/jour/thème, 12 items, durée max 600 s appliquée (auto-clôture de dosage ≠ fatigue), aucun endpoint bilan.
- **Interface** — SPA vanilla sur `/ui` (sans build) : dark oklch, contrastes ≥ 7:1, zéro clignotement (`prefers-reduced-motion` respecté), une question à la fois, feedback immédiat, bouton « Terminer la séance » toujours visible, alerte d'arrêt bienveillante, a11y (focus, aria-live, inputmode).
- **Revues intégrées** — exécution E2E réelle (serveur + cycle scripté : 24/25 vérifications) et conformité clinique (7 points OK, rien de grave). Correctifs : résumé de séance sur items *répondus* (et non servis), déduplication des essais, verrou sur le compteur journalier, baseline RT adaptative (médiane des temps corrects), durée max serveur, titre d'API neutralisé.
- **Tests** — 96 passed (engine 55 + backend 41), dont tests de régression des quatre constats de revue.
- **Réserves connues** — quota 3 séances/jour *par thème* (global à trancher) ; errorless d'entrée de palier et prerequis anglais/python à compléter ; READMEs de dev servis sous `/ui` ; ADR-003 (front vanilla → React+Vite) à formaliser.

## 2026-09-03 · Cadrage

- **Décision licence** — **BSD-3-Clause** choisie (code et contenu original) ; `LICENSE` rempli. Le dépôt peut désormais être diffusé ; hébergement GitHub créé en privé dans un premier temps.
- **Décision produit** — module Python cadré : mémorisation de concepts et de commandes du langage ; thématique cognitive à double dividende (l'effort de mémorisation est l'exercice, le contenu acquis est une compétence durable). Formats : errorless → production → prédiction de sortie ; cap de complexité de 2 niveaux d'imbrication en phase initiale.
- **Décision réglementaire (rappel)** — scission Entraînement (hors MDR) / Rééducation + Bilan (usage strictement familial) ; voie DM classe I différée en Phase 3.
- **Projet** — création du squelette d'arborescence (monorepo), documentation de cadrage, ADR-001 et ADR-002, schéma d'item normalisé.
