# Audit clinique indépendant — familles d'exercices de `remediation-cognitive`

**Date** : 2026-09-27 (nuit d'audit, sous-agent 1)
**Portée** : lecture seule. Aucun fichier du dépôt modifié en dehors du présent rapport.
**Population de référence du POC** : adulte de niveau socioculturel élevé, troubles cognitifs **acquis** (post-commotionnels / SPC). Hors périmètre : dyscalculie, troubles développementaux, dispositif médical (POC « hors MDR », `docs/10-clinique/cadre-usage.md`).

**Méthode** : lecture intégrale des documents cliniques (`docs/10-clinique/fondements.md`, `protocoles.md`, `taxonomie-fonctions.md`, `bibliographie.md`, `remediation.md`, `relectures.md`, `cadre-usage.md`), des ADR-004, 005, 007, 008, 011, 012, 013, 014, 015, des README et paliers des 8 familles (`content/entrainement/…`, échantillons d'items JSON), du programme 8 semaines, de `backend/app/domain/feedback.py`, et des missions. Recherche web complémentaire (4 requêtes) pour ancrer les sources citées. **Constat général important : le dépôt ne contient aucune URL de source primaire** (seul le titre ASHA 2019 de Spaced Retrieval est donné avec sa source) ; les citations sont des noms d'auteurs, ce qui rend la vérification indirecte — les ancres web trouvées sont listées en fin de rapport.

**Champs d'analyse par famille** : 1) source primaire/autorité réellement citée dans `docs/10-clinique/` et population visée par cette source ; 2) fonction visée ; 3) stratégie **réellement pratiquée** pendant l'exercice (pas celle annoncée) ; 4) progression (paliers, dosage) ; 5) feedback (immédiat, différé, reprise) ; 6) transfert attendu / limites.

---

## 0. Socle transversal : tolérances de réponse et feedback (ADR-008, ADR-014, ADR-013)

Ces trois ADR structurent le feedback de **toutes** les familles ; ils sont audités en amont.

### ADR-008 (tolérances de réponse) — jugement : solide, avec une réserve de cohérence inter-plateformes

