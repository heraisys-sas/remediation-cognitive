# Cadre des exercices cognitifs — entraînement et autoévaluation

Version 1.1 — 9 octobre 2026. Relecture de cohérence documentaire effectuée ; relecture clinique et essai d’usage restent à réaliser. **Spécification documentaire relue ; aucune nouvelle fonction livrée.**

## 1. Problème et résultat attendu

Une même tâche peut servir à apprendre une stratégie, pratiquer une compétence ou observer sa performance. Les descriptions actuelles confondent parfois ces usages : texte encore visible au test PQRST, position dans une séquence appelée techniquement `n-back`, QCM présenté comme application d’une stratégie. Pour une personne fatigable, ces écarts rendent le résultat difficile à comprendre et peuvent ajouter des étapes inutiles.

Cette spécification rend chaque parcours explicite : ce que la personne fait, ce qui reste visible, les aides reçues, le résultat réellement observable et ses limites. La réussite du travail produit se vérifie par la fidélité du protocole, la compréhension de la consigne et la possibilité de régler le confort. Aucun objectif d’assiduité, de rétention commerciale, de complétion du programme ou de gain cognitif clinique n’est fixé.

Sources de vérité : [référentiel v1.3 et suivants](../10-clinique/referentiel-exercices.md), [revue des tâches existantes](../10-clinique/revue-competences-exercices.md), [recherche des candidats](../10-clinique/recherche-exercices-feuille-de-route.md). Les sources scientifiques R, S et FR restent dans ces documents ; les fiches ci-dessous relient chaque choix à leur portée sans recopier les bibliographies.

## 2. Périmètre, statuts et navigation documentaire

| Document de spécification | Statut de sélection | État logiciel au 9 octobre 2026 |
|---|---|---|
| [Corrections des exercices existants](corrections-exercices-existants.md) | Exercices conservés ; révisions détaillées proposées | Tâches présentes, corrections nouvelles à développer |
| [Quatre mémoires immédiates](memoires-immediates.md) | Quatre principes retenus par l’utilisateur | Retenir un code a une base partielle ; trois autres non implémentés |
| [Candidats attention, contrôle et visuospatial](candidats-cognitifs.md) | **Propositions à arbitrer**, y compris leur destination | Aucune nouvelle implémentation déclarée |
| [Prototypes du 7 octobre](prototypes-epreuves-cognitives.md) | Exigences antérieures, portée résiduelle au §9 ci-dessous | Prototypes non implémentés selon la revue |

« Spécifié » signifie qu’un contrat relisible existe ; cela ne signifie ni sélection définitive, ni livraison, ni validation clinique. Les exigences **P0** sont nécessaires pour livrer correctement un exercice **si sa réalisation est décidée**. **P1** désigne une extension facultative. Cette notation ne classe pas les candidats par priorité de livraison.

Décisions acquises : conserver Déduction, Calcul mental et Retrouver le mot ; spécifier EX-MI-001 à 004 ; exclure EX-MI-005 à 007 ; accueillir l’autoévaluation dans **Exercices ciblés**. Aucun exercice ou historique n’est supprimé. Le bilan standardisé, les normes/percentiles, le diagnostic, l’IRT historique et un score global de capacités restent hors périmètre. L’absence de validation clinique spécifique n’empêche pas de décrire honnêtement une pratique d’entraînement.

## 3. Trois usages explicites

| Usage | But et déroulement | Résultat et comparaison |
|---|---|---|
| **Parcours d’entraînement** | Pratiquer la compétence nommée ; apprendre/appliquer une stratégie lorsque pertinente ; aides et correction disponibles aux phases prévues | Réussites, erreurs et aides sur la tâche ; séparer première réponse, essai assisté et reprise après correction |
| **Exercices ciblés — autoévaluation** | Observer sa performance dans une configuration choisie, annoncée et stable ; exemple préalable distinct ; correction au moment défini | Description de cette tâche et de ses conditions ; comparaisons uniquement compatibles ; aucune norme clinique |
| **Double usage** | Deux protocoles ou modes versionnés partageant éventuellement un contenu et un composant | Historiques et résultats séparés ; une séance d’entraînement ne devient jamais rétrospectivement une observation autonome |

Une répétition de n-back peut entraîner la tâche de n-back sans établir un transfert général. Inversement, savoir choisir une bonne stratégie dans un QCM ne démontre pas son application. La destination dépend de l’objectif et du protocole, pas du prestige d’un test ni de la seule présence d’un chronomètre.

