# 2026-10-08 — enrichissement du parcours Retrouver le mot

## 2026-10-08 — Refactorisation (issue #20)

Registre unique des thèmes et métadonnées d'interface, correcteurs et validateurs
modulaires, I/O des générateurs mutualisée. Interface vanilla séparée en comportements,
état de séance réinitialisable, progression pure extraite du service. Contrôles Ruff,
chargement des scripts et non-régression renforcés ; nettoyage des copies `.cluster`.
Contenu, règles de correction/dosage et persistance conservés. ADR-037.


Nouvelle banque adulte de 288 mots : douze paliers de 24, QCM uniquement au premier, départ Auto au deuxième. Difficulté graduée par précision et contexte ; quotas de séance 10/10/10/8/8/6, puis six questions pour les paliers supérieurs de culture générale et de langue soutenue. Le repère permanent de mode de réponse quitte la carte ; les précisions figurent dans les listes des réglages. Nouveaux identifiants ev2, anciennes banques et historiques conservés.

# 2026-10-07 — parcours lexical sans retour au QCM

Le palier 4 du parcours Retrouver le mot ne sélectionne plus les QCM de l'ancien niveau mixte : il sert les cinq rappels indicés existants. Le QCM reste au palier 1 ; les anciens items et historiques sont conservés. Les libellés de paliers précisent la tâche et le point de départ Auto (palier 2). Un repère textuel discret indique le mode de réponse sur cette carte.

# 2026-10-07 — ordre des cartes de thèmes

Retrouver des mots et leur contexte et Méthodes pour retenir et s’organiser sont placés immédiatement après Déduction et Calcul mental. L’ordre relatif des autres cartes est conservé.

# 2026-10-07 — autorisation micro avant la première question

Les séances de rappel lexical demandent l'accès au micro avant de présenter et lire la première question. Le flux autorisé est réutilisé pour éviter une deuxième demande. Refus ou échec d'ouverture : saisie clavier automatique, sans nouvelle ouverture automatique pendant la séance. La décision dans le dialogue d'autorisation est attendue avant la lecture.

# 2026-10-07 — préparer le micro avant la réponse lexicale

Le micro natif est ouvert pendant la lecture de la question, avec capture conservée et transcription désactivées jusqu’à sa fin. Cela retire l’ouverture du matériel du début de la réponse. Les transitions internes de la voix native ne rouvrent pas inutilement le micro préparé. Annulation et passage au clavier libèrent toujours le micro. Le « oui » rapporté sur la première réponse n’a pas été reproduit sur audio synthétique ; validation avec le microphone utilisateur nécessaire.

# 2026-10-07 — enchaînement du rappel lexical

Après une réponse correcte dans Retrouver le mot (rappel indicé), passage à la suite après trois secondes, ou au résumé en fin de séance. Le bouton reste utilisable immédiatement. Les réponses incorrectes et les autres types d'exercices restent à progression manuelle. Les minuteries sont annulées au changement d'écran.

# 2026-10-07 — réponse orale automatique pour retrouver un mot

Dans les items de rappel lexical, le micro local démarre après la lecture de la question. Les transcriptions provisoires sont affichées et vérifiées sans compter comme essais ; une réponse reconnue comme correcte est soumise une seule fois. « Répondre au clavier » coupe le micro et vide le champ. Les autres types d’exercices conservent leur mode de réponse.

# 2026-10-07 — extraction critique de la PR #11

Sauvegardes et compteurs protégés contre les accès concurrents, normalisation UTC partagée, correction ciblée de synthèse Windows et de détection macOS. Les comportements d'exercices, seuils de fatigue et fonctions vocales récentes sont conservés. Tests de concurrence, sélection et dates ajoutés ; workflow CI unique. Décisions détaillées dans `docs/30-technique/revue-pr11.md`.

# 2026-10-06 — prononciation française de triangle

Correction orale ciblée « triangle(s) » → « tri-angle(s) » pour éviter la lecture anglaise de l'homographe par certaines voix avancées. Appliquée à la lecture automatique et au bouton Écouter dans les thèmes français, pour le navigateur comme pour macOS. Texte affiché et réponses inchangés ; anglais et Python exclus. Le rendu vocal reste à apprécier à l'écoute selon la voix.

# 2026-10-05 — Audrey haute qualité via macOS

Le sélecteur ajoute les voix françaises Premium/Enhanced installées sur macOS, même si Chrome ne les expose pas. Leur lecture passe par le serveur local et `say`, sans service distant ni modèle ajouté. Le mode automatique privilégie ces voix ; les voix fantaisie sont retirées des choix navigateur. Une lecture native devenue obsolète après changement d'étape est ignorée. Redémarrage du backend nécessaire pour les nouvelles routes.

# 2026-10-05 — choix explicite de la voix française locale

L'interface ne force plus arbitrairement la première voix française : un sélecteur à côté d'Écouter permet de mémoriser la voix souhaitée. Le mode automatique privilégie la voix française locale marquée par défaut par le navigateur. La liste suit les changements de voix exposés par celui-ci ; aucune voix distante n'est utilisée comme secours. Les règles de prononciation et de non-répétition sont conservées.

# 2026-10-05 — lecture rétablie dans Actualiser une consigne

Le parcours masquait les commandes audio et annulait la lecture dès son lancement. Chaque message courant dispose désormais du bouton Écouter et de la lecture automatique, selon la préférence existante. La consigne générale n'est lue automatiquement qu'une fois par séance ; changer d'étape coupe l'ancien message et remplace le texte à relire. La restitution finale ne permet pas de réécouter les messages masqués. Prononciation des calculs et règles de lecture des autres thèmes conservées.

# 2026-10-03 — parcours clavier dans Au quotidien

Les boutons Afficher puis Passer reçoivent le focus à leur apparition dans Au quotidien : Entrée les active. La saisie, les choix de réponse et le bouton Suivant utilisaient déjà le focus et la validation clavier natifs. Aucun choix supplémentaire n’est déclenché automatiquement.

# 2026-10-03 — validation au clavier dans Actualiser une consigne

