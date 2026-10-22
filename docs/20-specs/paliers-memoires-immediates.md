# Paliers des quatre mémoires immédiates

10 octobre 2026 — implémentation locale après demande utilisateur. Protocole des stimuli `memoires-immediates-v2`, règles `paliers-mi-v1`. Les anciens blocs conservent leur contenu et ne servent pas rétroactivement à la progression.

## Principe et fondement

Augmenter d’abord la quantité à retenir, à règle et cadence constantes. Le rappel inverse, le calcul, les distracteurs et la double tâche changeraient la demande : ils ne sont pas ajoutés pour rendre artificiellement ces parcours plus difficiles. Les modalités et conditions restent séparées.

- Chiffres : [étude sur empans direct/inverse](https://pmc.ncbi.nlm.nih.gov/articles/PMC2978794/), différence entre maintien sériel et manipulation. Les 11–12 chiffres sont un défi de conception, pas une norme ou un seuil de haut potentiel.
- Chemin : [eCorsi](https://pmc.ncbi.nlm.nih.gov/articles/PMC4151195/), plateau de neuf positions et variation de longueur. Notre disposition et nos règles ne constituent pas un Corsi standardisé. Pas de trajet inverse ni de répétitions ajoutées dans cette progression.
- Changement : [étude des liaisons et de la position](https://pmc.ncbi.nlm.nih.gov/articles/PMC1868390/), [Logie et collègues](https://visualcognition.nd.edu/assets/257341/logiebrockmolejaswal_m_c2011.pdf). Quantité et délai sont des dimensions distinctes. Positions conservées, deux identiques/deux différents par bloc, un remplacement ou un échange de deux couleurs selon condition.
- Objets : [What was where](https://pmc.ncbi.nlm.nih.gov/articles/PMC3485137/), charge et délai influencent les erreurs de liaison objet–position. Notre réponse en cases est une adaptation originale, pas une reproduction normée du protocole.

Ces travaux justifient le choix des dimensions ; ils ne valident ni nos seuils de passage, ni un effet thérapeutique, ni l’étiquette « haut potentiel ». Les niveaux supérieurs sont des défis avancés accessibles selon réussite, sans catégorie de personne.

## Échelles livrées

| Parcours | Paliers | Départ | Dimensions conservées |
|---|---|---|---|
| Retenir un code | P1–P7 : 2, 3, 4, 5, 6, 7, 8 chiffres distincts. P8 : 8 avec répétitions non consécutives. P9–P12 : 9, 10, 11, 12 avec répétitions | P3 : 4 chiffres | Rappel direct ; visuel 2 s/chiffre, intervalle 1 s ; audio fin effective de chaque chiffre puis intervalle 1 s |
| Refaire le chemin | P1–P8 : 2 à 9 étapes distinctes | P2 : 3 étapes | Plateau fixe de 9 cases dans toute la progression, 1,5 s/signal et 0,5 s d’intervalle ; ordre direct |
| Qu’est-ce qui a changé ? | P1–P4 : 2, 3, 4, 5 éléments, délai 1,5 s. P5–P7 : 5 éléments, délais 2, 3, 5 s | P2 : 3 éléments | Exposition 5 s, même position, même palette et même règle de changement ; conditions forme/couleur/association séparées |
| Quel objet était où ? | P1–P5 : 2, 3, 4, 5, 6 objets, délai 1 s. P6–P7 : 6 objets, délais 2 puis 3 s | P2 : 3 objets | Exposition 6 s ; mêmes pictogrammes lisibles, objets fournis pour replacer ; pas de rappel libre d’identité |

Les paliers sont des configurations successives ; leur difficulté n’est pas nécessairement strictement croissante. Les effets des répétitions dépendent de leur organisation ([Cowan et Hardman, 2021](https://pubmed.ncbi.nlm.nih.gov/34148530/)).

Code : les répétitions sont annoncées et apparaissent à longueur constante avant toute augmentation suivante. Un même chiffre peut revenir ; pas de répétition immédiatement consécutive. Les zéros initiaux sont conservés. Pas de groupement visuel imposé ni de réduction du temps de réponse.

Objets : jusqu’à quatre, une rangée ; cinq/six, deux rangées de trois emplacements. Ce changement de géométrie est enregistré dans le stimulus et annoncé par le modèle ; il ne survient pas pendant l’exercice. Chaque palier est une configuration différente, sans équivalence psychométrique présumée. Maison et poisson ajoutés comme pictogrammes originaux. Cases et réponses restent de taille confortable sur téléphone.

## Passage et conservation

Progression calculée par le serveur à partir des blocs persistés, indépendante pour code vu/entendu et pour les trois conditions de changement. Un bloc comporte quatre exercices. Une progression automatique ne modifie jamais les paramètres à l’intérieur du bloc.

- Deux blocs admissibles consécutifs avec au moins trois réponses entièrement exactes chacun : monter d’un palier, sans dépasser le plafond.
- Deux blocs admissibles consécutifs avec au plus une réponse entièrement exacte chacun : redescendre d’un palier, sans descendre sous P1.
- Deux réponses exactes : maintien du palier et remise à zéro des deux séries de résultats.
- Un bloc incomplet, aidé ou comportant une interruption n’est pas admissible : aucune montée/descente, aucune durée interprétée. Il n’efface pas la dernière série admissible.
- Changement : une détection « différent » n’est entièrement exacte que si la localisation est exacte ; les rejets corrects restent comptés séparément dans les résultats détaillés.
- Fermeture répétée, retry réseau ou ouverture d’un bloc ne comptent pas comme une nouvelle réussite. L’ouverture simultanée de plusieurs blocs garde des configurations fixes ; Clôtures traitées dans leur ordre durable de fin, avec une révision incrémentée après chaque montée/descente ; un bloc d’une ancienne révision, même revenu au même numéro de palier, n’entraîne pas de promotion en chaîne.

Le seuil de deux blocs à trois sur quatre est une règle de fonctionnement prudente, sans étalonnage clinique. Les paliers persistés survivent au redémarrage via les journaux ; aides, interruptions, résultats historiques et règles FSRS existantes restent séparés. Pas de classement entre personnes ni de score de capacité.

Les réglages numériques dérogatoires actifs suspendent la progression pour ces blocs, qui ne servent pas de référence de palier. La simple activation du mode dérogatoire sans réglage numérique personnel ne la suspend pas. Désactiver le mode reprend la progression normale. Une modalité ou condition changée retrouve son propre niveau.

## Vérification

Tests des blocs complets et passage dans chaque parcours, fermeture idempotente, séparation des modalités, exclusion des aides/interruption, descente après difficulté répétée, génération et correction de tous les paliers sur plusieurs graines. Tests frontaux de masquage, clavier, SVG, dictée, compte à rebours et sauvegarde maintenus. Recette technique à 320 px : six cases et six pictogrammes entièrement contenus dans leurs plateaux/cases. Relecture professionnelle et essai d’usage requis avant de considérer les paliers supérieurs éprouvés en usage.