Texte d’accueil proposé pour Exercices ciblés : « Observez comment vous réalisez une tâche, dans les conditions choisies. Les résultats décrivent cet exercice. » Les détails sur répétition, aides et matériel apparaissent dans le résultat, sans avertissement permanent ni vocabulaire diagnostique.

## 4. Besoins utilisateur et contrat commun P0

- En tant que personne fatigable, je veux comprendre l’action attendue et commencer quand je suis prête.
- Je veux m’exercer avec une aide sans que le logiciel présente ensuite ma réponse comme autonome.
- Je veux observer deux essais comparables et savoir pourquoi des essais différents restent séparés.
- Je veux interrompre, changer mon confort et retrouver mes préférences sans perdre les réponses déjà validées.
- En tant qu’accompagnant autorisé par la personne, je veux distinguer une erreur de réponse d’un problème de perception, de pointage ou de dictée.

### Phases et réponses

Le parcours commun est : choix de tâche/usage → consigne avec exemple indépendant → prêt → présentation/action → réponse → validation → correction au moment prévu → résumé. Les phases non pertinentes sont omises ; la fiche définit les exceptions, notamment les flux continus et la correction entrelacée. Il n’est pas nécessaire de construire un moteur générique avant de livrer un lot.

La configuration et les stimuli effectifs sont figés au départ. Un bouton de réponse ne valide pas par simple focus. Avant validation, la réponse est modifiable, sauf réponse continue explicitement enregistrée au fil des événements. Après validation, une correction de saisie ou de transcription est une révision technique traçable ; elle ne remplace pas silencieusement une première réponse fausse. Une nouvelle tentative après révélation est assistée.

Pendant un rappel masqué, aucune réponse ne reste accessible dans un panneau, un attribut de contrôle, un texte alternatif, une ancienne vue ou une lecture audio encore en cours. Retirer les éléments du DOM/arbre accessible et couper la lecture ; un simple masquage visuel ne suffit pas. Les objets fournis pour répondre peuvent rester accessibles lorsque la tâche l’exige, sans porter leur ancienne position ou leur ordre correct. Il ne s’agit pas de rendre le logiciel inviolable par ses outils de développement.

Les corrections montrent ce qui était attendu et, si utile, une démarche courte. Un résultat ambigu est « À vérifier ». L’absence déclarée « Je ne sais pas » est distincte d’une question non atteinte ou d’un incident. Les omissions ne concernent que des occasions de réponse réellement présentées et terminées selon le protocole.

### Pause, sortie et incident

Pause et sortie sont accessibles, sans compte à rebours ni confirmation imposant d’attendre. Une pause entre essais conserve les essais achevés. Pendant un encodage, un maintien ou un flux, la pause masque le stimulus, arrête voix/capture et marque **l’essai interrompu** : le temps passé en pause n’est pas retranché pour fabriquer un rappel « immédiat » ou une mesure continue. Repartir utilise un nouvel essai lié, avec nouveau stimulus. Une tâche de construction/planification en entraînement peut reprendre son brouillon, avec pause tracée et sans comparaison de durée continue.

Perte de visibilité, rechargement, capture rompue ou stimulus incomplet suivent la même règle. Aucun item futur n’est compté faux. Le résumé d’une séance partielle affiche les seules observations disponibles. Le motif peut rester « interruption » ; une justification médicale ou personnelle n’est jamais exigée.

### Confort et difficulté

Le **confort** règle lisibilité, son/voix, mode de saisie, chrono visible ou masqué, rythme confortable et possibilité d’arrêt. La **difficulté de la tâche** règle longueur, nombre d’informations, similarité, contraintes et degré d’aide. Un paramètre comme la durée d’exposition influence les deux : il peut améliorer le confort, mais son changement rend les résultats différents et doit être tracé.

Les nouveaux protocoles proposent un niveau simple, un exemple et des essais à départ volontaire. Leurs valeurs chiffrées sont des **défauts de conception à arbitrer lors de l’essai d’usage**, jamais des doses thérapeutiques. Elles ne modifient pas automatiquement les quotas déjà livrés. Augmenter une dimension à la fois ; aucune accélération simultanée cachée. Pour les nouveaux exercices, proposer « Même niveau / Plus simple / Plus complexe » après un bloc, sans adaptation automatique en V1. Les règles de progression existantes restent décrites comme existantes tant qu’un changement n’est pas décidé.

## 5. Interface sobre P0