Entrée dans un champ de réponse déclenche désormais le bouton Valider lorsque tous les champs sont renseignés. Ces champs sont sur une seule ligne et ne nécessitent pas de retour à la ligne. La composition de texte et le maintien de la touche ne déclenchent pas de validation supplémentaire.

# 2026-10-03 — entre-deux plus lisible dans Déduction 3×3

La précision « sans être nécessairement voisins ni à égale distance » est retirée des indices entre-deux sur les grilles 3×3 (ligne, colonne et diagonale) : elle décrit une liberté impossible avec trois cases. Elle reste sur les grilles 4×4. La contrainte logique, les solutions et les identifiants sont inchangés ; seule leur formulation est allégée.

# 2026-10-03 — calcul adulte plus exigeant dès le palier 5

Remplacement des paliers 5–12 par 252 nouveaux items `cm4-…` : opérations directes, produits et divisions, transformations inverses, décimales, proportions, pourcentages et applications à plusieurs étapes. Le calcul pur reste présent à chaque palier ; méthodes spécifiques et réponses recalculées indépendamment. P1–4 conservés, 320 items au total. Historiques préservés, anciennes réussites exclues de la maîtrise du nouveau corpus. ADR-024.

# 2026-10-03 — séances supplémentaires de calcul mental réellement disponibles

Le commutateur « Dépasser la limite de séances » levait déjà le quota serveur, mais Calcul mental pouvait ne plus avoir de carte due après deux séances : la séance suivante était vide et donnait l'impression que le réglage ne fonctionnait pas. Calcul mental complète désormais une séance avec les cartes non dues dont l'échéance est la plus proche, sans changer la sélection des autres thèmes. Son plafond ordinaire passe de trois à six séances quotidiennes ; la dérogation permet toujours d'aller au-delà. Le résumé utilise ce plafond propre au thème.

Le mode Auto de Calcul mental ne commence plus par les compléments dans 10 : une progression neuve entre au palier 5, tandis que les paliers 1 à 4 restent disponibles dans le sélecteur. Une première séance automatique suffisamment complète (au moins huit réponses) et réussie à moins de 50 % ramène la séance suivante au palier 3. Les anciens historiques de socle réussis rejoignent le nouveau départ ; une difficulté déjà observée conserve le niveau stocké.

# 2026-10-02 — déduction allégée et lecture des indices réparée

Le panneau générique « Voir un coup de pouce » est masqué dans Déduction : il répétait la méthode alors que l'exercice possède déjà une aide au raisonnement graduée. Les aides propres à la grille et le tableau facultatif restent disponibles. Le bouton « Écouter » lit désormais la consigne puis toutes les phrases de la grille ; auparavant `contenu.enonce` était vide pour ce type structuré, donc aucun texte n'était envoyé à la synthèse vocale. En lecture automatique, une consigne identique n'est dite qu'à la première grille de la séance ; les indices nouveaux sont toujours lus et le bouton permet toujours de demander une relecture complète.

# 2026-10-02 — méthodes spécifiques plutôt qu'un rappel universel

Le triptyque générique « quoi faire / comment / vérifier » n'est plus affiché dans toutes les familles. Le panneau est désormais masqué quand aucune stratégie concrète n'est définie ; il montre en priorité la méthode propre à l'item, ou une stratégie stable adaptée à la déduction, aux empans, aux associations, au rappel de séries et à l'accès lexical. Les consignes stratégiques des tâches fonctionnelles restent consultables. Reconnaissance simple, anglais, Python et séquences déjà guidées n'ont plus de panneau redondant.

# 2026-10-02 — démarrage des exercices avec indices réparé

Le rendu d'un item à indices progressifs référençait par erreur une variable réservée à l'aide des grilles de déduction. Quand un tel item était tiré en premier dans « Retrouver des mots et leur contexte », la question était lue puis le démarrage affichait un échec. Le bouton d'indice lexical est de nouveau rendu indépendamment sous le libellé « Un indice ».

# 2026-10-02 — consigne audio non répétée

Pendant une séance de mémorisation, une consigne identique n'est désormais lue automatiquement qu'à sa première occurrence. Le rappel bref reste affiché sur les items suivants et le bouton « Écouter » permet toujours une répétition volontaire. Une consigne réellement différente est affichée et lue lors de sa première apparition.

# 2026-10-02 — cadence commune des séquences à mémoriser

Les empans de chiffres, les empans de mots et les séquences de lettres utilisent désormais la même cadence que les séries visuelles : chaque élément reste visible 2 secondes, puis un blanc de 2 secondes précède le suivant. Le contenu généré porte explicitement les deux durées, l'interface emploie aussi 2 secondes comme valeur de repli et le validateur refuse toute séquence plus rapide.

# 2026-10-02 — opérateurs mathématiques prononcés explicitement

La synthèse vocale reçoit désormais une formulation orale dédiée : `−` et le moins ASCII espacé deviennent « moins », `×`, `x` ou `*` entre espaces deviennent « multiplié par », `+`, `=` et `÷` sont également explicités. Un `?` occupant la place d’un terme dans une opération devient « quel nombre », tandis qu’un point d’interrogation final reste une ponctuation. Le texte affiché et les traits d’union des mots restent inchangés.

# 2026-10-02 — reprise après interruption réellement vécue

Le parcours Reprendre de « Garder le cap » remplace quatre vignettes décrites par douze contrôles réellement interrompus : quatre points à traiter, détour bref non noté après un à trois points, dossier masqué, identification du prochain point puis achèvement. Correction détaillée des décisions et de la reprise, nouveaux identifiants `cap-2-reprise-…`, double clic neutralisé. Adapter et Vérifier restent inchangés.

# 2026-10-01 — banques fonctionnelles enrichies

Actualiser une consigne, Comparer deux documents et Repérer l’essentiel passent de 4 à 12 situations par palier, en conservant quatre exercices par séance. Progressions rendues explicites, corrections successives et informations à conserver ajoutées, nombre d’écarts et de sélections rendu variable, distracteurs auto-révélateurs supprimés. Nouveaux identifiants `v2` ; double clic neutralisé dans le flux de sélection.

