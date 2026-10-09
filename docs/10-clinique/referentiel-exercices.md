# Référentiel des compétences cognitives et des exercices

Version 1.5 — 9 octobre 2026. Public : orthophoniste, chercheur, conception produit et développement. Cette version actualise les tâches implémentées : PQRST séquencé et résultats séparés du contexte. Les quatre nouvelles mémoires immédiates restent spécifiées, à développer.

Ce document relie la compétence visée, la tâche proposée, sa justification, les paramètres à spécifier et ce que le logiciel implémente réellement. Il oriente les spécifications ; il ne constitue ni un protocole thérapeutique validé ni une batterie standardisée.

## 1. Lecture et maintenance

Trois statuts d’exercice : **retenu pour spécification**, **implémenté** (éventuellement partiellement), **piste à confirmer**. Une discussion ou une ligne de feuille de route ne suffit pas à déclarer une fonction implémentée. Un exercice peut solliciter plusieurs compétences ; la cible principale est distinguée des contributions secondaires et des facteurs qui peuvent brouiller le résultat.

Deux niveaux de justification : **fondement de la tâche** (ce qu’elle sollicite) et **efficacité de l’entraînement** (ce que des études permettent de conclure). Une tâche étudiée ou un test validé ne valide pas automatiquement notre adaptation logicielle. L’amélioration sur une tâche ne démontre pas un transfert au quotidien ni un bénéfice après commotion.

Quatre exercices sont retenus pour préparer leurs spécifications : Retenir un code, Refaire le chemin, Qu’est-ce qui a changé ? et Quel objet était où ?. Les trois autres pistes complémentaires sont écartées par l’utilisateur le 9 octobre 2026 ; elles ne font pas partie du périmètre à développer. Les compétences hors mémoires immédiates sont inventoriées au §6. Après le signal de l’utilisateur le 9 octobre 2026, les exercices déjà implémentés ont fait l’objet d’une [revue scientifique et de propositions de révision](revue-competences-exercices.md). Le signal a ensuite été donné pour les pistes uniquement prévues : la [recherche préparatoire](recherche-exercices-feuille-de-route.md) examine leurs candidats et sources, sans rédiger les nouvelles spécifications. Les formats d’observation pourront rejoindre « Exercices ciblés », rubrique d’autoévaluation, selon la précision de l’utilisateur.

Sources locales : [catalogue des cartes et parcours](../../backend/app/domain/catalog.py), [chargement du contenu et libellés](../../backend/app/domain/contenu.py), [feuille de route](../00-produit/feuille-de-route.md), [spécification des prototypes](../20-specs/prototypes-epreuves-cognitives.md). Les libellés sont ceux du catalogue au 9 octobre 2026 ; les correspondances cognitives ci-dessous sont des analyses de conception à relire, pas des résultats cliniques.

Les spécifications demandées sont désormais rédigées dans le [cadre cognitif](../20-specs/cadre-exercices-cognitifs.md), les [corrections de l’existant](../20-specs/corrections-exercices-existants.md), les [quatre mémoires immédiates](../20-specs/memoires-immediates.md) et les [fiches candidates](../20-specs/candidats-cognitifs.md). « Spécifié » décrit un document, pas une sélection ou une livraison. Les nouveaux candidats restent **propositions à arbitrer**. [ADR-042](../30-technique/adr/ADR-042-cadre-cognitif-et-autoevaluation.md) et le tableau d’articulation du cadre fixent la portée résiduelle des prototypes, conservés tant que leurs contrats restent utiles.

Pour chaque évolution : garder les identifiants du référentiel, dater le changement, actualiser statut et liens vers code/contenu/tests. Un changement de stimulus ou de protocole conserve sa traçabilité selon les règles de contenu versionné. Les fiches détaillées futures renvoient à ce référentiel plutôt que de recopier leurs justifications.

## 2. Mémoires immédiates : périmètre et distinctions

Définition de travail : maintenir brièvement une information disponible après sa disparition, puis la restituer ou la reconnaître. Le rappel intervient après la présentation, sans activité intercalée dans les variantes de base. La durée exacte est une propriété du protocole, pas un seuil universel définissant une mémoire.