Fond ardoise mat, surfaces discrètes, typographie lisible, espaces stables, une consigne et une zone de tâche. La qualité visuelle vient de la hiérarchie et des alignements : pas de flash, scintillement, pulse, confetti, bruit décoratif, alarme de vitesse ni animation de déplacement des stimuli. Les changements nécessaires de stimulus sont stables, à cadence explicite. Le résumé bref propose le retour à l’accueil ; détails et réglages sont repliés.

Les couleurs pertinentes sont conservées. Les états d’interface ne reposent pas seulement sur la couleur ; en revanche, donner le nom ou un symbole de la couleur pendant une tâche de mémoire de couleur ou d’interférence changerait la tâche. Une alternative accessible est identifiée comme une autre condition, jamais présentée comme équivalente. Même règle pour décrire verbalement une figure ou une position spatiale. Le lecteur d’écran peut utiliser les contrôles ; on ne promet pas qu’il conserve toutes les dimensions d’une tâche visuelle.

Exigences de recette de conception : clavier complet avec focus visible et jamais couvert ; alternative clic puis destination pour toute manipulation par glisser ; cibles confortables proposées de 44 × 44 pixels CSS ; zoom 200 % et écran de 375 pixels sans perte de commande ; texte usuel contrasté à au moins 4,5:1 ; contours/états utiles à 3:1 ; aucun rétrécissement automatique des stimuli pour forcer une grille à tenir. Ces exigences produit ne constituent pas une certification d’accessibilité.

Audio unique : **Écouter** au repos ; pictogramme haut-parleur barré pendant la lecture, nom accessible « Arrêter la lecture », place et dimensions fixes. Lire la consigne n’ajoute pas une seconde modalité aux stimuli. Toute lecture d’un stimulus visuel crée une modalité mixte ou une aide, à tracer ; aucune synthèse pendant une réponse orale chronométrée. L’échec audio laisse un choix de modalité explicite et ne produit pas un essai auditif fictif.

Préférences et mode dérogatoire persistent selon [ADR-030](../30-technique/adr/ADR-030-interface-discrete-mode-derogatoire.md). Réglages dérogatoires visibles seulement après activation ; **aucun bandeau « mode dérogatoire actif »**. Désactivation : suspendre les valeurs dérogatoires sans les effacer. Changement en cours : appliqué au prochain essai, pas au stimulus courant. Échec de stockage : message discret dans Réglages et fonctionnement avec valeurs annoncées.

## 6. Observations, données nécessaires et comparabilité

Le résultat affiche un fait compréhensible : « 3 associations correctement replacées sur 4 », « 2 changements manqués », « réponse après un indice ». Un pourcentage éventuel expose son dénominateur ; dénominateur nul = résultat absent. Les erreurs sont des descriptions de réponse, pas des mécanismes cérébraux diagnostiqués. Une hausse peut refléter familiarité, stratégie, aide, fatigue ou dispositif.

### Socle minimal proposé, sans modification du contrat API dans ce lot

| Donnée | Pourquoi la conserver | Limite |
|---|---|---|
| ID d’essai/séance, date, ID exercice, usage, versions du protocole et du calcul | Relier sans dupliquer ; savoir ce qui a réellement été exécuté | Pas de profil médical obligatoire |
| Références et empreinte des stimuli, graine si génération, ordre réalisé, configuration effective | Reconstituer la condition et détecter une répétition | Le modèle correct reste dans la banque versionnée ; pas besoin de le dupliquer partout |
| Réponse validée et révision technique éventuelle ; statut observé/assisté/interrompu/à vérifier | Correction et provenance | Brouillons et frappes intermédiaires non nécessaires, sauf ordre de construction explicitement étudié |
| Aides réellement ouvertes, répétition/réexposition, phase et tentative | Séparer autonomie et apprentissage | Ne pas inférer l’usage d’une stratégie à partir de sa seule proposition |
| Modalités présentation/réponse et dispositif ; version de mise en page/palette quand pertinente | Ne pas agréger des conditions différentes | Pas d’empreinte matérielle détaillée ni d’inventaire du poste |
| Événements temporels requis par la fiche et durée active | Dater une présentation, délai ou fenêtre de réponse | Aucune durée de frappe interprétée comme vitesse cognitive |
| Résultats dérivés spécifiques et état de vérification | Résumé recalculable | Pas de score composite entre compétences |

La charge perçue peut être demandée une seule fois en fin de séance, facultativement (« confortable / effort important / je préfère arrêter »), sans seuil diagnostique ni pénalité. Aucun taux d’observance, série de jours ou taux de complétion du programme. Pas de télémétrie nouvelle nécessaire à ces spécifications.