# 2026-10-01 — parcours homogènes et départ automatique ajusté

Les cartes Mémoire, Séries, Méthodes, Garder le cap et Évocation proposent maintenant des parcours dont les maîtrises, cartes FSRS et baselines sont séparées. Les stratégies SFA/PCA et la mémoire de la source ne sont plus des niveaux obligatoires de l'accès lexical ; PQRST guidé est directement accessible. Pour un parcours neuf, le mode automatique évite les entrées les plus faibles lorsqu'elles n'introduisent pas une manipulation indispensable (cinq chiffres, quatre mots, trois paires, deux séries, rappel lexical avec indices). Les historiques composites restent conservés sans être convertis. ADR-023.

# 2026-10-01 — retours PQRST et rappel libre fiabilisés

La reformulation PQRST n'est plus jugée par la seule présence de cinq mots-clés : chaque item déclare cinq critères, leurs formulations reconnues, leurs éventuels sous-faits et des contradictions explicites. Le retour distingue idées retrouvées, non reconnues et contredites ; les quatre séquences reçoivent des identifiants `mt2-…`. Le rappel libre distingue désormais cibles retrouvées, omissions, confusions entre séries et intrusions ; une intrusion ne produit plus une maîtrise complète malgré un rappel suffisant. Interface, générateur, validateur et tests synchronisés.

# 2026-10-01 — retrait de la carte chaînes et suites

Suppression complète de « Calculs en chaîne et suites » : carte, 162 items, générateur spécifique, types dédiés, compatibilité API, tests et historique local. Calcul mental et le moteur partagé restent inchangés.

# 2026-10-01 — séries et attention fonctionnelle

Rubriques clarifiées, parcours auditif autonome (48 mots AAC mutualisés, 329 ko), rythme visuel 2 s + 2 s. Remplacement des 32 items rs-* par rs2-* ; ajout de 32 listes auditives et de 36 situations fonctionnelles (actualiser, comparer, sélectionner). Les historiques des anciens thèmes sont conservés. Programme synchronisé, correction et interface couvertes par tests ; fondement et limites dans ADR-022.

# Changelog

Format : [date] — [périmètre] — description. Les retours informels de l'orthophoniste sont journalisés ici, sans caution clinique.

## 2026-09-30 · Accueil : accès secondaires remontés avant « Extra »

- Les trois accès (Programme, « Sociabilité — reprendre contact », Repères) passent au-dessus de la rubrique « Extra », séparés comme les autres rubriques ; « Extra » reste en fin de page.

## 2026-09-30 · Accueil : boutons du bas uniformisés ; « Sociabilité — reprendre contact »

- Les trois accès secondaires du bas de l'accueil (Programme, missions, Repères) partagent désormais le même style (secondaire) et sont légèrement espacés.
- Le bouton « Reprendre contact — missions dans la vraie vie » devient « Sociabilité — reprendre contact » ; l'écran « Missions dans la vraie vie » reste inchangé.

## 2026-09-30 · En-tête : commutateur de limite déplacé à droite du sous-titre

- Le commutateur « Dépasser la limite de séances » quitte le bas de l'accueil et passe dans l'en-tête, à droite de « Des séances courtes, à ton rythme. » — il reste visible sur toutes les vues ; la note de portée est raccourcie. Aucun changement de comportement ni d'API.

## 2026-09-30 · Évaluation : dérogation étendue, plafond hebdomadaire