- **Ce qui est fait** : la forme ne fait pas la justesse (casse, accents, heures sous toutes les formes françaises, nombres en lettres, montants en équivalence déterministe, faute de frappe 1–2 selon longueur, mots < 7 lettres exclus de la tolérance de frappe). Le filet sémantique (empreintes Apple Natural Language sur macOS/iPad, repli lexical n-grammes ailleurs, seuil 0,78) ne s'applique qu'aux réponses libres, **jamais** aux choix multiples, et **jamais à travers un jalon de sens** (jour, moment, nombre — mesuré en usage réel : « 14 h 30 » vs « 15 h 30 » à 0,999 de proximité, d'où la règle). Aucun LLM dans la boucle de validation ; chaque tolérance verrouillée par un test.
- **Point de vigilance clinique** : le jugement sémantique d'une même réponse peut **différer selon la plateforme** (moteur Apple vs repli lexical). Le document le reconnaît (repli = portabilité), mais pour un outil qui vise une trajectoire personnelle suivie dans le temps, une correction dépendante du matériel est une variabilité de mesure non maîtrisée. À consigner au minimum.
- **Précaution honnête** : « accepter une réponse fausse est plus grave que refuser une réponse juste » — bornage documenté par des cas d'usage réels, variantes déclarées par item (`reponse.variantes`) privilégiées à l'abaissement du seuil. Bonne discipline.

### ADR-014 (quand révéler la réponse) — jugement : la distinction demandée par la vigilance est **déjà intégrée**, l'extrapolation restante est signalée

- **Ce qui est fait** : séparation explicite entre récupération (correction immédiate, errorless) et raisonnement (second essai avant révélation ; types énumérés dans `backend/app/domain/feedback.py` : `but-etapes`, `auto-instruction`, `plan-a-verifier`). Jamais de réponse avant un essai (protection de l'effet de test). La condition d'indication de l'errorless learning est correctement posée via Ptak : « l'avantage est maximal là où la personne ne peut pas détecter ses erreurs » — c'est exactement la vigilance demandée (errorless **quand la personne ne peut pas se corriger seule**), et l'ADR n'en fait pas une doctrine universelle.
- **Extrapolation documentée mais non prouvée** : l'« hypothèse de guidage » (Schmidt 1991 ; Winstein & Schmidt 1990) et l'effet du retour différé viennent de la **motricité**. Leur extension aux tâches cognitives verbales (choisir un plan, formuler une auto-instruction) est plausible mais non établie expérimentalement dans ce domaine. L'ADR l'utilise comme argument, sans marquer cette limite de domaine — voir § « généralisations douteuses », point G2.
- **Limite assumée en interne** : le palier 1 de « Méthodes » (PQRST) reste un exercice de mémoire où la méthode est **nommée mais non mise en œuvre** (corrigé partiellement par ADR-015, voir famille méthodes).

### ADR-013 (répétition espacée à l'échelle de la séance) — jugement : exemplaire en honnêteté probatoire

- Les pas FSRS à l'échelle du jour (plus de « dû dans l'heure »), reprise **unique** des erreurs en fin de séance **avec la réponse fournie avant le nouvel essai** (complément errorless), plafonnée à 4 par séance, essais assistés non repris, séance vide sans coût.
- La section « Base clinique (vérifiée le 2026-09-26) » **reconnaît explicitement** la pauvreté de la littérature sur ce point précis et sépare ce qui vient des sources (Ebbinghaus, Spaced Retrieval ASHA 2019, errorless) de ce qui est un choix propre du projet (fréquence 5–10 min, ≤ 3 séances/jour : « pas une donnée de la littérature retrouvée ici »). C'est le modèle de transparence que les autres familles devraient suivre.

---

## 1. Calcul mental (`content/entrainement/calcul-mental/`, ADR-011, ADR-012)

**Source citée dans `docs/10-clinique/`** : Kumon (fondements.md : « progression par paliers très fins… 90 % × 3 sessions », « maîtrise fluide »), soroban/abaque mental (mentionné comme piste, **non implémenté**), Sweller (CLT) pour le dosage. **Aucune source primaire** sur la remédiation arithmétique de l'adulte cérébrolésé ; la bibliographie ne cite aucun travail sur la récupération des faits arithmétiques. Population des références implicites : l'éducation (Kumon = enfants/apprenants tout-venant ; littérature des faits arithmétiques = population développementale). **Population cible ≠ population des sources** : extrapolation assumée mais silencieuse.

**Fonction visée** : récupération automatique des faits arithmétiques (libérer la MDT), stratégies de calcul (doubles, compléments), mémoire de travail (palier 7 : deux opérations enchaînées), numératie fonctionnelle (paliers 8–9 : argent, quantités, durées), attention soutenue et inhibition (palier 11 : suites et erreurs).

**Stratégie réellement pratiquée** : la récupération de faits et le calcul direct, avec **aide repliée facultative** qui *nomme* la stratégie (« un presque-double, c'est le double plus un ») mais **ne la fait jamais produire ni vérifier** : rien n'oblige ni ne vérifie que la stratégie a été employée ; un utilisateur peut répondre par comptage effortful sur chaque item sans jamais pratiquer la stratégie, et la mesure (justesse) ne le distingue pas. La stratégie est *disponible*, pas *entraînée*. Le palier 7 porte une consigne de méthode affichée une fois par séance — exposition, pas entraînement.

**Progression** : 12 paliers linéaires (prérequis en chaîne), 212 items, faits utiles ×2–×5 puis ×6–×9 en lacunes ciblées, aucun doublon commutatif, génération déterministe, **contrôle indépendant par recalcul au dépôt** (excellent, avec mesure de sa propre couverture : 92 %). Critère de maîtrise : 90 % × 3 séances. **Lacune** : les protocoles exigent une « maîtrise **fluide** » (c'est le cœur de Kumon : vitesse ET exactitude), mais le critère implémenté ne mesure que la justesse — la fluence n'est pas opérationnalisée dans la décision de passage de palier (le RT est collecté pour la détection de fatigue, pas pour la maîtrise).

**Feedback** : révélation immédiate (tâche de récupération — conforme ADR-014), tolérance numérique ADR-008 (chiffres ↔ mots, symboles), reprise unique en fin de séance (ADR-013), FSRS qui ressert en priorité les faits manqués (palier 10 explicitement appuyé là-dessus). Cohérent de bout en bout.

**Transfert attendu / limites** : les paliers 8–9 construisent le **transfert proche** dans le contenu même (argent, proportions) — c'est la famille entraînement la mieux armée pour la question « à quoi ça me sert demain ». Le mécanisme annoncé (« la récupération automatique libère la mémoire de travail, qui est justement la ressource fragile après une commotion ») est une inférence CLT **plausible mais non démontrée** dans cette population. Limites : aucune preuve que l'automatisation arithmétique réduit la fatigabilité cognitive SPC ; le bénéfice attendu reste la performance dans la tâche et son usage quotidien direct, pas la « réparation » d'une fonction.

---

## 2. Concentration (`content/entrainement/concentration/`, ADR-012)

**Source citée** : famille PASAT « assimilée, protocole non copié » (fondements.md, sprint 2), famille d2 pour le filtrage, hiérarchie attentionnelle Sohlberg & Mateer (fondements, taxonomie — leur programme APT « modèle à s'inspirer sans le copier »). Populations des sources : TBI et populations neurologiques pour l'APT (études APT-II, APT-III existent, dont essais contrôlés et études de cas unique — ancre web trouvée), PASAT issu de la neuropsychologie (MS, TCC). **Population SPC spécifique : non couverte par les sources citées.** Point interne décisif : `remediation.md` (2026-09-24) a **reclassé cette famille comme « Évaluation (mesures) »** — « les familles classiques mobilisées (PASAT, d2, empan, n-back, séries) sont majoritairement des paradigmes d'évaluation, pas de remédiation », plafonnées à une séance/jour.

**Fonction visée** : attention soutenue (chaînes 3→7 opérations, cascade), MDT (maintien du total courant), attention divisée et sélective (double tâche de filtrage), vitesse de manipulation (séries à règle).

**Stratégie réellement pratiquée** : le maintien subvocal d'un total courant et l'addition sérielle sous longueur croissante — une **performance**, pas une stratégie enseignée. L'aide « calcule de gauche à droite, étape par étape » est une consigne générique ; aucune stratégie de regroupement, de chunking ou de vérification n'est enseignée ni pratiquée. En double tâche, aucune stratégie de partage des ressources (priorisation, auto-rythme) n'est proposée — c'est de l'exposition à la charge, pas de l'entraînement stratégique. C'est cohérent avec le nouveau statut « mesure », mais la README du thème parle encore d'« entraînement » dans son titre (résiduel à harmoniser).

**Progression** : 9 paliers, 162 items, montée en charge **dans les items** (3→7 opérations, 5→9 éléments de filtrage) — la fatigue devient mesurable intra-séance (RT et erreurs montent naturellement) : bon design de mesure. Alternance des familles au fil des paliers (chaîne + double tâche + séries) = interleaving de fait, que fondements.md réserve à la phase « entraînement » une fois la phase aiguë passée — **mais aucun critère opérationnel de sortie de phase aiguë n'est défini nulle part** : le principe est posé, sa condition d'application est indéterminée.

**Feedback** : numérique tolérant (ADR-008), immédiat, affichage temporisé exclu de `temps_ms`, détection de fatigue (RT médian + erreurs) qui **propose** l'arrêt, garde-fou 600 s. Aucune reprise spécifique documentée pour ce thème (erreurs reprises via ADR-013 comme ailleurs).

**Transfert attendu / limites** : le dépôt **dit lui-même** la limite (remediation.md) : « s'entraîner à l'empan améliore d'abord l'empan : l'effet test-retest est fort, le transfert vers les activités quotidiennes est faible ». Position interne honnête : cette famille **situe**, elle ne remédie pas. Limite résiduelle : en tant que mesure, elle n'a aucune validation psychométrique (fiabilité, sensibilité au changement) ; les scores ne sont présentés que comme trajectoire personnelle — acceptable pour un POC, à ne jamais présenter autrement.

---

## 3. Déduction (`content/entrainement/deduction/`, ADR-007) — résumé bref (géré ailleurs)

**Source citée** : **aucune** — le logigramme est un genre de puzzle classique, sans ancrage clinique cité dans `docs/10-clinique/` (ni taxonomie ni bibliographie). C'est la seule famille sans référence, même générique. **Fonction** : raisonnement déductif, MDT (maintien des contraintes), inhibition (éliminer), avec brouillon cliquable (tableau ✗/✓) qui **externalise la charge** — mécanisme de compensation correct. **Stratégie réelle** : propagation de contraintes ; la consigne enseigne « note ce qui est certain, barre ce qui devient impossible » (stratégie réellement utile et pratiquée via le tableau) ; 3 phrases de secours sur demande, sans pénalité. **Progression** : 4 paliers (3×3 → 4×4, 4→17 phrases), 20 grilles/palier, 6 grilles/séance max, stock généré par solveur jamais resservi, triple contrôle + relecture du sens des phrases. **Feedback** : correction cases justes/fausses après validation, solution jamais révélée avant validation ; **remarque pour l'équipe en charge** : les grilles de déduction ne figurent pas dans `TYPES_ESSAI_SUPPLEMENTAIRE` de `feedback.py` alors que ADR-014 classe le raisonnement en « second essai » — incohérence mécanique à arbitrer (le retour par cases laisse re-déduire, donc l'esprit est proche, mais la règle n'est pas alignée). **Transfert/limites** : aucune source ne documente le transfert du puzzle déductif vers le raisonnement quotidien ; à considérer comme un jeu de raisonnement structuré, pas comme une remédiation documentée.

---

## 4. Évocation / retrouver le mot (`content/entrainement/evocation/`, ADR-004, paliers SFA/PCA)

**Source citée** : Baddeley & Wilson (errorless learning) et Evans et al. 2000 (*Neuropsychological Rehabilitation*, comparaison errorless vs essai-erreur **chez des patients amnésiques**) ; Spaced Retrieval ASHA 2019 ; PACE (fondements, « adaptable aux troubles pragmatiques légers »). Taxonomie-fonctions.md cite « l'indiçage progressif (sémantique puis phonologique) et la récupération espacée avec estompage des aides » **sans citer les auteurs primaires des hiérarchies d'indiçage ni de SFA/PCA** (Boyle, Leonard, Wambaugh… sont absents de bibliographie.md). **Population des sources : aphasie post-AVC (SFA/PCA), amnésie (errorless)** — extrapolation vers l'anomie SPC (déficit d'accès par fatigue/ralentissement, lésion diffuse) plausible mais non documentée par les sources du dépôt.

**Fonction visée** : accès lexical et récupération ; mémoire de la source (palier 4).

**Stratégie réellement pratiquée** : deux niveaux de réalité très différents. Paliers 1–5 : le comportement réellement entraîné est la **demande d'aide graduée** puis la récupération avec estompage — c'est une stratégie de compensation valide et mesurée (`resume.sans_aide`, `resume.assistees`), l'aide « dis la définition à voix basse » est un vrai auto-indice (paraphrase). Paliers 6–7 (SFA/PCA) : **la stratégie est réellement produite par l'utilisateur** (génère catégorie, usage, lieu / sons, syllabes, rime, puis nomme) — le mécanisme actif des deux méthodes, correctement transposé, avec production non notée (bon choix : on note la génération, pas l'exactitude des attributs).

**Progression** : 7 paliers à prérequis, cran d'entrée par reconnaissance (palier 1), estompage des indices, alternance (palier 5), 50 + 12 items. Volume faible aux paliers 6–7 (6 items chacun) — pour une méthode dont la littérature documente des gains **limités aux mots entraînés** (généralisation aux mots non entraînés contestée), 6 items produiront un effet très restreint, même attendu comme tel.

**Feedback** : le plus soigné du dépôt — clôture sans erreur (la révélation complète est un mode d'interface, jamais un échec ; l'essai assisté est enregistré `correcte=false, assistee=true`, sans faux signal de réussite au moteur), aucun indice ne contient la réponse (contrôle bloquant), tolérance sémantique ADR-008 bornée par jalons, reprise ADR-013. Conforme à l'errorless **pour une population qui ne peut pas se corriger seule** — or un adulte SPC de haut niveau **peut souvent** se corriger (il détecte le mot qui n'est pas le bon) : le choix errorless est sûr (charge affective) mais probablement **au-delà du nécessaire** pour ce profil ; le sujet mériterait d'être posé à l'orthophoniste.

**Transfert attendu / limites** : gains attendus sur les items entraînés (conforme à la littérature SFA) ; aucune promesse de généralisation globale du lexique — le dépôt n'en fait pas, c'est correct. Limite de contenu : le pool lexical (verre, clé, marteau, parapluie…) est de très haute fréquence ; pour le niveau socioculturel visé, le palier 1 (reconnaissance parmi 3 mots) risque le plafond — le dosage protège la fatigue mais pas l'ennui ; la difficulté devrait venir de l'estompage des aides, pas de la rareté (choix défendable, à assumer explicitement).

---

## 5. Mémoire (`content/entrainement/memoire/`, ADR-005 partiellement)

**Source citée** : « familles classiques des techniques d'entraînement cognitif » (fondements, sprint 2), Miyake (updating → n-back), Evans et al. 2000 pour errorless. Le **reclassement documentaire le plus net** du dépôt est ici : `remediation.md` classe explicitement empans/n-back/paires/séries comme **« Évaluation (mesures) »**, séance/jour plafonnée, section interface séparée — la mesure de la thérapie.

**Fonction visée** : mémoire de travail verbale et numérique (empans endroit/envers, empan de mots 3→5), updating (n-back N=2→4), mémorisation longue par paires mot–nombre.

**Stratégie réellement pratiquée** : la **rétention passive et la répétition subvocale** — et rien d'autre. Aucune stratégie de regroupement des chiffres (chunking), aucune imagerie ni phrase-lien pour les paires, aucune instruction de codage sémantique : l'utilisateur de haut niveau improvise ses propres stratégies (et les aurait de toute façon), l'utilisateur fatigué répète. Pour les paires associatives — présentées comme « compétence utile au quotidien (codes, rendez-vous) » — l'absence d'enseignement d'une stratégie de liaison (imagerie, construction de phrase) est le plus grand manque de la famille : la compétence du quotidien repose précisément sur ces stratégies, et c'est elles qui se transfèrent, pas le drill d'appariement.

**Progression** : 12 paliers à prérequis, 216 items, familles entrelacées par palier (empan + paires + n-back), rythme d'affichage borné et **affiché explicitement** (correctif sprint 4 : « un toutes les 0,92 s » — très bon détail d'interface clinique), pools de mots concrets sans doublons, cap 6 chiffres / pas 4 n-back.

**Feedback** : ordre strict sur les empans (l'ordre **est** la tâche — ADR-008), mots dictés acceptés (« zéro sept un »), jamais de chronométrage du rappel (cadre-usage), affichage temporisé hors `temps_ms`, reprise ADR-013. Aucune norme affichée — garde-fou respecté.

**Transfert attendu / limites** : par l'aveu du dépôt, effet test-retest fort, transfert faible — et la littérature des entraînements de MDT (méta-analyses Melby-Lervåg & Hulme) confirme le **transfert proche seulement** ; le dépôt évite prudemment toute promesse de far transfer du n-back (la littérature « brain training » qui la revendique est contestée) — **cette prudence doit rester une règle durable**. En l'état : famille de repérage de trajectoire, pas de remédiation ; son intérêt réel est la **courbe de récupération** et la détection de fatigabilité.

---

## 6. Méthodes (`content/entrainement/methodes/`, ADR-014, ADR-015)

**Source citée** : `remediation.md` « Méthodes implémentées » nomme **PQRST**, **Goal Management Training**, **Auto-instruction (Meichenbaum)** ; la taxonomie et les README les reprennent. **Aucune de ces méthodes n'a sa source primaire dans bibliographie.md** : Levine et al. (GMT, l'étude princeps 2000 et les suivantes chez TCC) absent, Wilson (PQRST en rééducation mnésique) absent, Meichenbaum absent. Le dépôt cite donc les méthodes sans citer leurs preuves — c'est le principal défaut documentaire de la famille. Populations des sources non citées mais connues : TCC pour GMT (le meilleur appui externe de tout le dépôt, justement non cité), enfants TDAH/TCC pour l'auto-instruction, adultes cérébrolésés pour PQRST.

**Fonction visée** : mémorisation de textes (PQRST), planification (GMT), autorégulation (auto-instruction), attention sélective (repérage d'information).

**Stratégie réellement pratiquée** — la famille la plus inégale, mais en voie de correction documentée :
- Palier 1 « PQRST » (12 items) : la méthode est **nommée dans la consigne mais non mise en œuvre** — le texte s'affiche 25 s puis deux questions de mémoire. C'est un test de mémoire avec une étiquette de méthode. ADR-014 le reconnaît explicitement (« la méthode n'est pas mise en œuvre par la personne — elle est seulement nommée ») et l'assume comme mesure du **résultat** de la méthode.
- Palier 6 « PQRST mis en œuvre » (ADR-015, 4 séquences) : **la stratégie est réellement pratiquée** — parcours jugé, **question personnelle écrite** (non notée, modèle montré), lecture sans chronomètre, **reformulation** jugée à 4 idées-clés sur 5, test. Deux productions actives par texte, séquence indivisible, fiche méthode reprise en fin de séance. C'est l'implémentation la plus fidèle du principe « stratégique » de remediation.md, appuyée sur effet de génération et élaboration verbale.
- Paliers 2–4 (GMT, auto-instruction, vérification de plan) : le comportement réel est une **reconnaissance** du bon plan/la bonne question parmi trois — discrimination, pas production. La méthode est affichée en permanence pendant l'exercice (ADR-014 règle 4 : « elle doit rester visible pour être utilisable ») et la première erreur ouvre un **second essai** (`TYPES_ESSAI_SUPPLEMENTAIRE`), le second seul comptant pour la maîtrise — bon design anti-échec. Mais choisir un plan parmi trois n'est pas construire un plan : à ce format, l'écart entre la méthode citée (GMT = entraînement guidé par objectifs avec coaching métacognitif, protocole structuré) et son implémentation (QCM) est maximal. **« L'étiquette n'est pas le protocole. »**

**Progression** : 6 paliers, 44 items + 4 séquences longues (8–12 min pour le palier 6 — dans le cadre). Volume très faible au palier 6 (4 textes écrits à la main), enrichissement coûteux assumé dans l'ADR.

**Feedback** : conforme ADR-014 (second essai sur les types de stratégie, révélation immédiate sur le PQRST de mesure), production non notée (question personnelle) ou jugée sur seuil explicite (4/5, validateur vérifiant que chaque idée-clé figure dans le résumé modèle — défaut réel attrapé, bon signe), panneau méthode permanent.

**Transfert attendu / limites** : GMT a un appui expérimental réel chez TCC (transfert vers la gestion de buts quotidiens), mais il porte sur **son protocole**, pas sur un QCM ; la transposition pourrait gagner beaucoup à un item de type « écris ton plan » (production, comme la question PQRST). Limite franche : 8 items par palier de QCM de plans — risque de plafond rapide chez un adulte de haut niveau, pour qui distinguer le bon plan est trivial ; la difficulté utile serait de **produire** et **vérifier** son propre plan.

---

## 7. Au quotidien (`content/entrainement/quotidien/`)

**Source citée** : `remediation.md` (le cadre de la remédiation : Sohlberg & Mateer, Wilson, Van der Linden, Seron comme tradition) ; la README cite « l'implémentation d'intention » pour le si-alors et « inspiré du Time Pressure Management » pour le palier 8 — **sans citer Gollwitzer (intentions d'implémentation) ni Fasotti (TPM, développé précisément chez TCC)** dans bibliographie.md. Même défaut documentaire que « méthodes » : les concepts sont nommés, leurs preuves absentes.

**Fonction visée** : mémoire de travail (prise de message), planification (étape suivante), anticipation (estimation de durée), initiation (par où commencer), mémoire prospective (si-alors, aide externe), résolution de problème, gestion de la pression temporelle. C'est la famille la plus alignée sur la définition de la remédiation du dépôt (« la fonction altérée dans des situations de vie »).

**Stratégie réellement pratiquée** : la **sélection** de la bonne stratégie parmi trois options (choisir le meilleur si-alors, la meilleure aide externe, la réaction d'urgence adaptée) — pas son **exécution** ni son application à sa propre vie. Les consignes portent réellement la stratégie (« accroche l'action à un moment précis de ta journée », « une bonne aide est au bon endroit, au bon moment, et visible juste avant l'action ») : l'enseignement est présent, la production absente. Le réel est délégué aux missions — qui ne couvrent que l'exposition **sociale**, pas ces stratégies cognitives (aucune mission « installer une aide externe chez soi » ou « construire son plan si-alors du matin »). Concrètement : on sait **reconnaître** qu'« je le prendrai si j'y pense » est un mauvais plan ; rien ne fait écrire « quand je me brosse les dents, je prends le traitement » **pour sa propre journée** — or c'est exactement le mécanisme d'action documenté des intentions d'implémentation (la formation d'un plan précis lié à un repère, pas sa reconnaissance).

**Progression** : 8 paliers fonctionnels à prérequis, 88 items, fourchette d'acceptation pour les durées (bonne tolérance clinique), aucune chronométrée — le refus argumenté des exercices de vitesse (« fatigants, anxiogènes, transfert faible ») et son remplacement par le Time Pressure Management (gérer la demande : simplifier, prioriser) est le choix le plus solide de la famille, cohérent avec la littérature TPM.

**Feedback** : ADR-008 en usage réel le plus sollicité (heures et montants sous toutes leurs formes, jalons stricts — né d'un vrai signalement « vendredi soir » accepté pour « jeudi soir ») ; immédiat ; reprise ADR-013. **Incohérence détectée** : les types de choix de plan du quotidien (`si-alors`, `meilleure-solution`, `aide-externe`, `gestion-du-temps`) **ne figurent pas** dans `TYPES_ESSAI_SUPPLEMENTAIRE` — alors que ADR-014 définit le second essai pour ce qui « se raisonne », et que choisir un plan **est** raisonner selon les termes mêmes de l'ADR. Ces items reçoivent donc une révélation immédiate après première erreur, en contradiction avec la logique ADR-014 (l'exclusion ne tient que pour les trois types de « méthodes »). À aligner ou justifier.

**Transfert attendu / limites** : les sources non citées existent et sont favorables (intentions d'implémentation : fort effet expérimental sur la réalisation d'intentions, y compris cliniques ; TPM : essais chez TCC ; aides externes : socle de la remédiation mnésique) — mais le format QCM entraîne une discrimination, et la phrase du README « c'est la stratégie qui se transfère, pas le score » est **une assertion, pas un dispositif** : rien ne mesure ni ne provoque l'usage hors écran de ces stratégies. La famille gagnerait plus qu'aucune autre à un pont vers des missions personnelles.

---

## 8. Rappel de séries (`content/entrainement/rappel-series/`, ADR-005)

**Source citée** : paradigmes classiques de rappel libre et d'interférence (fondements « familles classiques », sans auteurs primaires — Bousfield/Tulving absents) ; le rappel différé s'appuie sur le principe de l'interférence et du délai, **pas** sur le Spaced Retrieval ASHA 2019 (correctement non revendiqué : SR = rappel d'une cible spécifique à intervalles croissants, chose différente). `remediation.md` la classe en **« Évaluation (mesures) »** (1 séance/jour max), comme mémoire et concentration.

**Fonction visée** : récupération sans indice, mémoire épisodique, résistance à l'interférence entre séries et au délai (20 s).

**Stratégie réellement pratiquée** : le rappel libre brut — l'aide (« note d'abord les mots qui viennent sans effort, puis cherche les autres ») est une heuristique de production légère, pas une stratégie de codage. Aucune stratégie d'élaboration, d'imagerie ou de catégorisation n'est enseignée (il n'y a d'ailleurs pas de structure catégorielle exploitable dans les séries). En l'état c'est cohérent avec son statut de **mesure** : on mesure la récupération sans indice, on ne l'entraîne pas.

**Progression** : 4 paliers (1 série de 4 mots → 3 séries de 3 mots → rappel différé), 32 items, seuils de réussite partielle déclarés par item (0,50–0,75) — la réussite partielle **explicite** (« retrouvés / manquants », jamais un verdict binaire) est le bon traitement clinique de ce paradigme. Invariants validés : aucun mot dupliqué entre séries, rythme borné, délai borné et **passable** (aucune contrainte).

**Feedback** : affichage des mots retrouvés et manquants, aucun score, aucune norme (garde-fou répété : « jamais un score de mémoire »), comparaison tolérante (accents, casse, pluriel simple), rappel différé court (20 s) « n'entraîne la récupération sans indice, ne prétend pas mesurer la mémoire à long terme » — limitation honnête et exacte.

**Transfert attendu / limites** : en tant que mesure non normée, elle sert la trajectoire personnelle et rien d'autre — le dépôt le dit trois fois. Le seul risque généralisation viendrait d'un usage futur « normatif » des seuils (comparer entre personnes) : explicitement interdit dans ADR-005 et taxonomie-fonctions.md ; cette interdiction devra être défendue à chaque itération produit.

---

## Généralisations douteuses (signalements consolidés)

- **G1 — Population : aucune source citée ne porte sur la population cible.** Iverson/McCrory (Berlin) = profil symptomatique, pas efficacité d'intervention ; errorless = amnésie/TBI ; SFA/PCA = aphasie post-AVC ; Kumon/faits arithmétiques/testing effect/interleaving = populations scolaires ; CLT = tout-venant. Aucune n'est invalide pour autant, mais **toutes** les affirmations d'efficacité restent extrapolées pour un adulte SPC de haut niveau. Le dépôt l'assume rarement mot pour mot (ADR-013 est la seule section avec une « base clinique vérifiée » explicite et ses limites).
- **G2 — Feedback : la littérature citée est majoritairement motrice.** Schmidt 1991 (hypothèse de guidage) et Winstein & Schmidt 1990 sont des études de **motricité** ; leur extension au feedback des tâches cognitives (ADR-014 : second essai ; ADR-013 : reprise unique) est plausible mais non démontrée dans le domaine cognitif. L'ADR-014 devrait marquer cette limite de domaine, comme il le fait pour errorless avec Ptak (qu'il cite correctement).
- **G3 — « Maîtrise fluide » non opérationnalisée.** Le critère implémenté (90 % × 3 séances) mesure la justesse, jamais la fluence ; citer Kumon tout en ne mesurant pas le cœur de Kumon (vitesse + exactitude) est une généralisation décorative. Le RT existe déjà dans les données — l'écart est faible entre l'état actuel et une maîtrise réellement fluide.
- **G4 — « C'est la stratégie qui se transfère, pas le score » : assertion sans dispositif.** Dans « quotidien » et « méthodes », la stratégie pratiquée est une **sélection** (QCM) ; l'usage réel d'une stratégie n'est ni provoqué ni mesuré (les missions ne couvrent que le social). Le mécanisme d'action des méthodes citées (écrire son plan, s'auto-instruire, installer son aide) est la **production** — qui n'existe qu'au palier 6 PQRST (ADR-015) et aux paliers SFA/PCA.
- **G5 — L'étiquette n'est pas le protocole.** GMT (Levine), auto-instruction (Meichenbaum), PQRST (Wilson), TPM (Fasotti), intentions d'implémentation (Gollwitzer), SFA/PCA : les implémentations du dépôt sont des **proxys à un seul item ou QCM** de méthodes dont la preuve expérimentale porte sur des protocoles complets, gradés, avec coaching. Citer la méthode importe son autorité sans importer ses conditions.
- **G6 — Le filet sémantique dépend de la plateforme** (empreintes Apple vs repli lexical) : une même réponse peut être acceptée sur iPad et refusée ailleurs ; pour une trajectoire personnelle suivie dans le temps, c'est une variabilité de mesure non maîtrisée (documentée comme limite technique, pas comme risque de mesure).
- **G7 — Interleaving : principe posé, condition jamais définie.** Fondements réserve l'alternance à la phase « entraînement » (phase aiguë = bloquer et simplifier), mais aucun critère de sortie de phase aiguë n'existe dans les documents lus. Le principe s'applique donc toujours ou jamais, selon l'interprétation — indéterminé.
- **G8 — Points correctement tenus (à ne pas dégrader)** : aucune promesse de far transfer du n-back ; aucune norme populationnelle ; scores jamais comparés entre personnes ; résultat partiel jamais un score de mémoire ; dyscalculie et hors-périmètre retirés le jour même (ADR-012) ; relectures orthophonistes toujours « informelles, pas une validation clinique » (`relectures.md` encore vide d'entrées — la relecture formelle est **systématiquement « à faire »** dans les README, c'est la dette documentaire transverse la plus visible).

## Propositions priorisées (hors déduction)

1. **P1 — Opérationnaliser la « maîtrise fluide »** : ajouter au critère 90 % × 3 une condition de fluence (RT médian stable sous un seuil relatif, données déjà collectées). Coût faible, rend Kumon vrai, et la fluence est le meilleur marqueur d'automatisation protège-charge. *(calcul-mental, transversal)*
2. **P2 — Aligner « quotidien » sur ADR-014** : passer `si-alors`, `meilleure-solution`, `aide-externe`, `gestion-du-temps` en types à second essai — ou documenter explicitement pourquoi le raisonnement de choix de plan y échappe à la règle que l'ADR lui-même énonce. *(quotidien)*
3. **P3 — Réparer la chaîne méthode → preuve** : ajouter à `bibliographie.md` les sources primaires des méthodes nommées (Levine et al. pour GMT, Wilson pour PQRST, Meichenbaum, Boyle/Leonard ou Wambaugh pour SFA/PCA, Fasotti et al. pour TPM, Gollwitzer pour les intentions d'implémentation), **avec la population d'origine de chaque preuve**. Sans cela, l'audit de la chaîne de preuve est impossible. *(documentation transverse)*
4. **P4 — Faire produire la stratégie dans « quotidien »** : un item par situation du type « écris ton propre plan si-alors pour aujourd'hui » (non noté, modèle affiché — même logique que la question PQRST de ADR-015). C'est le passage discrimination → génération, et le mécanisme d'action réel des intentions d'implémentation. *(quotidien)*
5. **P5 — Enseigner une stratégie de codage dans « mémoire »** : regroupement des chiffres, imagerie/phrase-lien pour les paires — avec une vérification légère. La famille est reclassée « mesure » : si elle reste entraînement pour quelqu'un, ce sont ces stratégies qui doivent l'être, pas le drill. *(mémoire)*
6. **P6 — Définir un critère de sortie de phase aiguë** (quand l'interleaving s'active, fondements.md) : un critère simple côté produit (ex. maîtrise du palier 1 sur deux thèmes + 2 semaines sans alerte fatigue) suffirait à rendre le principe appliqué et auditable. *(transversal)*
7. **P7 — Consigner la variabilité de correction inter-plateformes** (ADR-008) dans la documentation patient/ortho, et tracer le moteur utilisé dans le résumé de séance. *(transversal, mesure)*
8. **P8 — Étendre `sans_aide` / `assistees` aux familles à aides au-delà de l'évocation** (calcul, quotidien, méthodes) : l'aide réellement utilisée est un meilleur indicateur de remédiation que le taux de réussite brut, et le concept existe déjà dans le moteur. *(transversal)*
9. **P9 — Vider la dette de relecture** : toutes les familles portent `relecture_ortho: a_revoir` et « relecture orthophoniste à faire » ; `relectures.md` n'a aucune entrée. Avant tout élargissement, la relecture informelle des items existants est la priorité de sécurité de contenu. *(transversal)*

---

## Ancres web consultées (4 requêtes, sources prioritaires)

- Middleton & Schwartz (2012), *Errorless Learning in Cognitive Rehabilitation: A Critical Review* — PMC (pmc.ncbi.nlm.nih.gov) : confirme la lecture de ADR-014 (EL indiqué surtout là où la personne ne peut pas détecter ses erreurs ; revue critique, population amnésie/TBI/neurodégénératif).
- Chui et al. (2025), *Errorless Learning for Everyday Functioning in Adults With Acquired Brain Injury* — SAGE : revue récente, appui de l'usage EL en lésion acquise pour le fonctionnement quotidien (population ABI, pas SPC spécifiquement).
- Études APT (APT-II dans MCI, Pantoni et al. 2017 — PMC ; APT-3 en design de cas unique ; chapitre Cambridge sur Sohlberg & Mateer) : la hiérarchie attentionnelle citée existe comme programme documenté, avec des preuves modérées chez TCC — pas de preuve spécifique SPC.
- Cochrane Library : revue « Cognitive training and cognitive rehabilitation for mild to moderate Alzheimer's disease and vascular dementia » (2013) — illustre que les preuves de niveau Cochrane portent sur des populations (démences) différentes de celle du POC ; aucune revue Cochrane dédiée SPC trouvée à ce niveau d'évidence pour ces exercices.

*Note : conformément à la consigne, déduction n'est développée que succinctement (équipe dédiée) ; les 7 autres familles sont couvertes en pleine profondeur.*
