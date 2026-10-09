# Les quatre exercices de mémoire immédiate retenus

Version 1.1 — 9 octobre 2026. Relecture de cohérence documentaire effectuée ; relecture clinique et essai d’usage restent à réaliser. **Principes retenus par l’utilisateur ; spécifications proposées, non livrées.**

Le [référentiel](../10-clinique/referentiel-exercices.md#3-exercices-retenus-pour-les-spécifications) définit les compétences et les quatre IDs conservés. Le [cadre commun](cadre-exercices-cognitifs.md) s’applique : départ volontaire, masquage réel, interruption, aides, données minimales et comparabilité. Les [références R1–R4](../10-clinique/referentiel-exercices.md#8-références-déjà-consultées-via-consensus) sont réutilisées ; aucune nouvelle validation clinique n’est revendiquée.

## Règles communes de ce lot

**Usage proposé à arbitrer :** pratique en parcours d’entraînement, avec stratégie/démonstration facultative puis essais nouveaux ; version d’observation dans Exercices ciblés avec paramètres fixes et exemples distincts. Les résultats des deux usages sont séparés. La pratique porte sur le maintien/rappel ou la reconnaissance dans la tâche ; aucun transfert au quotidien n’est promis par l’habillage.

Défaut de départ proposé : un exemple corrigé puis un bloc de quatre essais, chaque essai lancé volontairement, possibilité de terminer après chacun. Ce nombre organise l’interface ; il n’est ni un minimum de dose ni un seuil d’interprétation. La personne peut poursuivre ou s’arrêter ; aucun objectif de complétion. Pour l’observation, la correction détaillée vient après le bloc ; en entraînement, après chaque réponse validée. Toute exposition corrective susceptible d’influencer l’essai suivant est connue, et les stimuli suivants sont nouveaux.

Les réglages chiffrés ci-dessous sont des propositions de conception à essayer, non des normes. Longueur/quantité, exposition, similarité, aides et modalité sont indépendantes. Aucune adaptation automatique nouvelle en V1. Les réglages de confort sont persistants ; les overrides restent dans le mode dérogatoire. La consigne audio avant départ ne rend pas le stimulus auditif. En revanche, une lecture des éléments à mémoriser change la modalité.

Pendant l’encodage et le maintien, une pause ou sortie invalide la continuité de l’essai ; sa reprise est un nouvel essai lié avec autre stimulus. Le délai réel entre disparition et disponibilité de la réponse est conservé ; la latence de première action reste distincte, selon le cadre. Pour EX-MI-003, conserver également l’apparition de la seconde composition : elle met fin au masque sans être le début de la réponse. La durée de saisie n’est jamais un score de mémoire. Une demande de revoir/réécouter ouvre un essai assisté après verrouillage de la première réponse ou absence déclarée ; jamais de correction avant la validation.

## EX-MI-001 — Retenir un code

**Compétences et statut.** MI-VER et MI-ORD ; attention d’encodage et familiarité numérique contribuent. Base visuelle directe existante `memoire/chiffres-endroit`, 3 à 6 chiffres, départ Auto actuel à 5 selon [catalog.py](../../backend/app/domain/catalog.py). La présentation fonctionnelle « code », son départ proposé à 3 et une version auditive dédiée sont **à développer** ; ces valeurs ne décrivent pas le logiciel courant. Aucun rappel inverse ou calcul dans cette variante.

**But et consigne.** « Retenez ce code. Quand il aura disparu, entrez les chiffres dans le même ordre. » L’entraînement peut proposer avant un exemple une répétition mentale ou un regroupement choisi, sans montrer de groupement pendant un essai dit sans aide. L’autoévaluation garde la stratégie libre, avec déclaration facultative, sans nouveau conseil en cours de bloc.

**Stimuli proposés.** Suite originale de trois chiffres entre 0 et 9, sans répétition dans le profil initial ; conserver les zéros initiaux. Génération isolée EX-MI-001, graine/ID et suite attendue versionnés. Présentation visuelle d’un chiffre centré à la fois, 2 s puis 1 s de blanc entre chiffres ; après dernier chiffre, masquage puis champ de réponse, sans délai additionnel intentionnel. En auditif, chaque chiffre prononcé une fois par voix française locale ; intervalle proposé 1 s après fin effective du chiffre, aucune forme écrite de la suite. Les deux rythmes ne sont pas supposés équivalents.

**Phases et réponse.** Consigne/exemple → prêt → suite → masque → saisie texte de chiffres → validation → correction au moment prévu. Champ texte numérique, pas nombre entier, pour conserver « 047 » ; séparation par espaces/tirets tolérée. La dictée est une modalité de réponse distincte nécessitant vérification ; défaut proposé clavier/clavier visuel stable. Retour arrière avant validation autorisé. « Je ne sais pas » distinct d’une réponse vide non validée.

**Aides et correction.** Montrer le code et la réponse après validation ; souligner sobrement les positions différentes avec texte, sans rouge/vert obligatoire. Une nouvelle présentation est assistée et datée. Ne pas faire jouer automatiquement la correction sonore avant le moment prévu. En entraînement, un nouvel essai avec un nouveau code permet de réutiliser la stratégie.

**Observations.** Exactitude de la suite entière et positions exactes sur longueur présentée ; contenu retrouvé indépendamment de l’ordre par correspondance d’occurrences. Une suite plus courte montre des éléments manquants, mais l’alignement peut être ambigu : ne pas imposer un diagnostic de substitution/transposition. Pour 4–7–2 → 7–4–2, contenu intégral retrouvé, une position exacte, ordre différent. Pour profils avec chiffres répétés, compter les occurrences, sans réutiliser un seul chiffre de réponse pour plusieurs attendus.

**Progression/confort.** Augmenter longueur de 3 à 4 puis plus séparément ; répétitions dans la suite = variante signalée ; rythme constant par défaut. Une taille de caractère accrue reste possible sans changement de contenu. Variante auditive préparée et vérifiée avant départ ; audio indisponible = choix explicite d’un autre essai, pas repli visuel silencieux.

**Données nécessaires.** ID/suite attendue via banque, modalité et voix si auditive, longueur/rythme effectifs, suite validée, aide/réexposition, temps de présentation et délai de rappel, état de transcription éventuel. Pas de conservation d’audio par défaut ; pas de journal de frappe.

**Fondement et limites.** R3 : ordre sériel interdomaines, fondement de tâche. R1 : progression sur chiffres visuels entraînés sans transfert aux chiffres entendus/lettres visuelles dans l’étude ; aucune efficacité SPC de ce code web établie. R1 n’impose pas son nombre de séances. Comparer direct/inverse ou lu/entendu comme une même mesure est exclu.

**Acceptation P0.** Code « 047 » conservé et corrigé comme trois chiffres ; exemple 4–7–2 ci-dessus produit les comptes attendus ; aucun chiffre accessible après masque ; aucune comparaison avec anciens essais dont modalité/aides manquent ; rythme et longueur réglables séparément ; retour arrière ne crée pas de réponses supplémentaires ; répétition assistée ne remplace pas l’essai initial.

## EX-MI-002 — Refaire le chemin

**Compétences et statut.** MI-SPA et MI-ORD ; perception et précision du pointage contribuent. **Non implémenté** ; idée Corsi anciennement hors V1 des prototypes, désormais principe retenu pour cette spécification. Aucun empan clinique calculé.

**But/consigne.** « Regardez les cases indiquées. Reprenez le même chemin, dans le même ordre. » Pratique possible d’un repérage spatial ou d’une répétition mentale ; ne pas demander de réciter des numéros. Aucun numéro affiché dans les cases.

**Stimuli proposés.** Six cases fixes dans une géométrie irrégulière simple, coordonnées normalisées et versionnées ; trajet initial de trois positions distinctes. Chaque case active reçoit un contour stable et une légère différence de surface pendant 1,5 s, suivie de 0,5 s sans indication. Une seule case active ; pas de flash ni trace cumulée. La dernière indication disparaît avant activation de la réponse. La disposition et les dimensions restent identiques dans l’essai ; un changement de géométrie est une autre configuration.

**Phases/réponse.** Prévisualisation des cases neutres → prêt → indications successives → toutes neutres → sélection du trajet → validation. Clic/toucher ; clavier : déplacement de focus prévisible entre cases et activation, avec alternative de sélection directe présentée pendant l’exemple. Les noms accessibles de positions identifient les commandes sans annoncer leur ordre correct. Les positions sélectionnées peuvent porter un repère discret d’ordre **de la réponse actuelle** ; jamais un indice de la solution. Annuler le dernier choix et recommencer la saisie sont disponibles avant validation.

**Aides/correction.** Démonstration préalable ; revoir le trajet pendant l’essai exige une nouvelle tentative assistée. Après validation, comparer séquence attendue et reproduite à un rythme choisi, avec possibilité d’arrêter la lecture visuelle. Un retour sur la réponse n’ajoute pas une animation décorative.

**Observations.** Trajet complet exact, positions exactes au rang demandé, positions retrouvées sans ordre si l’alignement est certain, omissions et répétitions. Pointer une mauvaise case puis annuler avant validation reste une correction de saisie, pas automatiquement un oubli. Les réponses avec même ensemble de cases et autre ordre ne sont pas des succès complets.

**Progression/confort.** Deux positions comme profil simplifié, trois au départ proposé, puis quatre ; rythme constant. Nombre de cases, longueur et répétitions dans le trajet sont trois dimensions séparées. Répétitions non consécutives envisageables en P1, avec explication explicite ; éviter les répétitions consécutives avant définition d’un signal stable les rendant discernables. Modifier taille/géométrie pour confort crée une configuration distincte, sans déplacer les cases pendant l’essai.

**Données/fondement.** Disposition versionnée, trajet, durées réalisées, séquence de réponse finale, annulations uniquement si nécessaires au dépannage, aides et modalité de pointage. R2 : eCorsi sur tablette, 107 adultes, appui au format spatial ; ni normes importées ni preuve thérapeutique de cette adaptation. R3 justifie de distinguer identité de position et ordre. La navigation clavier ajoute une charge ; ne pas agréger avec tactile/souris.

**Acceptation P0.** Après présentation, aucun repère du trajet dans vue/arbre accessible ; géométrie stable ; saisie et annulation possibles entièrement au clavier ; réponse A–C–B pour attendu A–B–C reconnue comme ordre différent ; pause lors du deuxième signal produit un essai interrompu ; la correction ne commence jamais avant validation.

## EX-MI-003 — Qu’est-ce qui a changé ?

**Compétences/statut.** MI-VIS ; MI-LIA pour association forme–couleur. **Non implémenté.** Détection/reconnaissance après masquage, pas rappel libre ; discrimination perceptive et attention contribuent. Les couleurs pertinentes sont explicitement conservées.

**But et consignes par condition.** Forme : « Retenez les formes ; dites si une forme a changé. » Couleur : « Retenez les couleurs ; dites si une couleur a changé. » Association : « Retenez quelle couleur porte chaque forme ; dites si les associations ont changé. » Une seule condition par bloc ; familiarisation séparée permettant de vérifier perceptibilité et compréhension.

| Condition | Composition et transformation permise | Ce qui reste fixe |
|---|---|---|
| Forme | Trois formes très distinctes ; remplacer une seule forme | Couleurs, positions, taille/orientation |
| Couleur | Trois objets ; remplacer une seule couleur par une autre palette admissible | Formes, positions, taille/orientation |
| Forme–couleur | Trois formes distinctes, trois couleurs ; permuter les couleurs de deux formes | Ensemble des formes/couleurs, positions, taille/orientation |

**Défauts proposés.** Exposition simultanée 5 s, masque neutre 1 s, seconde composition stable sans limite de réponse. Quatre essais : deux identiques et deux différents, ordre mélangé et non annoncé comme une alternance. Le tirage doit permettre toutes les positions de changement et toutes les paires d’échange ; pas de motif apprenable « toujours au centre ». Un exemple hors bloc montre côte à côte deux compositions afin de vérifier la perceptibilité avant la tâche mnésique. Ce contrôle ne diagnostique pas la vision.

**Phases/réponse.** Prêt → première composition → masque → seconde composition → choix « Identique / Différent » → si Différent, localisation proposée → validation finale → correction. La décision identique/différent est verrouillée avant localisation pour ne pas réécrire la détection. En condition forme/couleur, sélectionner un élément ; en association, sélectionner les **deux** formes dont les couleurs sont échangées, annoncé dans la consigne. Un utilisateur peut déclarer ne pas savoir localiser ; cela ne transforme pas automatiquement sa détection en erreur.

**Aides/correction.** Aucune première composition accessible pendant la décision/localisation. Revoir l’original rend l’essai assisté. Après validation, montrer les deux compositions, les changements s’il y en a, et une explication textuelle. Identique doit rester une vraie possibilité ; aucune correction disant « trouvez le changement » sur tous les essais.

**Observations et dénominateurs.** Sur essais différents : détections et changements manqués ; sur essais identiques : rejets corrects et fausses alertes. Absence déclarée et incident séparés. Localisation rapportée uniquement avec son nombre d’occasions : par exemple « 1 localisation exacte parmi 2 changements détectés et localisés », sans assimiler cela à tous les changements présentés. En association, une seule des deux formes trouvée est une localisation partielle, jamais la détection d’un seul objet modifié. Pas de score composite de mémoire ou de seuil de sensibilité calculé sur quatre essais.

**Progression/confort.** Deux éléments pour simplifier, trois proposés, augmentation jusqu’à cinq comme piste de profil ; ne pas diminuer exposition en même temps. Palette sRGB, fond mat, tailles et contrastes versionnés ; couleurs discriminables sans saturation criarde. Contrôle d’interface lisible mais aucun nom/symbole de couleur donnant une réponse pendant le stimulus. Si les couleurs ne sont pas discriminables, choisir la condition forme ou une autre activité et garder les résultats séparés. Une variante verbalisée est un autre protocole.

**Données/fondement.** Références des deux compositions, condition, éléments réellement modifiés, palette/fond, durées, décision verrouillée, localisation et aides. R1 : transfert entre tâches visuelles proches dans son étude, sans validation de ces formes familières ni efficacité SPC. R4 : détection forme/couleur/position et associations, fondement expérimental, pas démonstration thérapeutique. Une difficulté perceptive n’est pas attribuée à la mémoire.

**Acceptation P0.** Des essais identiques existent réellement ; seules les dimensions prévues varient ; une permutation conserve les ensembles de couleurs/formes ; première composition absente du DOM après masque ; pas de fuite via texte alternatif ; une fausse alerte est distincte d’un changement manqué ; la localisation ne réécrit pas la décision initiale ; correction nomme les deux formes échangées.

## EX-MI-004 — Quel objet était où ?

**Compétences/statut.** MI-LIA et MI-SPA, identité des objets en contribution ; **non implémenté**. Associations simultanées avec objets fournis au rappel, sans ordre à mémoriser. Ce protocole n’est ni une reconnaissance des objets présents ni leur remise dans un ordre d’apparition.

**But/consigne.** « Retenez où se trouve chaque objet. Ensuite, replacez les objets dans les emplacements vides. » En entraînement, proposer une stratégie avant l’exemple : repérer les relations (« la clé à gauche de la tasse »). La verbalisation est une stratégie, pas preuve d’un système de mémoire isolé. Version d’observation sans conseil nouveau pendant le bloc.

**Stimuli proposés.** Trois objets familiers très distincts — clé, tasse, livre — dans trois emplacements fixes, présentation simultanée 6 s puis masque 1 s. Un profil simple utilise deux objets ; la géométrie, la banque d’objets et leur apparence sont versionnées. Aucun emplacement prérempli au rappel. Les couleurs peuvent distinguer les objets ; elles restent identiques entre exposition et réponse et ne créent pas une deuxième association à retenir.

**Phases/réponse.** Prêt → modèle → masque → emplacements vides et réserve de tous les objets → sélectionner un objet puis sa destination → validation → comparaison. Réserve visuellement distincte de la zone des emplacements. Son ordre est tiré **indépendamment** de la disposition modèle ; ne pas recopier systématiquement l’ordre initial. Une coïncidence aléatoire reste possible : imposer que tout objet change de rang pourrait lui-même créer un indice, surtout avec deux objets. Ne pas utiliser nom, ID, texte alternatif ou couleur de case encodant la solution.

**Interaction.** Alternative clavier et clic puis destination obligatoire ; glisser facultatif. Déplacer un objet déjà posé, retirer un placement et annuler possibles. Un objet ne peut occuper deux emplacements ; une case ne peut contenir deux objets. Déposer sur une case occupée propose un déplacement/échange explicite et réversible, jamais un écrasement invisible. Valider partiellement reste possible avec avertissement neutre « Un emplacement est vide » et choix de corriger ou confirmer ; cela n’impose pas de deviner.

**Aides/correction.** Après réponse verrouillée, montrer modèle et placement. Revoir le modèle avant validation nécessite terminer la première tentative puis un essai assisté. Aucun fantôme d’objet ou dessin de couleur restant dans la bonne case. Le dernier placement peut être déduit des autres quand autant d’objets que de cases sont fournis : les associations ne sont donc pas des observations indépendantes.

**Observations.** Nombre d’associations exactes sur celles attendues, associations erronées, objets non placés, permutations si démontrables. Un échange clé/tasse fait deux associations incorrectes ; le signal « permutation » décrit cette configuration, sans doubler le nombre d’erreurs total. Une mauvaise manipulation annulée n’est pas une erreur de mémoire. Avec les objets fournis, on ne mesure pas leur rappel libre ni leur dénomination.

**Progression/confort.** Augmenter de deux/trois à quatre objets sans réduire exposition ; nombre d’emplacements vides supplémentaires et similarité des objets = variantes séparées. Réserve stable pendant la réponse ; un zoom ne redistribue pas les emplacements. Si le viewport ne permet pas la disposition, choisir une géométrie adaptée avant départ, pas pendant le rappel.

**Données/fondement.** IDs objets, disposition modèle, ordre de réserve réalisé, placement final et aides ; version géométrie/palette, temps d’exposition/masque, mode de réponse. Pas de capture d’écran nécessaire. R4 fournit un fondement général aux associations visuelles ; la [recherche complémentaire](../10-clinique/recherche-exercices-feuille-de-route.md) ne fournit pas de preuve clinique spécifique de cette adaptation objet–position. Habillage quotidien ≠ transfert établi.

**Acceptation P0.** Modèle retiré du DOM/arbre accessible ; réserve sans indice de position ; aucune case préremplie ; réponse possible au clavier et annulation exacte ; permutation de deux objets produit deux associations fausses et un événement descriptif de permutation ; modifier la fenêtre en cours interrompt l’essai si cela modifie la géométrie ; correction impossible avant validation.

## Livraison, limites et décisions restantes

Ces quatre fiches satisfont la sélection des principes et rendent leurs modalités discutables. La destination initiale, les valeurs proposées, les banques originales et palettes/géométries précises restent à figer avant livraison. La relecture professionnelle est à tracer comme relecture, sans label de validation clinique. Les critères P0 du cadre et de chaque fiche constituent la recette ; aucun score d’empan normé, de capacité générale ou d’observance n’est ajouté.

EX-MI-005 (objets présents), EX-MI-006 (éléments fournis à remettre dans l’ordre) et EX-MI-007 (sons/rythmes) restent **écartés**. Aucun développement, fiche supplémentaire ou banque correspondante n’est prévu dans ce lot.