| ID compétence | Dimension principale | Ce que l’on distingue |
|---|---|---|
| MI-VER | Rétention verbale immédiate | Identité de chiffres/mots ; présentation lue ou entendue à tracer séparément |
| MI-ORD | Maintien de l’ordre sériel | Ordre des éléments, distinct de leur identité ; peut concerner plusieurs modalités |
| MI-SPA | Maintien de positions spatiales | Où étaient les positions ; avec ou sans ordre de passage |
| MI-VIS | Maintien de caractéristiques visuelles | Forme, couleur, orientation ou identité visuelle selon la consigne |
| MI-LIA | Maintien des associations | Quel objet avait quelle couleur ou occupait quelle position |
| MI-AUD | Rétention auditive non verbale — hors sélection | Piste sons/rythmes écartée ; aucun exercice ni recherche spécifique prévu dans ce lot |

Ces dimensions se recoupent ; elles ne sont pas présentées comme six systèmes indépendants. L’attention intervient pendant l’encodage et le maintien. Le rappel inverse, le tri et l’actualisation ajoutent une manipulation : ils sont répertoriés dans la **mémoire de travail**, pas assimilés à la seule rétention immédiate. Le rappel de contexte, le rappel différé et la mémoire prospective figurent séparément au §6.

## 3. Exercices retenus pour les spécifications

### EX-MI-001 — Retenir un code