Notes et textes personnels restent locaux. Ne pas conserver un audio par défaut. Pour une réponse orale ambiguë, garder la transcription nécessaire et sa révision ; sans preuve suffisante, résultat à vérifier. Une production graphique exportée n’est pas requise si les objets structurés suffisent ; dessin libre et audio sauvegardé restent options explicites. Les données d’exercice ne sont pas commitées.

L’entraînement utilise son périmètre existant. L’autoévaluation a un espace logique séparé, sans jointure automatique vers FSRS ou le bilan historique ; cela n’impose pas la création d’un nouveau service. Le contrat précis de persistance/API devra être arrêté avec l’ADR d’implémentation. Une réécriture idempotente conserve un seul événement ; un échec de sauvegarde garde un brouillon local et indique ce qui n’a pas été enregistré.

### Comparaison autorisée

Comparer seulement même exercice, usage, version de protocole/correction, modalité, dispositif de réponse, dimensions de difficulté, durées, aides, statut complet/vérifié et mise en page pertinente. Pour un protocole à tirages, conserver la même banque et les mêmes règles de composition ; une nouvelle graine n’invalide pas à elle seule la comparaison descriptive, mais les formes ne sont pas déclarées psychométriquement équivalentes. Signaler contenus déjà vus et ordre des essais. Une configuration différente reste consultable côte à côte avec ce libellé ; aucune courbe commune calculée par défaut.

Pour les tâches de rappel, distinguer trois événements : disparition effective du stimulus, disponibilité réelle des commandes de réponse et première action de réponse. Le masquage prévu se mesure jusqu’à la disponibilité de la réponse ; le temps entre cette disponibilité et la première action est une latence distincte. Le temps jusqu’à validation comprend encore la saisie et n’est pas un délai de maintien imposé. Pour une comparaison de compositions, dater l’apparition de la seconde composition au lieu de la confondre avec une réponse. Conserver uniquement les événements nécessaires à la fiche, sans journal de frappe. Le temps de réaction exige un stimulus individuel datable et une réponse datable sur la même horloge monotone ; un retour ASR/réseau ne fournit pas cette mesure. L’absence de mesure fiable laisse le champ absent. Les tâches de vitesse et couleurs ont leurs règles spécifiques dans la fiche et le prototype. Pour les flux à fenêtres, la réponse doit avoir commencé dans la fenêtre datée du stimulus : une réponse tardive n’est jamais transférée à l’item suivant. Le premier appui admissible est enregistré ; maintien de touche, répétitions automatiques et double déclenchement clic/clavier sont dédupliqués. Un nouvel item exige le relâchement d’une commande restée appuyée. Une fenêtre raccourcie par un incident de rendu n’engendre pas une omission cognitive.

## 7. Recette, priorités et succès du lot

Ordre proposé : corriger la fidélité/libellés de l’existant ; réaliser les mémoires retenues par lots indépendants ; sélectionner les candidats avant toute planification de livraison. Chaque exercice peut être essayé seul. Aucun calendrier clinique ni dose de programme n’est déduit de cet ordre.

Critères P0 transverses, à vérifier lors de l’implémentation sur données fictives :

- [ ] Consigne, stimulus, réponse et correction reproduisent le protocole de la fiche ; aucune réponse révélée à une phase interdite.
- [ ] Aucun résultat d’observation n’intègre une aide ou une nouvelle présentation comme un premier essai autonome.
- [ ] Pause, sortie, perte de visibilité, audio indisponible et sauvegarde répétée produisent des statuts exacts, sans réponses doublées ni omissions inventées.
- [ ] Un changement de modalité, rythme, aide ou règle de comptage sépare les comparaisons.
- [ ] Clavier, zoom, petit écran, focus et absence de mouvement décoratif sont inspectés ; les commandes d’arrêt restent accessibles.
- [ ] Chaque exemple d’erreur prévu par la fiche dispose d’une correction déterministe ou d’un état explicite « À vérifier ».
- [ ] L’utilisateur peut expliquer l’action à réaliser après la consigne et distinguer première réponse et réponse aidée dans le résumé lors de l’essai d’usage ; les incompréhensions sont consignées puis corrigées.

Les vérifications mesurent la qualité du logiciel et de son usage, pas son efficacité thérapeutique. Relecture orthophoniste/chercheur : **à réaliser**, avec population et limites conservées. Pour la présente livraison documentaire : vérifier liens locaux, ancres et `git diff --check` ; aucun test applicatif requis en l’absence de code changé.