- La dérogation « Dépasser la limite de séances » couvre désormais **tous les thèmes**, évaluation comprise ; libellé, note et messages de l'interface ajustés.
- La limite de l'évaluation passe d'une séance par jour à **une séance par semaine** (semaine calendaire, lundi–dimanche ; compteur par fenêtre, remis à zéro le lundi). Motif inchangé — répéter une mesure la fausse — et mieux servi par l'espacement hebdomadaire.
- Contrat : champ additif `fenetre_sessions` (`jour` | `semaine`) dans le résumé de fin ; `sessions_restantes_aujourdhui` reste le décompte, dans la fenêtre du thème. Résumé et refus 429 phrasés par fenêtre. ADR-021 ajusté ; `tools/reinitialiser_seances.py` adapté (fenêtre courante — l'évaluation se rouvre le lundi).

## 2026-09-30 · Limite de séances : dérogation explicite depuis l'accueil

- Nouveau réglage sur l'accueil — « Dépasser la limite de séances du jour » : il lève le plafond pour la journée **pour les entraînements** ; l'évaluation reste à une séance par jour (répéter une mesure la fausse). Désactivé par défaut, conservé d'une visite à l'autre ; l'état est visible sur la page.
- Le démarrage de séance transmet `sans_limite_sessions` (corps `DemarrageOptionnel`) : la dérogation est **accordée par le serveur**, jamais contournée par l'interface ; le compteur du jour continue de compter toutes les séances. Le résumé de fin remplace « séances restantes » par « Limite levée… » quand elle est active.
- Documentation : ADR-021, contrat d'API et README ajustés ; tests dédiés (API : dérogation accordée en entraînement, ignorée en évaluation, combinée au palier ; contrôle JS exécutant la vraie requête).

## 2026-09-30 · Déduction : clôture des suites du rapport du 29/09 (matin)

- Les deux suites du rapport de correction du matin du 29/09 portaient sur le corpus de 80 grilles, remplacé le soir même par la refonte à 100 grilles (`b68308a`) : **« quatre grilles à phrase retirable »** (palier 3, ex-`dc-3-12/16/17/20`) et **« redondances du palier 4 à arbitrer »** (122 mesurées) sont **closes**.
- Contrôle du 30/09 sur le corpus actuel (`tools/mesurer_difficulte.py`) : palier 3 → 0 phrase retirable ; palier 4 → 0 phrase retirable et 0 information interne retirable ; seul résidu de redondance du corpus : les cinq repères d'accompagnement de P2, voulus (ADR-018). Documentation seule — aucun contenu modifié.

## 2026-09-30 · Méthodes de calcul et Garder le cap

- Remplacement des aides génériques des 212 calculs par une stratégie adaptée et une vérification ; panneau unique facultatif « Une méthode possible », sans résultat intermédiaire fourni. Nouveaux identifiants cm3, opérations et réponses conservées.
- Nouvelle carte « Garder le cap » : 12 situations de reprise après interruption, adaptation du plan et contrôle final. Sources primaires et limites documentées ; quatre items par séance, sans chronomètre de réponse.
- Tests de couverture, rendu du panneau, transition entre thèmes et parcours API des trois familles. ADR-020.

## 2026-09-30 · Plans, recherche documentaire et choix en situation

- Méthodes P4 : huit plans entièrement revus, contraintes explicites et une seule étape à déplacer pour rétablir l’ordre.
- Méthodes P5 : huit documents enrichis et visibles avec les questions, sans phase de mémorisation temporisée ; validation et rendu contrôlés.
- Méthodes P2/P3 et Au quotidien P2/P4/P5/P6/P7/P8 : alternatives pertinentes au regard d’une contrainte précise, suppression des formulations caricaturales et des ambiguïtés repérées. P5 quotidien : liens événement-action ; P7 : supports de rappel.
- Remplacement de 96 items : 32 `mt3-…` et 64 `qo2-…`, sans réaffectation des anciens identifiants ni modification des autres familles. ADR-019.

## 2026-09-30 · Libellés fidèles aux tâches

- Au quotidien conservé ; descriptions centrées sur les actions demandées, sans assimiler rappel d’un détail à un entraînement spécifique de mémoire de travail.
- Méthodes devient « Méthodes pour retenir et s’organiser » ; descriptions des 14 paliers des deux thèmes et générateurs synchronisés. Aucun contenu d’item remplacé.
- Revue des 136 items documentée, avec les défauts de contenu restant à traiter, notamment les plans sans erreur nécessaire.

## 2026-09-30 · Méthodes : plan et propositions visibles

- Correction du routage des exercices à choix de Méthodes et Au quotidien, absents de la liste de l’interface : les propositions remplacent le champ libre et le palier 4 affiche son plan numéroté dans l’ordre fourni.
- Contenu et réponses inchangés ; test de rendu des huit plans et contrôle de couverture des types à propositions du corpus.

## 2026-09-30 · Déduction : brouillon explicitement facultatif

- « Tableau de déduction » devient « Aide — noter les possibilités », fermé par défaut à chaque exercice ; explication de son usage facultatif à l’intérieur du panneau.
- Retrait des invitations systématiques à noter/barrer dans les consignes des cinq paliers, dans la méthode de départ de P2 et dans les aides graduées. La grille, les pions et les phrases restent le parcours par défaut.
- Aucun changement des problèmes ou de leurs solutions. Nouveaux identifiants dérivés des textes pédagogiques modifiés ; générateurs mis à jour.

## 2026-09-30 · Aides raisonnées et lisibilité du palier 2

- P2 : 6–8 phrases par grille (moyenne 7,25 contre 9,8), deux repères individuels du même pion reliés par « et », aucun changement de sujet. Sélection d’informations plus utiles, retrait des négations relatives difficiles en fin de palier ; étape 3 sans repères individuels. Les regroupements seuls ne suffisaient pas : ils allongeaient la liste en décomposant les chaînes, d'où cette révision ciblée.
- Entrée de P2 : méthode visible et repère d’accompagnement supplémentaire lorsqu’il permet un premier croisement simple ; aucune phrase ne donne seule une case. Les redondances pédagogiques explicites sont admises et distinguées du noyau de résolution.
- Tous les paliers : bouton « Aide au raisonnement », puis comparaison des possibilités, puis conclusion expliquée. Listes numérotées ; démonstrations calculées depuis les énoncés, sans indices cachés de position. L’unicité et la résolution sans aide restent contrôlées.
- Nouveaux identifiants pour les 100 contenus modifiés (les aides font partie du contenu). Solutions P1/P3/P4/P5 conservées ; P2 régénéré. Les spécificités de progression P3–P5 restent inchangées.

## 2026-09-29 · Déduction : contraintes collectives et cinq paliers (Codex)

- Remplacement explicite des 80 grilles par 100 nouveaux items (identifiants dérivés du contenu), P1–P4 en 3×3 et P5 en 4×4. Graines isolées par palier.
- Répartitions et exclusions de catégories, diversité explicitement annoncée, entre-deux avec références partielles ; aucune règle collective implicite. Suppression des quotas de longueur et des informations dispensables pour la preuve par propagation.
- Trois étapes par palier ; place réservée aux nouveautés malgré les révisions dues. Maîtrise suivie sur les séances comprenant une réponse de dernière étape, sans réutiliser les taux de l'ancien corpus ; palier courant et ancien historique conservés.
- Rendu français des nouveaux indices, correction des phrases mêlant négation et relation positive ; contrôles JS par atome corrigés pour isoler réellement chaque prédicat.
- Contre-vérification indépendante : 100 solutions uniques conformes aux réponses. 237 tests réussis, un test sémantique système ignoré (empreintes absentes) ; 940 items valides ; 890 phrases contrôlées et 19 références de rendu. Régénération identique vérifiée.
- ADR-017 ; contenu à relire, aucune calibration clinique revendiquée. Serveur utilisateur et autre checkout préservés.

## 2026-09-29 · Déduction : le choix de palier part vraiment au serveur (sélecteur d'essai)

Défaut confirmé par Codex : en choisissant « Essai — palier 2 », le frontend démarrait la séance au palier courant (une grille du palier 1 était servie). `demarrerSession` recevait le palier mais POSTait `…/sessions` sans corps — le choix était ignoré.

- **Interface** : le palier choisi part dans le corps JSON (`{"palier": N}`, contrat `DemarrageOptionnel` du serveur) ; le mode **auto** reste sans corps (progression côté serveur, comportement inchangé) ; les réessais (incident réseau ou bandeau) conservent le palier choisi. Version du script incrémentée (`app.js?v=20260929a`).
- **Contrôles** : nouveau `tools/verifier_session.js` — il exécute le **vrai** `demarrerSession` + `apiFetch` de `frontend/src/app.js` sur un `fetch` simulé (pas une copie) : palier 2 → POST avec corps `{"palier": 2}` et `Content-Type` JSON ; auto → aucun corps ; réessai réseau → le palier est conservé. Branché dans la suite de tests (Node requis, sinon contrôle ignoré et signalé). Test d'API dédié au thème : palier 2 forcé → tous les items servis sont du palier 2 ; sans corps → palier 1 sur un état vierge ; palier inconnu → 422.
- **Filtrage serveur revérifié** : `selectionner_items` ne mélange aucun item d'un autre palier.

## 2026-09-29 · Déduction : identifiants dérivés du contenu + aides harmonisées (paliers 2–4)

Deux finitions, après la correction du matin (preuve exacte, palier 3 réparé) :

- **Identifiants du générateur dérivés du contenu.** Les anciens identifiants positionnels (`df-<palier>-<rang>`) étaient réutilisés à contenu changé — reproduction : la graine produisait un `df-1-01` aux énoncés différents du livré. Désormais l'identifiant est une **empreinte sha256 tronquée (12 hex)** du contenu pédagogique canonique (consigne, figures, couleurs, énoncés, indices, aide, réponse ; date, auteur et identifiant exclus) : une re-génération identique garde les identifiants, tout changement en produit un nouveau, une collision d'empreinte échoue bruyamment, et les tests vérifient l'absence de recouvrement avec les identifiants positionnels historiques `df-*`/`dc-*`.
- **Aides harmonisées (47 items, paliers 2–4).** Les 47 derniers items portant « dont la phrase donne la position » passent à l'aide « croisement » — énoncés, solutions, indices et consignes strictement préservés. Identifiants remplacés (dérivés du contenu) ; correspondance complète dans `.cluster/correction-deduction-20260929/mapping_aides_anciens_nouveaux.md`. Le palier 1 garde son texte d'ancrage (initiation, décision documentée). Contrôle de cohérence des aides ajouté au validateur du dépôt et à la suite de tests.
- **Contrôles** : pytest 218 passed ; `validate_items` 0 erreur (920 items) ; Node 687 phrases / 0 anomalie ; générateur : 32 grilles d'essai conformes. Aucun travail sur les redondances dans cette passe (demande explicite).

## 2026-09-29 · Déduction : preuve exacte du « fixe seule » et réparation du palier 3

La détection des phrases qui fixent seules une position était incomplète (propagation à sens unique, sans l'unicité des cases) : elle rendait un faux « zéro phrase solo » au palier 3. Vérification indépendante : **19 phrases fautives dans 13 grilles sur 20** — des chaînes « diagonale + opposé + comparaison » qui fixent deux jetons d'un coup.

- **Preuve exacte** : énumération exhaustive des placements injectifs des seules figures citées (cache, budget borné, erreur explicite si dépassé — jamais de faux zéro) ; propagation binaire complétée (les deux extrémités, unicité, vocabulaire vérifié). « rang de lecture » remplace l'ancien « k » (ordre présenté, pas un minimum) ; « support propagé » est une borne supérieure.
- **Contenu réparé** : les 13 grilles fautives du palier 3 gardent leur solution ; leurs phrases solo sont scindées en deux chaînes de deux informations qui exigent le croisement entre phrases. **Identifiants remplacés** : df-3-03→dc-3-03, df-3-04→dc-3-04, df-3-05→dc-3-05, df-3-07→dc-3-07, df-3-09→dc-3-09, df-3-11→dc-3-11, df-3-12→dc-3-12, df-3-13→dc-3-13, df-3-15→dc-3-15, df-3-16→dc-3-16, df-3-17→dc-3-17, df-3-18→dc-3-18, df-3-20→dc-3-20 — les autres identifiants sont inchangés, les df-3-* remplacés ne seront pas réutilisés.
- **Mesure du 29/09** (outil exact, 80 grilles) : palier 3 — solo 19→0, rang de lecture 1–3→2–4, redondances entre phrases 16→9, redondances internes 229→171. Paliers 2 et 4 : inchangés (zéro solo). Résidus documentés : quatre grilles gardent une phrase retirable (plancher de quatre phrases du validateur) ; palier 4 — redondances mesurées à 122, pré-existantes, hors périmètre de cette correction.
- **Générateur** : types unaires retirés des relations du palier 3 ; plancher de nettoyage à quatre phrases (aligné sur le validateur) ; aide des paliers 2–4 réécrite (croisement, plus « la phrase donne la position ») ; descriptions corrigées (palier 1 non séquentiel, palier 4 sans « moins de phrases »). Essai borné : 32 grilles générées conformes.
- **Tests** : +6 tests indépendants (reproduction df-3-03 cases 0/8, scission inoffensive, propagation inverse et unicité, retrait réel des informations et de l'ancre sans mutation, distinction rang de lecture / support, zéro solo paliers 2–4 par énumération brute). Total : 216 tests. Le rapport de la nuit du 28 (`895efdf`) est dépassé sur le critère C — voir ADR-016.

## 2026-09-27 · Sélecteur de palier (outil d'essai)

Demande : pouvoir choisir le palier pendant la phase de test.

- **Interface** : chaque carte de thème propose un sélecteur « Palier : auto » (défaut) ou « Essai — palier N ». Le choix ne vaut que pour la séance lancée.
- **Serveur** : `POST …/sessions` accepte un corps facultatif `{"palier": N}` ; un palier inexistant répond 422 `palier_inconnu`. Les paliers disponibles sont exposés dans `GET /themes`.
- **Rien ne casse, et c'est vérifié** : le palier est un paramètre de séance (les tests s'en servaient déjà) ; la **progression ne peut pas reculer** — le critère de maîtrise n'avance que vers le haut (`max(palier, session.palier + 1)`) ; les paliers d'essai n'ont donc pas d'effet destructeur, et réussir trois séances d'essai à un palier supérieur fait avancer la progression, ce qui est exact.
- **Effets connus** : la séance ne sert que le palier choisi ; les états de révision des exercices joués sont mis à jour (normal, ce sont de vrais exercices) ; le quota de séances du jour est inchangé ; la cadence du programme est contournée (c'est le but d'un outil d'essai).
- **Retrait facile** : le sélecteur n'est qu'un contrôle d'interface ; le jour où l'essai est fini, le supprimer de la carte de thème suffit (le serveur accepte ou ignore le palier sans effet de bord).
- **Contrôles** — 206 tests (2 nouveaux : palier forcé servi, progression jamais en recul).

## 2026-09-27 · Réponses : articles, pluriel et réponses courtes dans une phrase

Deux demandes d'usage : « un verre » accepté pour « verre » (trouve le mot) ; « devant la gare » ou « on attend devant la gare » acceptés pour « la gare ».

- **Déterminant de tête retiré** avant comparaison : « un verre » = « verre », « la carte de mutuelle » = « carte de mutuelle » (y compris « 1 verre », puisque « un » est aussi le nombre).
- **Pluriel simple toléré** : « des gares » = « gare » (même mot, autre forme) — jamais une différence interne.
- **Réponse courte écrite dans une phrase** : « on attend devant la gare » = « gare » ; « jeudi soir, comme prévu » = « jeudi soir ». Borné : la réponse attendue reste courte (≤ 3 mots), aucun jalon de sens ne doit différer (jour, moment, nombre), et la correspondance se fait sur des mots entiers.
- **Phrase donnée bornée** : la réponse courte est acceptée dans une **petite phrase** (« on attend devant la gare » = « gare »), pas dans un texte entier (douze mots au plus) — le mot ne doit pas pouvoir s'y trouver par hasard.
- **Tolérance de frappe resserrée** : elle ne s'applique plus aux mots de moins de sept lettres. Sur un mot court, une lettre change crée un **autre mot** — « garde » pour « gare » était accepté ; il ne l'est plus.
- Défaut corrigé au passage : la ponctuation collait aux jetons, si bien que « jeudi soir, comme prévu » ne contenait pas le jalon « soir » et était refusé à tort.
- **Précision** : dans « méthodes », l'item qui parle de la gare est un **choix multiple** — la réponse se choisit parmi les propositions (ADR-008). La tolérance ci-dessus s'applique aux réponses **libres**.
- **Contrôles** — 203 tests (3 nouveaux) ; 920 items / 0 erreur.

## 2026-09-27 · Palier « PQRST mis en œuvre » : la méthode appliquée pas à pas

Mise en œuvre des arbitrages validés (4 idées-clés sur 5, champ libre, 5 étapes, textes de 4 phrases du quotidien, fiche récapitulative).

- **Nouveau type d'exercice** `pqrst-mise-en-oeuvre` : un item = **une séquence guidée** sur un texte de quatre phrases — Parcours (jugé), **Question à écrire** (non notée, modèle affiché), Lecture (sans chronomètre), **Reformulation** (jugée à **4 idées-clés sur 5**, résumé modèle), Test (2 questions de mémoire).
- **Nouveau palier 6** du thème méthodes (4 séquences), en **identifiants neufs** (`mt-6-…`) ; programme mis à jour (6 paliers).
- **Correction serveur** par étape : la question écrite n'est pas notée, les idées manquées sont signalées, le test est jugé d'ensemble.
- **Interface** : zone de séquence (les cinq étapes en une page, valider d'un bloc), retour détaillé par étape, et **fiche méthode** reprise au résumé de séance.
- **Contrôle de faisabilité** au dépôt : chaque idée-clé doit se trouver dans le résumé modèle — il a immédiatement attrapé deux résumés incomplets (l'exercice aurait été infaisable).
- **ADR-015** ; README du thème mis à jour ; 920 items / 0 erreur ; 200 tests.

## 2026-09-27 · PQRST mis en œuvre : arbitrages rendus, mise en œuvre planifiée

- **Décisions de l'orthophoniste** : reformulation à **4 idées-clés sur 5**, question personnelle en **champ libre** (modèle affiché ensuite), **5 étapes**, textes de **4 phrases** du quotidien, **fiche méthode récapitulative** en fin de séance.
- Proposition mise à jour (`docs/20-specs/proposition-palier-pqrst-mis-en-oeuvre.md`) ; mise en œuvre planifiée pour la fin de journée.

## 2026-09-27 · Proposition : palier « PQRST mis en œuvre »

- **Constat** : le palier PQRST actuel teste le **résultat** de la méthode (texte masqué → questions de mémoire) sans la faire appliquer ; les deux étapes qui portent l'apprentissage — écrire sa question (Q) et reformuler (S) — sont absentes.
- **Proposition écrite** (`docs/20-specs/proposition-palier-pqrst-mis-en-oeuvre.md`) : une séquence guidée en 5 étapes dans un même item, avec deux productions par texte, un jugement par étape (choix, production libre non notée, idées-clés) et aucun chronomètre sur la lecture.
- **Rien n'est implémenté** : la proposition attend la validation de l'orthophoniste (5 points à trancher : seuil de reformulation, nature de la question personnelle, nombre d'étapes, longueur des textes, fiche méthode de fin de séance).
- Pointeur ajouté dans le README du thème.

## 2026-09-27 · Quand révéler la réponse, et la stratégie visible pendant l'exercice

Deux questions : réponse immédiate ou second essai ? et les exercices de méthode sollicitent-ils assez la stratégie ?

- **Recherche** : errorless learning (Baddeley & Wilson ; Middleton & Schwartz 2012) demande la réponse **tout de suite** après une erreur, là où la personne ne peut pas se corriger seule. À l'inverse, la pratique de récupération (Roediger & Karpicke) et l'**hypothèse de guidage** (Schmidt 1991 ; Winstein & Schmidt 1990) montrent qu'un retour immédiat améliore la séance mais **dégrade la rétention**.
- **Décision (ADR-014)** : jamais de réponse avant un essai ; **récupération → correction immédiate** ; **raisonnement → un second essai** avant la réponse (choisir un plan, formuler une auto-instruction, vérifier un plan). C'est le second essai qui compte comme réponse de l'exercice.
- **Implémenté** : le serveur ouvre un second essai (`essai_supplementaire`) sans révéler la réponse ni rien enregistrer ; l'interface affiche « On reprend — tu peux demander un indice » et laisse l'exercice actif.
- **Stratégie visible** : le panneau « Méthode » affiche désormais **la méthode de l'exercice en cours** (PQRST, GMT, auto-instruction, plan à vérifier, stratégie de lecture) pendant qu'on répond, au lieu d'une consigne lue une fois par séance.
- **Constat confirmé côté contenu** : le palier 1 de « Méthodes » est **PQRST**, dont les questions portent sur la mémoire d'un texte — d'où l'impression justifiée d'un exercice de mémoire.
- **Contrôles** — 195 tests (dont deux sur le régime de feedback).

## 2026-09-26 · Reprise errorless : un exercice manqué revient une fois, avec sa réponse

Demande validée : « ok pour la 2 » — et question du lieu du signalement.

- **Ce qui se passe** : un exercice manqué (et non assisté) est réinséré **en fin de séance**, avec la **réponse fournie avant le nouvel essai** — c'est le complément d'errorless learning (ré-encoder une erreur la renforce). Une reprise par exercice, **quatre au maximum par séance** : la séance ne double pas, et au-delà la répétition espacée ramène le reste le lendemain.
- **Où c'est signalé — dans le fil de l'exercice, pas sur l'accueil** : après une erreur, le retour annonce « Cet exercice reviendra une fois en fin de séance, avec la réponse » ; à la reprise, une note affiche la réponse (« il s'agit de la réancrer, pas de la deviner »). Un avis général sur l'accueil serait abstrait ; l'information utile est celle qui accompagne l'erreur.
- **La note FSRS et le taux de réussite ne changent pas** : c'est la première réponse qui fait foi ; la reprise est un essai supplémentaire.
- **ADR-013** mis à jour (décision 3 et 3 bis) ; version des scripts incrémentée.
- **Contrôles** — 193 tests, dont un garde-fou sur le plafond de reprises.

## 2026-09-26 · Répétition espacée : vérification clinique du choix

Question posée : le passage à une échelle quotidienne est-il pertinent cliniquement ?

- **Oui, et c'est documenté** : la répétition espacée (Ebbinghaus, déjà au socle du projet) et le **Spaced Retrieval** — rappel à intervalles croissants, technique développée en gériatrie et étendue à l'aphasie et au traumatisme crânien (ASHA, 2019) — placent la répétition **dans le temps**, pas dans la minute. Revoir tout un palier dix minutes plus tard était de la pratique massée, l'inverse de ce que ces approches prescrivent.
- **Errorless learning (Baddeley & Wilson ; Evans et al., 2000)** : pour un déficit mnésique, ré-encoder une erreur la renforce — d'où le principe « guider jusqu'à la réussite », déjà appliqué par les indices progressifs.
- **Un point ouvert, noté dans ADR-013** : la littérature d'errorless learning demande qu'une **erreur soit reprise rapidement**, avec la réponse fournie avant le nouvel essai. Le logiciel ne le fait pas encore (la reprise a lieu à la séance suivante). À instruire par l'orthophoniste.
- **Limite honnête** : la fréquence des séances (5-10 min, jusqu'à 3/jour) n'a pas été instruite par ces recherches ; elle reste le cadre propre du projet.
- Documentation : ADR-013 doté d'une section « Base clinique », bibliographie complétée.

## 2026-09-26 · Répétition espacée : fin des mêmes séries qui reviennent le même jour

Signalement : « l'impression de retrouver plusieurs fois la même série dans méthodes et ailleurs ».

- **Diagnostic par les données** : dans *méthodes*, les 12 cartes du palier étaient toutes dues en même temps, avec des échéances à **dix minutes** de leur révision — et le palier compte exactement 12 items pour 12 servis par séance. Chaque séance resservait donc tout le palier.
- **Cause** : les pas d'apprentissage par défaut de FSRS (1 min / 10 min) viennent des applications de révision continue ; ici, le logiciel se pratique en séances quotidiennes.
- **Corrigé** : pas d'apprentissage et de réapprentissage à l'échelle du **jour** — bon → 2 jours, échec → le lendemain, facile → 8 jours ; plus rien n'est dû dans la même journée.
- **Deux garde-fous** : une séance qui n'a rien à proposer ne consomme pas le quota quotidien ; une séance sans réponse n'est pas historisée (aucun recul de palier possible).
- **ADR-013** écrit. Les cartes existantes se réparent d'elles-mêmes (dernière reprise, puis rythme quotidien).
- **Contrôles** — 192 tests, dont un garde-fou « une carte revue aujourd'hui n'est pas due aujourd'hui ».

## 2026-09-26 · Audit de la dictée : du sens partout, sans excès

Demande : vérifier que **tous** les champs libres avec reconnaissance vocale bénéficient d'une reconnaissance de sens, mais pas trop permissive.

- **Deux manques trouvés et corrigés** : les **séquences de chiffres dictées en mots** (« cinq quatre neuf » pour « 549 », « zéro sept un » pour « 071 ») étaient refusées — la dictée écrit volontiers en mots ; et la **dictée était proposée pour le thème Python**, où elle n'a pas de sens (le code vit de son indentation et de ses symboles).
- **Tolérance conservée, bornée** : valeurs (chiffres ↔ mots, symboles d'unité), heures, mots et accents, variantes déclarées, faute de frappe, et reconnaissance de sens (empreintes locales) pour les formulations libres — jamais à travers un jour, un moment ou un nombre, et **jamais sur un choix multiple**.
- **Bornes vérifiées** : un chiffre, un jour, un moment, un montant ou un ordre erroné restent refusés.
- **Audit documenté** dans ADR-008 (tableau champ par champ) et **batterie de tests** `test_reconnaissance_vocale.py` : pour chaque champ, une forme dictée acceptée **et** une réponse fausse refusée.
- **Contrôles** — 916 items / 0 erreur ; 190 tests.

## 2026-09-26 · Périmètre corrigé : la dyscalculie sort du champ du POC

Correction de périmètre, faite le jour même : la dyscalculie (trouble **développemental** du sens du nombre) n'est **pas** dans le périmètre de ce POC, qui vise des troubles cognitifs **acquis** chez l'adulte (post-commotionnels).

- **Palier retiré** : « Sens du nombre » (comparer, situer, décomposer) et ses contrôles, ajoutés quelques minutes plus tôt sur une interprétation erronée. Les paliers suivants sont renumérotés (11 = *Suites et erreurs*, 12 = *Faits à l'envers*).
- **Ce qui reste, et pourquoi** : faits difficiles (× 6 à × 9), suites et erreurs, faits à l'envers — les deux dernières servant la **mémoire de travail**, l'**attention soutenue** et les **lacunes ciblées**, qui sont dans le champ du projet.
- **ADR-012 renommé et annoté** : le périmètre corrigé figure en tête, avec la mention du retrait. Le cadrage « dyscalculie » est explicitement écarté dans le README du thème, pour éviter une nouvelle confusion.
- **Contrôles** — 916 items / 0 erreur ; 164 tests.

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

## 2026-10-06 — Prototype PQRST, accompagnement Apple local

Retour facultatif après correction : deux relances métacognitives maximum, reformulation retravaillable sans modifier le score. Modèle Apple embarqué optionnel, absence ou panne sans blocage, aucun repli cloud. Voir ADR-027.

### PQRST — question personnelle

Le bilan restitue la question du champ 2 et précise « sans score ». La question modèle reste un exemple distinct. La question personnelle est désormais transmise au modèle local avec la reformulation ; une relance peut inviter à vérifier leur lien, sans notation supplémentaire.

### PQRST — suppression de la saisie générique redondante

Le palier de mise en œuvre conserve uniquement ses champs dédiés. La préparation générique ne réaffiche plus « Ta réponse » et sa dictée après le rendu de la séquence.

### Méthodes — ordre des parcours

PQRST guidé pas à pas précède désormais PQRST — répondre de mémoire dans le sélecteur, et devient le choix initial à l’ouverture. Aucun changement des items ni des historiques.

### Sélecteurs — départ Auto explicite

« Auto — suivre ma progression » distingue désormais la reprise du niveau initial indiqué séparément pour une première séance. Le départ Calcul mental (5) provient de l’API. Les parcours à palier unique sont explicitement identifiés.

### Cartes allégées

Retrait du paragraphe explicatif Auto sous les sélecteurs. Le libellé « Auto — suivre ma progression » suffit ; le comportement reste identique.

## 2026-10-07 — Interface discrète

- Accueil et exercices allégés, réglages et résultats détaillés repliés.
- Mode dérogatoire persistant sans bandeau ; paliers et dépassement conditionnés au mode, préférences conservées.
- Boutons spécialisés harmonisés et confirmation de fin sans expiration.
- Aucun contenu ni moteur modifié ; ADR-030.

### Finition audio et fond

- Une commande unique « Écouter », remplacée par un haut-parleur barré pendant la lecture ; taille fixe et nom accessible « Arrêter la lecture ».
- État partagé entre synthèse navigateur, voix locale et fichiers audio ; retour au repos après arrêt, fin ou erreur.
- Éclairage de fond très léger et statique, sans motif ni animation.

## 2026-10-08 — Retrouver le contexte en images

- Remplacement des dix items de mémoire de source du palier 4 par de nouvelles identités illustrées ; messages, options et réponses conservés, autres familles inchangées.
- Dix scènes générées depuis les contextes du contenu, 20 exports WebP responsive de 13 à 112 Ko.
- Révélation par Afficher, phrase de contexte masquée, transcription du message seul ; stimulus retiré avant le rappel.
- Temps de mémorisation déclenché après décodage de l’image, reprise sur erreur de chargement. ADR-035.

### Retrouver le contexte — seconde passe de rappel (2026-10-08)

- Première passe conservée : chaque scène est suivie immédiatement de sa question.
- « Passer au rappel » repose ensuite toutes les questions sans montrer les scènes ; une erreur révèle uniquement la scène correspondante dans la correction.
- Progression Découverte/Rappel, retrait de la correction entre questions, pas de reprise supplémentaire pour ce parcours.
- Même contenu et mêmes images WebP ; API et moteur inchangés. Tests : 5 Node, 50 backend, Chrome mobile sur les deux passes.

### Réglages — rejouer un palier terminé (2026-10-08)

- Case sous « Dépasser la limite de séances », activable en mode dérogatoire et persistante entre visites.
- Dérogation facultative `rejouer_palier` : inclut les exercices déjà faits sans attendre leur échéance, dans le palier choisi et le quota normal ; ni remise à zéro ni levée implicite de la limite de séances.
- ADR-036 ; 49 tests backend ciblés et contrôle Chrome de la persistance/activation conditionnelle.

## 2026-10-08 — Suivi du backlog et revue de la livraison des contextes

Feuille de route remise en cohérence avec main : livraisons identifiées, anciennes orientations retirées du backlog actif, validation de la correction sémantique priorisée (#6). Les prototypes restent spécifiés et non implémentés. Précision sur le résumé des deux passes de contexte, protégé par test ; chemin Linux de synthèse exercé par faux sous-processus en CI. Aucun contenu ni seuil de correction modifié.

### Scènes : le rappel final compte

À la suite de la précision utilisateur, les réponses de découverte servent uniquement à mémoriser et recevoir une correction. Seul le rappel final alimente résumé, FSRS, maîtrise et temps de référence. Un arrêt pendant la découverte affiche « Rappel non commencé ». Contrat additif `memorisation`, ADR-039 ; contenu et identifiants inchangés, anciens historiques conservés sans réinterprétation.