**Compétences :** MI-VER et MI-ORD. **Statut :** principe retenu ; [fiche détaillée rédigée](../20-specs/memoires-immediates.md#ex-mi-001--retenir-un-code). Version visuelle de rappel direct déjà présente dans `memoire/chiffres-endroit` ; présentation fonctionnelle « code » et variante auditive dédiée à développer selon les arbitrages de la fiche. Ce n’est pas une nouvelle carte déjà livrée.

**Déroulement :** départ volontaire → chiffres successifs → retrait complet → restitution immédiate dans le même ordre → validation → correction. Exemple : 4, 7, 2. Une nouvelle série différente est utilisée à l’essai suivant. Aucun calcul, tri ou inversion dans la variante de base.

**Paramètres à figer :** modalité, longueur, durée par chiffre, intervalle, répétitions éventuelles dans la série, mode de réponse, aides et moment de correction. Proposition initiale de confort discutée : 3 chiffres puis augmentation graduelle ; ce n’est pas la valeur automatique actuelle, dont le catalogue annonce un départ à 5 chiffres. Ne pas les confondre. Modalités visuelle et auditive sont deux configurations distinctes ; ne pas ajouter une lecture automatique aux chiffres visuels sans tracer la modalité mixte.

**Observation :** éléments exacts et ordre exact, omissions, substitutions et déplacements. Une erreur de saisie/dictée à vérifier ne doit pas être automatiquement interprétée comme un oubli. La vitesse de frappe n’est pas un score de mémoire. Une aide ou une seconde présentation est tracée.

**Justification :** le rappel sériel direct sollicite le maintien du contenu verbal et de son ordre [R1, R3]. L’étude R1 observe une progression sur des chiffres visuels entraînés mais pas de transfert aux chiffres entendus ou aux lettres visuelles. Cela justifie de séparer les modalités et de limiter les promesses. Un habillage de code quotidien n’établit pas un transfert écologique.

**Implémentation à consulter :** [catalogue](../../backend/app/domain/catalog.py), [items mémoire](../../content/entrainement/memoire/paliers/), [présentation](../../frontend/src/exercises/presentation.js). La version actuelle propose aussi des variantes inverses, à classer en mémoire de travail.

**Critères pour la future spécification :** aucun chiffre accessible après masquage ; correction impossible avant validation ; longueur et rythme indépendants ; aucune inversion implicite ; conserver modalité et aides avec le résultat.

### EX-MI-002 — Refaire le chemin

**Compétences :** MI-SPA et MI-ORD. **Statut :** retenu, [fiche détaillée rédigée](../20-specs/memoires-immediates.md#ex-mi-002--refaire-le-chemin), non implémenté dans les cartes actuelles ; la piste Corsi historiquement hors version 1 des prototypes est reprise dans cette fiche.

**Déroulement :** quelques cases fixes non numérotées → mise en évidence successive de positions → fin des indications → reproduction des positions dans le même ordre → comparaison après validation. La géométrie des cases ne change pas entre présentation et réponse. Une surbrillance stable remplace tout flash.

**Paramètres à figer :** nombre et disposition des cases, longueur du trajet, durée de mise en évidence, pause, positions répétées autorisées ou non, réponse tactile/clavier, annulation de saisie. Proposition initiale : 2 ou 3 positions, puis allongement sans accélération simultanée. Ce sont des choix de conception, pas des normes.

**Observation :** positions rappelées, ordre, omissions et répétitions ; garder à part les erreurs de pointage. La couleur peut signaler momentanément la case active sans devenir une information à mémoriser : une seule indication visuelle stable suffit ici.

**Justification :** adaptation du principe de Corsi ; R2 décrit une version tablette chez 107 adultes et son usage pour la mémoire visuospatiale. Cette étude porte sur la tâche de mesure, pas sur l’efficacité thérapeutique de notre entraînement. Changer la géométrie, le rythme ou la réponse empêche de reprendre ses normes.

**Critères :** pas de trace du trajet après présentation ; réponse dans la disposition initiale ; ordre et position observés séparément ; fonctionnement au clavier ; pas de score normatif importé du test de Corsi.

### EX-MI-003 — Qu’est-ce qui a changé ?

**Compétences :** MI-VIS ; MI-LIA dans la variante forme–couleur. **Statut :** retenu, [fiche détaillée rédigée](../20-specs/memoires-immediates.md#ex-mi-003--quest-ce-qui-a-changé-), non implémenté. La reconstruction de figures prévue dans la feuille de route est une autre tâche et ne constitue pas cette implémentation.

**Déroulement :** composition simple → masquage → seconde composition → réponse « Identique / Différent » → si demandé, localisation de l’élément modifié → validation → comparaison. Inclure des essais réellement identiques. Présentation simultanée, sans ordre de mémorisation imposé.

**Exemple :** cercle, triangle et carré ; après masquage, le triangle devient un losange. Garder les autres caractéristiques fixes pour isoler la modification.

**Variantes retenues dans la discussion :**

| Variante | Information pertinente | Changement autorisé |
|---|---|---|
| Forme | Forme | Une forme ; couleurs et positions conservées |
| Couleur | Couleur | Une couleur ; formes et positions conservées |
| Association forme–couleur | Quel objet porte quelle couleur | Permuter deux couleurs entre objets en conservant les ensembles de formes/couleurs ; évite de résoudre l’essai par la seule présence d’une couleur nouvelle |

La variante association demande sa propre consigne et sa propre version : une permutation affecte deux objets, contrairement aux changements simples. Ne pas mélanger les conditions dans un même indicateur.

**Paramètres proposés à préciser :** départ à 2–3 éléments, progression jusqu’à 5, masquage de 1–2 secondes, exposition confortable, proportion d’essais identiques/différents, magnitude du changement. Aucun de ces réglages n’est un dosage validé. Une différence doit rester perceptible lorsque les deux compositions sont visibles ; sinon la difficulté mélange mémoire et discrimination perceptive.

**Observation :** changements détectés, changements manqués, fausses alertes sur essais identiques et localisation. Distinguer reconnaissance et rappel libre ; ce format ne mesure pas un empan verbal.

**Justification :** R1 rapporte un transfert entre détection de changements de couleur et d’orientation de lignes, dans les conditions de son étude. Cela soutient le choix du paradigme sans valider notre variante avec formes familières ni son efficacité après commotion. R4 étudie le maintien des associations visuelles et sa dépendance à l’attention.

**Couleurs :** elles sont présentes lorsqu’elles font partie du stimulus à retenir ; cette décision de l’utilisateur est conservée. Le décor reste neutre. Versionner palette, contraste, fond et condition. Ne pas ajouter un nom de couleur ou un symbole donnant la réponse à une tâche de mémoire des couleurs. Proposer une activité différente si la discrimination des couleurs est difficile ; ne pas comparer ces variantes comme équivalentes. Pas de saturation criarde, flash ni couleur décorative supplémentaire.

**Critères :** première composition absente du DOM accessible pendant le rappel ; essais sans changement ; seule la dimension annoncée varie ; changements et fausses alertes distingués ; mêmes positions entre compositions ; couleurs fidèles au protocole.

### EX-MI-004 — Quel objet était où ?

**Compétences :** MI-LIA et MI-SPA, avec maintien de l’identité des objets. **Statut :** retenu explicitement par l’utilisateur le 9 octobre 2026 ; [fiche détaillée rédigée](../20-specs/memoires-immediates.md#ex-mi-004--quel-objet-était-où-), non implémenté. Aucun ordre de passage à mémoriser dans la variante de base.

**Déroulement :** départ volontaire → présentation simultanée de quelques objets distincts dans des emplacements fixes → masquage complet → objets fournis dans une réserve distincte → replacement aux emplacements mémorisés → validation → comparaison avec le modèle. Fournir les objets au rappel permet de cibler davantage leurs associations avec les emplacements que la récupération de leurs noms.

**Exemple :** une clé à gauche, une tasse au centre et un livre à droite ; après disparition du modèle, replacer ces trois objets dans les emplacements vides. La réserve de réponse ne doit pas reprendre l’ordre spatial initial ni conserver un indice de position. Aucun emplacement prérempli avant la réponse.

**Paramètres à préciser :** nombre d’objets et d’emplacements, disposition, durée d’exposition, intervalle de masquage, similarité visuelle, emplacement de la réserve et modalités de réponse. Proposition initiale : 2–3 objets familiers très distincts, puis augmentation graduelle du nombre, sans réduire simultanément le temps. Choix de conception à ajuster, pas norme ni dosage clinique.

**Couleurs :** elles peuvent aider à distinguer les objets sans être une réponse à mémoriser. Dans la variante de base, conserver leur apparence entre présentation et rappel ; ne pas ajouter une association couleur–emplacement indépendante. Une future variante où la couleur devient pertinente exige une consigne et une version distinctes. Le décor reste neutre.

**Observation :** associations objet–emplacement exactes, permutations, omissions et placements supplémentaires. Distinguer erreur de pointage et association erronée. Ne pas produire un score global de mémoire à partir du seul résultat. Les objets étant fournis, la tâche ne démontre pas un rappel libre de leur identité.

**Justification :** choix de conception pour solliciter le maintien d’associations objet–position. R4 fournit un fondement général sur les associations de caractéristiques visuelles, sans démonstration d’efficacité de cette adaptation. La recherche initiale n’était pas spécifique à l’objet–position. La [recherche complémentaire autorisée](recherche-exercices-feuille-de-route.md) ne permet pas encore de conclure à une efficacité clinique de cette adaptation.

**Critères pour la future spécification :** modèle inaccessible pendant la réponse ; objets fournis sans indice de leur position initiale ; emplacement stable et réponse possible au clavier ; possibilité de déplacer/annuler avant validation ; correction uniquement après validation ; aucune réponse imposée par la couleur du décor.

## 4. Pistes écartées

Décision utilisateur du 9 octobre 2026. Identifiants conservés pour la traçabilité ; aucun développement, spécification détaillée ou enrichissement bibliographique prévu pour ces pistes dans le lot actuel.

| ID | Piste | Décision |
|---|---|---|
| EX-MI-005 | Quels objets étaient présents ? | Écartée |
| EX-MI-006 | Remettre les éléments fournis dans leur ordre d’apparition | Écartée |
| EX-MI-007 | Reproduire une courte succession de sons ou un rythme | Écartée |

Les associations forme–couleur relèvent déjà d’EX-MI-003 ; ne pas créer une fiche concurrente pour le même protocole. Les associations mot–nombre existantes sont inventoriées au §5, sans les assimiler à un exercice objet–position.

## 5. Aperçu du logiciel existant lié à la mémoire

| Carte/parcours réel | Ce qui est implémenté | Place dans le référentiel |
|---|---|---|
| Retenir et manipuler / Chiffres dans l’ordre | Empans directs de 3 à 6 chiffres ; départ automatique à 5 | MI-VER + MI-ORD ; base partielle d’EX-MI-001 |
| Retenir et manipuler / Chiffres en ordre inverse | Restitution inverse de chiffres | Mémoire de travail : maintien + manipulation |
| Retenir et manipuler / Mots — ordre et ordre inverse | Mots concrets, ordre direct et inverse | Rétention verbale/ordre pour direct ; manipulation pour inverse ; conditions à distinguer |
| Retenir et manipuler / Associations mot–nombre | Mémorisation puis rappel d’une association | Maintien associatif ; protocole et délai à préciser avant attribution à une seule mémoire |
| Retenir et manipuler / Position dans une séquence | Retrouver un élément plusieurs positions avant la fin | Maintien sériel/actualisation ; ne pas supposer un n-back continu classique d’après le seul type interne `n-back` |
| Mémoriser des séries / Rappel immédiat, mots lus ou entendus | Une à trois séries puis rappel libre | Rétention/récupération verbale avec interférence possible ; rappeler plusieurs séries n’isole pas une seule compétence |
| Mémoriser des séries / Rappel différé, sélectionner la première série | Délai de 20 s et variantes de sélection | Rappel différé et sélection, distincts de la base immédiate |
| Retrouver des mots et leur contexte / Retrouver le contexte | Dix scènes avec messages ; photo puis question, ensuite rappel sans photo ; scène révélée après erreur au rappel | Mémoire de source/contexte et récupération ; la seconde passe ne constitue pas une mesure pure de mémoire immédiate |
| Actualiser une consigne | Remplacement d’informations et application de la consigne actuelle | Mémoire de travail + inhibition ; pas simple stockage |

Pour le contexte illustré, [ADR-035](../30-technique/adr/ADR-035-scenes-memoire-source.md) décrit les scènes et les deux passes. Depuis le 9 octobre 2026, [ADR-044](../30-technique/adr/ADR-044-observations-contextes-et-persistance.md) ajoute un journal durable et des résultats descriptifs séparés : après photo et sans photo, premières réponses et photos revues après erreur. Il ne constitue pas une mesure pure de mémoire immédiate. PQRST est désormais séquencé et masqué, avec test après résumé modèle ([ADR-043](../30-technique/adr/ADR-043-pqrst-sequence-et-observations.md)) ; ses anciens résultats ne sont pas requalifiés.

Les métadonnées existantes `fonctions_ciblees` sont des intentions éditoriales ; elles ne prouvent ni spécificité ni efficacité. Le document historique [taxonomie](taxonomie-fonctions.md) range certains empans directs dans « mémoire de travail » : le présent référentiel affine la distinction maintien/manipulation sans modifier les items ou leurs historiques.

## 6. Autres compétences : inventaire et suivi de la revue

Inventaire initial du dépôt ci-dessous, conservé pour la traçabilité. La [revue du 9 octobre 2026](revue-competences-exercices.md#3-révision-des-compétences-annoncées) précise désormais les compétences défendables des exercices implémentés, les sources Consensus et les révisions proposées ; elle prévaut pour leur interprétation. Le signal a ensuite été donné : la [recherche sur les pistes de la feuille de route](recherche-exercices-feuille-de-route.md) précise les candidats, sources et réserves. La sélection des nouvelles tâches reste à décider. « Sollicité » décrit le contenu, pas une compétence mesurée indépendamment. Les priorités de développement restent à décider.

| ID famille | Compétence à documenter | Cartes/parcours actuellement concernés | Autres pistes de la feuille de route / spécification | Travail futur de justification |
|---|---|---|---|---|
| CT-MDT | Mémoire de travail : manipulation, actualisation | Retenir et manipuler (inverse, position), Actualiser une consigne, prise de message, Déduction | N-back visuel/auditif hors V1 | Distinguer maintien, manipulation, mise à jour, charge exécutive et n-back classique |
| CT-MEM | Apprentissage, récupération, mémoire épisodique et de source | Séries différées, Retrouver le contexte, PQRST, associations mot–nombre | Reconstruction de figures | Séparer rappel immédiat/différé, reconnaissance/rappel et source/contenu ; transfert des stratégies |
| CT-PRO | Mémoire prospective et compensation | Au quotidien : aide externe, si–alors ; missions et carnet | Pas de prototype dédié livré | Distinguer choix d’une stratégie et exécution réelle d’une intention future |
| CT-LEX | Accès lexical, connaissances sémantiques, stratégies phonologiques | Retrouver le mot, SFA, PCA ; anglais en Extra | Pas de nouveau prototype acté | Contribution du vocabulaire, indices, reconnaissance/production et généralisation |
| CT-ASE | Attention sélective, recherche et sélection d’information | Repérer l’essentiel, Comparer deux documents, Chercher dans un document | Recherche visuelle avec distracteurs hors V1 | Discrimination perceptive, compréhension et sélection ; préciser ce qui est ciblé |
| CT-ASO | Attention soutenue et maintien du but | Garder le cap, tâche commencée puis reprise ; certaines séries | Attention différée spécifiée ; attention soutenue dans plan historique | Ne pas qualifier une tâche courte de mesure pure d’attention soutenue ; dissocier mémoire et connaissances |
| CT-ADI | Attention alternée/divisée, gestion de deux activités | Reprise après interruption = reprise réelle, pas preuve d’une double tâche simultanée | Double tâche hors V1 ; ancienne batterie soutenue/divisée | Distinguer alternance, interruption et concurrence simultanée ; charge et confort |
| CT-INH | Inhibition et résistance à l’interférence | Actualiser une consigne, Repérer l’essentiel | Séries de couleurs : lecture, dénomination, interférence spécifiées | Dissocier lecture/dénomination/perception, inhibition et vitesse ; comparaisons de conditions |
| CT-FLE | Flexibilité et adaptation d’un plan | Garder le cap / Adapter un plan ; calcul mental : cible déclarée | Trail Making dans taxonomie historique, non décision actuelle | Changement de règle, alternance et adaptation fonctionnelle ; statut de l’ancienne piste à confirmer |
| CT-PLA | Planification, séquençage et anticipation | Au quotidien, Choisir un plan, Vérifier un plan, Garder le cap | Pas de nouvelle tâche de planification autorisée | Stratégie reconnue en QCM vs plan effectivement produit/exécuté |
| CT-META | Métacognition, auto-instruction, contrôle et vérification | Méthodes, Vérifier avant de terminer, missions/carnet | Suivi personnel et familiarisation des prototypes | Stratégie enseignée vs utilisée ; observation du transfert hors écran sans score d’observance |
| CT-TEM | Gestion du temps et estimation | Au quotidien : estimation et gestion du temps | Vitesse de traitement dans plan historique, chrono des couleurs | Distinguer estimation de durée, vitesse perceptive, vitesse de réponse et latence technique |
| CT-RAI | Raisonnement, déduction et compréhension de contraintes | Déduction, Comparer deux documents ; Python : prédiction de sortie | Pas de nouveau prototype acté | Contributions de mémoire, compréhension, connaissances et raisonnement |
| CT-VCO | Perception et construction visuospatiales | Grilles de Déduction (placement), sans exercice dédié de construction mnésique | Reproduction/reconstruction de figures spécifiée, Corsi hors V1 | Séparer mémoire visuelle, analyse spatiale, construction, motricité et dispositif |
| CT-CON | Connaissances et automatismes appris | Calcul mental, anglais, Python | Culture générale dans attention différée | Domaines appris et automatismes, distincts d’une fonction cognitive générale ; rôle des connaissances préalables |

Les couleurs de la spécification des prototypes servent à la lecture, la dénomination et l’interférence ; elles ne constituent pas encore l’exercice de mémoire des couleurs EX-MI-003. Le rapprochement thématique ne doit pas fusionner ces protocoles.

Les phases historiques « bilan », normes et IRT sont signalées dans la feuille de route comme non réactivées. Leur présence dans un ancien tableau n’autorise pas leur développement. Ce référentiel décrit les compétences et les tâches ; il ne réintroduit aucune batterie diagnostique.

## 7. Gabarit obligatoire pour les fiches et spécifications suivantes

1. ID stable d’exercice, compétence principale, contributions secondaires, objectif fonctionnel éventuel.
2. Statut : discussion, retenu, spécifié, implémenté ; version et liens code/contenu/tests ; état de relecture séparé.
3. Déroulement exact : encodage, disparition, maintien/délai, réponse, aide et correction.
4. Stimulus et dimensions pertinentes ; facteurs maintenus constants et changements permis ; graines et versions.
5. Modalités et réponse : vue/entendue/mixte, reconnaissance/rappel, ordre imposé ou non, dispositif.
6. Progression : quantité, complexité, temps et aides réglés séparément ; valeurs proposées distinguées des normes.
7. Observations : erreurs spécifiques, réponses partielles, incertitudes techniques/perceptives ; limites d’interprétation.
8. Fondement bibliographique : population, tâche, résultat et portée ; distinguer preuve directe et extrapolation de conception.
9. Confort/accessibilité : départ volontaire, charge visuelle/auditive, pause/sortie, alternative qui change éventuellement la tâche.
10. Critères d’acceptation et de vérification ; données réellement enregistrées ; aucun indicateur promis mais non implémenté.

Pour le public fatigable : une consigne et une tâche à la fois, décor sobre, pas de flash ni pression sur la vitesse de réponse par défaut. Les couleurs pertinentes sont conservées ; la sobriété ne supprime pas une caractéristique que l’exercice demande de retenir. Les paramètres discutés (par exemple quatre essais) sont des points de départ de conception, pas des prescriptions.

## 8. Références déjà consultées via Consensus

Cette section conserve les publications examinées pour la première version sur les mémoires immédiates. Les nouvelles recherches autorisées sur les exercices implémentés figurent dans la [revue scientifique, §5](revue-competences-exercices.md#5-sources-consultées-dans-consensus-et-portée). Les descriptions ci-dessous rendent explicite leur portée ; leur présence ne vaut pas validation clinique du logiciel.

- **R1 — Norris, Hall et Gathercole (2019), Memory & Cognition.** [Can short-term memory be trained?](https://consensus.app/papers/can-shortterm-memory-be-trained-norris-hall/bc06c28909e553dfa51730e0a8d78b41/?utm_source=chatgpt). Entraînement adaptatif sur 20 sessions : progrès sur chiffres visuels sans transfert aux chiffres entendus/lettres visuelles ; transfert entre deux tâches proches de mémoire visuelle. Pas de démonstration spécifique de nos variantes chez des adultes avec SPC.
- **R2 — Brunetti, Del Gatto et Delogu (2014), Frontiers in Psychology.** [eCorsi: implementation and testing of the Corsi block-tapping task for digital tablets](https://consensus.app/papers/ecorsi-implementation-and-testing-of-the-corsi-brunetti-gatto/949d1bba1c2457e9bc44dd4cfa56ef0f/?utm_source=chatgpt). Étude de tâche sur tablette chez 107 participants (18–30 ans et plus de 50 ans). Justification du format spatial ; ne démontre pas l’efficacité d’un programme de rééducation.
- **R3 — Hurlstone, Hitch et Baddeley (2014), Psychological Bulletin.** [Memory for serial order across domains](https://consensus.app/papers/memory-for-serial-order-across-domains-an-overview-of-the-hurlstone-hitch/7c582107ff015306b0af386750b0d54e/?utm_source=chatgpt). Revue des phénomènes d’ordre sériel verbal, visuel et spatial ; cadre de distinction entre contenu et ordre, sans validation de nos exercices.
- **R4 — Wheeler et Treisman (2002), Journal of Experimental Psychology: General.** [Binding in short-term visual memory](https://consensus.app/papers/binding-in-shortterm-visual-memory-wheeler-treisman/1585e2063e495b958a6dd46b154f9b47/?utm_source=chatgpt). Expériences de détection de changements forme/couleur/position ; rôle de l’attention dans les associations et vulnérabilité à l’interférence. Fondement de MI-LIA, pas preuve d’efficacité thérapeutique.
- **R5 — Fernández López et Antolí (2020), PLoS ONE.** [Computer-based cognitive interventions in acquired brain injury](https://consensus.app/papers/computerbased-cognitive-interventions-in-acquired-brain-lópez-antolí/a7dae02b13755d458dfbe088c8f54097/?utm_source=chatgpt). Revue/méta-analyse de huit essais randomisés : effets rapportés sur mémoire de travail verbale et visuelle, pas sur les autres domaines étudiés. Résultats de programmes hétérogènes, pas preuve pour chacun de nos exercices ni pour le SPC en particulier.

Référence complémentaire déjà examinée, sans nouvelle recherche : Norris, Kalm et Hall (2019 selon la fiche Consensus ; volume 46 de la revue), [Chunking and Redintegration in Verbal Short-Term Memory](https://consensus.app/papers/chunking-and-redintegration-in-verbal-shortterm-memory-norris-kalm/40afc0e4c6c5577fa9a7f96d4ae497e4/?utm_source=chatgpt). Six expériences sur regroupement verbal ; peut orienter une variante stratégique future. L’année d’édition finale devra être vérifiée avant une bibliographie de publication.

État de relecture de ce référentiel : **à relire par l’orthophoniste ou le chercheur**, sans prétendre à une validation déjà obtenue. Toute nouvelle recherche, correction de classification ou décision de développement est ajoutée avec date et provenance.