## 8. Arbitrages ouverts

| Décision | Défaut proposé | Responsable et moment |
|---|---|---|
| Candidats réellement sélectionnés et destination | Aucune sélection implicite ; liste de propositions dans la fiche candidats | Utilisateur/conception, avant planification de livraison |
| Mémoires retenues : entraînement, observation ou deux usages | Pratique guidée possible et observation séparée ; commencer par le protocole de base sans adaptation automatique | Utilisateur/conception ; la sélection des quatre principes est déjà acquise |
| Valeurs de départ et progression nouvelles | Valeurs des fiches, toutes signalées comme propositions ; une dimension à la fois | Conception + essai d’usage, avant figer une version |
| PQRST : moment du résumé modèle | Conserver le modèle après S, le masquer pour T et qualifier T de rappel après feedback ; alternative après T à arbitrer | Utilisateur/conception ; voir EX-REV-001 |
| Comparaisons et persistance nouvelles | Résultats descriptifs séparés, données minimales, aucune migration destructive | Ingénierie avant implémentation API |
| Versions sensorielles alternatives | Changer d’activité/condition si la dimension n’est pas perceptible ; ne pas fabriquer d’équivalence | Conception et utilisateur lors de l’essai |

Les valeurs proposées rendent le travail implémentable et discutable ; elles ne demandent pas de bloquer toute préparation documentaire. Les décisions de sélection restent nécessaires pour présenter un candidat comme futur exercice livré.

## 9. Articulation avec les spécifications antérieures

Le présent cadre prévaut pour destination, statuts, pause, confort, données minimales et distinction des usages. Il s’appuie sur la décision récente de l’utilisateur, précisée par [ADR-042](../30-technique/adr/ADR-042-cadre-cognitif-et-autoevaluation.md). Les formulations plus anciennes excluant tout exercice évaluatif ne valent pas exclusion d’Exercices ciblés.

| Texte antérieur | Source opérationnelle désormais applicable |
|---|---|
| Prototypes §§1–3 : rubrique « Prototypes », familiarisation/mesure, règles communes | Présent cadre : Exercices ciblés pour observation, entraînement si réellement pratiqué ; familiarisation = essais séparés, sans quatrième destination |
| Prototypes §4 : correction différée | Mécanique de file/réponse conservée ; classement, limite et statut dans EX-CAND-009 ; aucune livraison automatique |
| Prototypes §5 : figures | Mécanique palette/clavier/annulation conservée ; conditions visible/masquée et stratégie dans EX-CAND-006 ; défaut historique 4 éléments/15 s conservé en observation |
| Prototypes §§6–7 : couleurs, comptage vocal et calculs | Contrat technique conservé intégralement, sous EX-CAND-008 ; pas d’autres scores d’interférence inventés |
| Prototypes §8 : données | Socle minimal du présent cadre ; champs spécifiques couleurs/figures seulement lorsqu’ils sont effectivement nécessaires ; audio facultatif |
| Prototypes §§9–11 : ordre des lots, pistes, remplacement | Ordre de travail du présent cadre et statut candidat des fiches ; ancien ordre conservé comme historique, pas engagement de livraison |
| Proposition PQRST du 27 septembre | Décisions de contenu et cinq étapes conservées ; EX-REV-001 prévaut sur séquençage, masquage et interprétation ; ADR-027 reste applicable après correction |

Le document des prototypes reste nécessaire pour les contrats détaillés précités : **il n’est pas supprimé**. Il sera archivé/remplacé uniquement lorsque toutes ses exigences utiles auront une nouvelle source explicite. Aucun développement de ce lot n’est attesté par l’existence de ces documents.

## 10. Relecture documentaire du 9 octobre 2026

Version 1.1 : relecture croisée des quatre fiches, des décisions utilisateur, du référentiel et des contrats antérieurs. Points précisés : fenêtres et frontières des réponses continues ; délais de masquage distincts de la saisie ; seconde tâche définie seule/ensemble ; go/no-go distinct du stop-signal ; transitions PQRST et initialisation/continuation du n-back ; mapping stable du changement de règle ; bouton Afficher et contexte masqué conservés.

La sélection des candidats, leurs usages initiaux et les valeurs de confort proposées restent à arbitrer. Le résumé PQRST après S reste conservé, masqué avant T ; le déplacement après T demeure une alternative, pas une décision prise. Cette relecture porte sur la cohérence documentaire et les exigences techniques ; elle ne vaut ni relecture professionnelle clinique ni recette d’une implémentation.
