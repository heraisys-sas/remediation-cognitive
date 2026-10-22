# Corrections des tâches existantes et de leurs objectifs

Version 1.2 — 9 octobre 2026. Relecture de cohérence documentaire effectuée ; relecture clinique et essai d’usage restent à réaliser. **EX-REV-001 et résultats EX-REV-003 implémentés et techniquement validés ; autres exigences à développer.** Voir le [bilan de validation](plan-developpement-cognitif.md#validation-finale-du-lot-1--9-octobre-2026).

Le [cadre commun](cadre-exercices-cognitifs.md) s’applique à toutes les fiches, notamment statuts, aides, confort, données, interruption et comparabilité. Fondement : [revue du 9 octobre, tâches réelles et compétences](../10-clinique/revue-competences-exercices.md#2-évaluation-par-tâche-réelle). Les mentions S renvoient à sa [bibliographie commentée](../10-clinique/revue-competences-exercices.md#5-sources-consultées-dans-consensus-et-portée), les R au [référentiel](../10-clinique/referentiel-exercices.md#8-références-déjà-consultées-via-consensus). Les sources soutiennent une distinction ou une approche ; aucune ne valide ce logiciel.

## 1. Contrat éditorial et conservation P0

Déduction, Calcul mental et Retrouver le mot restent disponibles. Aucun ancien item ni historique n’est supprimé. Une correction de libellé garde son identifiant ; un protocole/stimulus changé reçoit une version et, si le contenu servi change, de nouveaux identifiants conformément à la règle du dépôt. Les résultats historiques gardent leur condition d’origine ; les champs manquants deviennent « non renseigné », sans reconstruction supposée.

| Tâche actuelle | Description cible à utiliser dans carte/détails | Condition à faire apparaître dans les résultats |
|---|---|---|
| PQRST guidé | Appliquer une méthode de lecture et se rappeler un texte | Étape, texte masqué, modèle déjà vu ou non, relecture/aide |
| Position dans une séquence (`n-back` interne) | Retrouver un élément à une position avant la fin | Longueur et distance à la fin ; aucun intitulé « n-back continu » |
| Chiffres/mots directs | Retenir une suite dans le même ordre | Direct, lu/entendu/mixte, longueur |
| Chiffres/mots inversés | Retenir puis inverser une suite | Inverse, modalité, longueur ; mémoire de travail |
| Séries | Rappeler des mots d’une ou plusieurs séries | Modalité, série demandée, délai réel ; « après 20 secondes » lorsque réalisé |
| Contexte | Associer un message à une scène puis retrouver son contexte | Première passe avec photo puis rappel sans photo ; reconnaissance si QCM |
| QCM de stratégie existant | Découvrir ou reconnaître une stratégie | Choix guidé ; ne pas annoncer une stratégie appliquée |
| Actualiser une consigne | Mettre à jour les informations utiles | Informations remplacées/maintenues, réécoute éventuelle |
| Repérer l’essentiel / Comparer / Chercher | Sélectionner, comparer ou extraire une information selon un but | Documents visibles, aides ; pas un rappel de mémoire |

La reconnaissance, le rappel et la production restent distincts. « Contribution possible de l’inhibition » n’est pas « mesure de l’inhibition ». Les textes visibles sont centralisés selon les conventions du dépôt, lors de l’implémentation.

## 2. EX-REV-001 — PQRST réellement séquencé

**Cible et usage.** CT-MEM et CT-META : apprendre/appliquer une stratégie de lecture et de récupération, dans le parcours d’entraînement. Compréhension, vocabulaire, rédaction et saisie contribuent. La [proposition antérieure](proposition-palier-pqrst-mis-en-oeuvre.md) a fixé cinq étapes, textes de quatre phrases, question personnelle non notée et seuil de reformulation 4 idées sur 5 ; ces décisions sont conservées. Le seuil reste éditorial, pas clinique. **Implémenté :** écrans successifs et masquage effectif dans [sequence.js](../../frontend/src/exercises/sequence.js), protocole versionné et observations décrits dans [ADR-043](../30-technique/adr/ADR-043-pqrst-sequence-et-observations.md).

| Phase | Consigne, stimulus et action | Aides et correction |
|---|---|---|
| P — Parcourir | « Repérez le sujet du texte. » Titre et première phrase ; choisir le thème | Retour bref après choix ; pas de texte complet anticipé |
| Q — Questionner | « Quelle question vous posez-vous sur ce texte ? » Champ libre, dictée locale facultative | Production non notée ; question possible montrée ensuite, puis retirée si elle donne une réponse |
| R — Lire | « Lisez pour chercher une réponse à votre question. » Texte complet et question personnelle | Lecture au rythme choisi ; Écouter disponible ; aucun chrono de vitesse |
| S — Reformuler | « Sans le texte, redisez l’essentiel avec vos mots. » Texte, question modèle et notes donnant des réponses retirés | Première reformulation verrouillée, ou absence explicitement déclarée ; « Relire » crée une tentative assistée, puis nouveau masquage |
| Retour S | Comparer sa reformulation aux idées-clés ; résumé modèle montré, conformément à la décision antérieure | Conserver première réponse et essai aidé séparément ; accompagnement Apple seulement au moment autorisé par ADR-027 |
| T — Se tester | « Répondez sans rouvrir le texte. » Deux questions une à la fois ; aucun texte, résumé ou note donnant la réponse | Correction après réponses validées ; une relecture reste possible comme aide explicite, pas comme réponse autonome |
| Fin | Fiche méthode en cinq lignes, consultation facultative | Résultats S et T séparés ; retour à l’accueil accessible |

**Arbitrage explicite.** Décision conservée dans l’implémentation : garder le résumé après S, le masquer avant T et nommer T « rappel après le retour sur la reformulation ». T suit une réexposition corrective : sa réussite n’est pas un premier rappel autonome. Si l’on souhaite un T avant tout retour correctif, reporter le résumé après T constitue une variante à décider, avec nouvelle version ; ne pas la modifier silencieusement.

**Transitions P0.** P avance après choix ou absence déclarée ; Q après saisie de la question ou déclaration « Je ne sais pas quoi demander », sans attribuer de score. R se termine sur une action explicite « Passer à la reformulation », qui arrête la lecture et retire le texte avant d’activer S. S est validée avant son retour ; une reformulation absente est conservée comme absence, pas comme production réalisée. Le retour S reste consultable jusqu’à « Passer au test », puis est retiré avant d’activer T. Chaque réponse T se verrouille avant la question suivante ; la correction détaillée des deux réponses vient ensuite, pour éviter de donner indirectement la seconde réponse. Aucun champ vide non validé ne déclenche une progression automatique.

**Observations et données.** Étapes effectivement réalisées, première reformulation, aides/réexpositions, idées reconnues et ambiguïtés, réponses T et modalité. Une similarité lexicale/sémantique incertaine ne juge pas automatiquement une compréhension ; permettre « À vérifier » et la comparaison aux idées-clés. Question personnelle non évaluée, notes facultatives locales ; pas de note de métacognition ni de conservation d’une conversation IA. Une relance après correction n’altère pas le résultat initial, conformément à [ADR-027](../30-technique/adr/ADR-027-accompagnement-pqrst-local.md).

**Progression/confort.** Varier précision des idées et complexité du texte séparément ; garder cinq étapes. Aucun raccourcissement de lecture couplé à un texte plus complexe. Les quatre textes du palier restent disponibles ; le nombre à faire n’est ni un minimum obligatoire ni un dosage clinique. Pause en lecture/entre textes possible ; interruption en rappel suivie d’un nouvel essai ou reprise assistée clairement qualifiée.

**Fondement.** S08 : sept personnes avec lésions préfrontales, effets de la méthode sur rappel/réponses ; petit échantillon et autre population. Soutient l’approche PQRST, pas ce seuil, l’algorithme de reformulation ni l’efficacité de l’interface.

**Acceptation P0.** Après R puis au test T, recherche dans DOM/arbre accessible et essai de lecture audio ne révèlent ni texte ni résumé ; une seule étape active ; le modèle S vu avant T apparaît dans la condition ; une relecture sépare l’essai aidé ; Q n’a jamais de score ; les anciens résultats ne reçoivent pas rétrospectivement la mention « texte masqué ». L’ancien QCM après texte reste accessible sous un intitulé d’introduction, sans prétendre appliquer les cinq étapes.

## 3. EX-REV-002 — Mémoire sérielle et conditions correctement nommées

**Cible/actuel.** Direct : MI-VER/MI-ORD ; inverse : CT-MDT ; position relative : maintien de l’ordre et récupération après fin de séquence. Les parcours existent dans [catalog.py](../../backend/app/domain/catalog.py) et [presentation.js](../../frontend/src/exercises/presentation.js). Le type interne `n-back` ne change pas dans ce lot ; la nouvelle famille candidate de n-back aura un autre protocole.

**Protocole.** Consigne « Retenez la suite ; à la fin, retrouvez l’élément demandé avant le dernier. » Donner avant départ un exemple de distance explicite, par exemple « deux positions avant le dernier » : A–B–C–D–E → C. Présenter la suite, la masquer, poser une seule question et recueillir la réponse, puis corriger. La distance est connue avant l’essai ; si une variante la révèle après la série, elle est séparée. Direct/inverse ont chacun leur consigne et leur correction ; aucune inversion cachée dans une progression directe.

**Stimuli/aides.** Banque et paramètres actuels conservés jusqu’à révision dédiée. Réécoute/représentation uniquement avant nouvelle tentative assistée. Les associations mot–nombre restent décrites comme rappel de paire après délai observé ; aucune conclusion d’apprentissage durable sans protocole longitudinal distinct.

**Observations.** Pour séries : éléments corrects, omissions, intrusions et confusions de série lorsque identifiables ; ordre observé uniquement si demandé. Pour séquence : réponse attendue, obtenue et position effectivement choisie si non ambiguë. Conserver modalité, longueur, distance, règle direct/inverse, délai réel, nombre de présentations. Les rapprochements cognitifs restent ceux de R3/S13 ; pas une mesure de vigilance.

**Progression/confort.** Longueur, distance, nombre de séries et délai sont des dimensions séparées ; rythme et voix réglables sans mélange des résultats. Le protocole de Retenir un code détaillé dans [EX-MI-001](memoires-immediates.md#ex-mi-001--retenir-un-code) ne remplace pas tacitement les variantes inverses.

**Acceptation P0.** Aucun texte utilisateur n’appelle la position relative « n-back » ; essai A–B–C–D–E ci-dessus corrigé C ; modalités et direct/inverse séparés ; délai prévu et réalisé distingués en cas d’interruption ; une série non montrée ne crée aucune omission. Les identifiants et historiques existants subsistent.

## 4. EX-REV-003 — Retrouver le contexte, deux passes distinctes

**Implémenté et validé le 9 octobre 2026 :** résumé par passe, première réponse conservée et journal durable séparé ; [ADR-044](../30-technique/adr/ADR-044-observations-contextes-et-persistance.md). Pas de nouvelle tentative notée après révélation de photo, de délai supposé ni de reprise de séance après rechargement.


**Cible/usage/actuel.** CT-MEM : associer un message à une scène et retrouver sa source ; entraînement possible au repérage d’indices de contexte. Photos et questions sont déjà présentes ; le résumé demeure principalement fondé sur les premières réponses selon [ADR-035](../30-technique/adr/ADR-035-scenes-memoire-source.md). **À développer :** résultat spécifique de chaque passe, aides et exposition réelle.

**Protocole conservé.** Chaque scène de la première passe est révélée sur activation explicite du bouton **Afficher** ; aucun affichage automatique à l’ouverture de l’item. La phrase nommant le contexte reste masquée ; la transcription lisible et la voix peuvent restituer le message sans nommer sa source. Dix scènes selon le corpus actuel, sans en faire un nombre obligatoire de séance : pour chaque scène, photo/message → question immédiatement après cette photo → réponse/correction → scène suivante. Après cette première passe, rappel des contextes **sans photo**, question par question. Après une réponse erronée au rappel, montrer la photo correspondante et permettre de comprendre/corriger ; conserver l’erreur de première réponse. Une réponse juste ne déclenche pas une réexposition automatique avant les autres rappels.

**Stimuli/réponse.** Photos web légères, originales ou utilisables, préparées localement avec dimensions réservées ; conserver les variantes responsives déjà livrées plutôt que réencoder ou agrandir les fichiers sans besoin ; défaut de budget à arbitrer : WebP/AVIF ou format de repli, environ 200 ko maximum par photo et taille adaptée à l’affichage. Précharger la photo utile avant départ de sa phase ; échec = incident, pas omission. Pas de téléchargement distant contenant les réponses de l’utilisateur. Texte alternatif et nom de fichier ne donnent pas la scène masquée au rappel. Conserver les choix de réponse si le parcours est en QCM et décrire le résultat comme reconnaissance de source, pas rappel libre.

**Aides/correction/observations.** Première passe et seconde passe ont chacune : nombre présenté, première réponse, justesse/absence, choix et aide. La seconde distingue première réponse sans photo, photo après erreur et éventuelle réussite après photo. Ne pas sommer les deux passes en score de mémoire. Un distracteur doit être plausible et éviter une réponse déterminée seulement par la longueur ou une formule unique.

**Progression/confort.** Modifier la similarité des contextes ou le nombre de scènes séparément ; exposition au rythme choisi, lecture locale possible, décor neutre. Une interruption avant le rappel conserve la première passe et qualifie le délai de rappel ; aucun délai supposé. Données minimales : IDs scène/message/question, passe, ordre, exposition/révélation, réponses et délai entre passes ; pas de copie des photos dans chaque résultat.

**Fondement.** S03/S09 soutiennent stratégies de mémoire et apprentissage contextualisé chez des adultes avec lésions cérébrales acquises, principalement TBI modéré/sévère pour INCOG ; aucune étude directe de ces dix scènes. La répétition et le feedback de la première passe influencent le rappel final.

**Acceptation P0.** Le bouton Afficher est nécessaire pour révéler chaque nouvelle scène ; aucune phrase ne nomme sa source pendant la présentation ; on voit une question après chaque photo ; au rappel aucune photo accessible avant réponse erronée ; erreur puis révélation donnent un premier résultat erroné et une aide, jamais une réussite autonome réécrite ; deux résumés séparés ; sortie après trois scènes ne compte pas les sept autres fausses ; une photo non chargée suspend l’essai.

## 5. EX-REV-004 — Déduction, Calcul mental et Retrouver le mot

Ces exercices sont **conservés** ; les exigences ci-dessous affinent leurs observations sans modifier d’office leur difficulté, banque ou progression.

| Exercice | Action, aides et correction proposées | Observations spécifiques et données minimales | Progression, limites et acceptation P0 |
|---|---|---|---|
| **Déduction** — CT-RAI | Garder indices et grille visibles ; résoudre puis valider. Après réponse, proposer facultativement « Quelle contrainte avez-vous vérifiée ? » avec sélection d’un indice ou explication libre ; ne pas imposer un nouveau texte à chaque problème. Aides raisonnées existantes avant nouvelle tentative, correction après validation. | Première solution, contraintes satisfaites/non satisfaites quand vérifiables, indice consulté, démarche déclarée. Une explication libre n’est pas notée automatiquement. | Varier nombre/structure des contraintes séparément. Une grille visible est un support autorisé. Acceptation : solution et vérification séparées ; refus de répondre à la question facultative sans pénalité ; aucune métrique d’intelligence. S01/S05 : cadres exécutifs et stratégies après TBI, appui indirect. |
| **Calcul mental** — CT-CON, contribution CT-MDT | Garder opérations et applications adultes. Consigne « Calculez à votre rythme. » Après validation : résultat et méthode adaptée ; choix facultatif de méthode utilisée (décomposer, fait connu, autre). Une solution consultée crée un essai assisté. | Réponse initiale, résultat, méthode déclarée et unités. Classer seulement les erreurs démontrables (unité absente, signe, résultat incorrect) ; pas diagnostiquer une erreur de retenue sans trace. | Complexité numérique et nombre d’étapes séparés ; aucun chronomètre imposé. Acceptation : pas de « vitesse/flexibilité » déduite de diversité d’opérations ; méthode inconnue autorisée ; réponses équivalentes tolérées selon ADR-008. S13/S05 et ADR-024 : pas de preuve directe du corpus. |
| **Retrouver le mot** — CT-LEX | Définition → production ; indices progressifs à la demande ; QCM conservé dans ses conditions actuelles. Correction montre mot et lien à la définition. SFA/PCA : une invite sémantique/phonologique à la fois, notes facultatives, nom « inspiré de SFA/PCA » si protocole adapté. | Réponse autonome/indicée/reconnue ; ordre des indices réellement ouverts ; transcription corrigée ; mot déclaré inconnu séparé d’un mot non retrouvé. Ne pas assimiler notes vides à un échec. | Familiarité, précision de définition et aide réglées séparément. Acceptation : résultat QCM séparé de production ; aide visible dans le résultat ; dictée incertaine jamais erreur cognitive automatique ; aucun score des notes SFA/PCA. S06 : 21 études/55 personnes aphasiques ; S07 : dix personnes aphasiques, effets chez sept ; extrapolation vers SPC. |

Le suivi compare des conditions similaires dans le domaine entraîné. Une évolution de lexique ne démontre pas un gain de mémoire générale ; une opération exacte ne mesure pas une fonction exécutive isolée. Les explications et notes personnelles sont facultatives, locales et non requises pour accéder à l’essai suivant.

## 6. EX-REV-005 — De la stratégie choisie au plan exécuté

**Cibles/usage.** CT-PLA/CT-META/CT-FLE : construire, utiliser, vérifier et réviser un plan ; parcours d’entraînement. **Actuel :** QCM « étape suivante », « par où commencer », « meilleure solution », auto-instruction, choix/vérification/adaptation de plan ; certains plans vérifiables existent déjà selon [ADR-019](../30-technique/adr/ADR-019-plans-verifiables-et-documents-consultables.md). La révision ajoute l’action manquante là où nécessaire, sans effacer les formats guidés.

**Scénario proposé.** Préparer un petit dossier : trois actions et deux contraintes explicites, par exemple compléter un formulaire avant de le signer, joindre la pièce demandée avant envoi. Toutes les informations utiles restent visibles. Consigne « Préparez votre plan, puis utilisez-le. » Construire un ordre par sélection/déplacement ; formuler une auto-instruction facultative (« Je vérifie les pièces avant d’envoyer ») ; exécuter les actions dans une simulation ; une nouvelle contrainte annoncée demande une modification ; vérifier avant de terminer ; corriger ensuite.

**Aides.** Démonstration distincte et QCM existant comme introduction ; modèle partiel, rappel du but et liste de contrôle sur demande. Une auto-instruction choisie dans une liste est notée comme choisie, pas produite. La consigne et les contraintes visibles font partie du protocole, pas d’une fuite à masquer.

**Correction/observations.** Corriger à partir des contraintes, accepter tous les ordres valides. Observer plan compatible, étape exécutée, contrainte manquée, modification après nouvel événement, erreur détectée spontanément ou après aide. Ne pas attribuer une erreur unique à « manque de flexibilité ». Conserver plan initial/final et actions validées ; traces de glissement et texte libre exhaustif inutiles.

**Progression/confort.** Défaut proposé : trois actions puis quatre, une modification à la fois ; ajout de contraintes avant accélération, sans minuterie de réponse. Une étape et une action active par écran ; le plan reste un repère compact consultable. Pas d’interruption imprévue en plus de la contrainte nouvelle.

**Fondement.** S05, recommandations de stratégies exécutives après TBI surtout modéré/sévère ; soutient l’application et le contrôle du but. Simulation originale, pas protocole complet de Goal Management Training.

**Acceptation P0.** Deux ordres différents respectant les contraintes sont acceptés ; le résultat expose une action réellement exécutée ; nouvelle contrainte introduite après enregistrement du plan initial ; « Vérifier » permet de chercher avant toute révélation ; choix QCM et production séparés ; une pause conserve un brouillon sans produire de durée continue comparable.

## 7. EX-REV-006 — Rappel externe et intention si–alors appliqués

**Cible/actuel.** CT-PRO et apprentissage d’aide externe ; aujourd’hui reconnaissance d’une stratégie dans un QCM. **Révision proposée :** appliquer une intention dans une courte simulation d’entraînement ; un rappel affiché n’est pas une mesure de mémoire prospective sans aide.

**Phases.** Consigne « Quand le message “Dossier prêt” apparaîtra, joignez la pièce prévue. » Choisir/configurer un rappel local dans la simulation ; vérifier sa règle si–alors ; effectuer deux ou trois petites actions indépendantes et peu chargées ; événement cible visible ; réaliser l’action prévue ; retour après fin de l’occasion d’action. L’événement est déclenché par une étape, pas par une horloge de vie réelle. Variante sans rappel seulement sur choix explicite, avec autre condition.

**Stimuli/réponse/aides.** Messages synthétiques sans données personnelles ; liste de pièces distinctes ; action sélectionner puis joindre. Le rappel peut contenir l’intention entière si c’est l’aide entraînée. Distinguer rappel programmé mais non délivré (incident), rappel délivré, consulté et action réalisée. Pas de notification externe ni d’envoi réel requis.

**Observations/données.** Bonne action au signal, mauvaise action, action prématurée, occasion terminée sans action, aide consultée ; ordre et événement déclencheur. Pas de latence normée. Résultats « avec rappel » et « sans rappel » séparés. Une absence de réponse après sortie est interrompue, pas oubli.

**Progression/confort.** Défaut : une intention et un signal explicite ; varier nombre d’étapes intercalées ou complexité de l’action séparément. Aucun son obligatoire ni double tâche ajoutée d’office.

**Fondement et acceptation.** S03/S09 : aides/stratégies dans TBI/ABI, pas validation du simulateur. P0 : la personne réalise une action observable ; un rappel effectivement consulté est tracé ; le signal absent n’engendre aucun échec ; aucune alarme système ou transmission externe créée ; QCM conservé comme familiarisation.

## 8. EX-REV-007 — Prise de message et usage d’une note

**Cible/actuel.** Encodage et récupération verbale ; le QCM actuel sur une heure est une réponse locale. **Deux versions proposées en entraînement :** retenir sans aide ; prendre une note puis l’utiliser. Elles n’ont pas le même objectif.

**Phases et consigne.** « Retenez quoi faire et quand » ou « Notez ce qui vous aidera à réaliser la demande ». Départ → message bref de deux informations dans une modalité choisie → retrait → restitution structurée « quoi / quand » → exécution simulée (choisir l’action et le créneau) → correction. Dans la version avec note, celle-ci reste consultable pendant l’action ; dans l’autre, texte et réécoute sont retirés. Une réécoute demandée crée une aide explicite.

**Correction/observations.** Définir valeurs admises et tolérances de forme ; observer information exacte, omission et confusion uniquement si démontrables. Usage de note, restitution et action séparés. Une bonne action avec note montre l’usage de l’aide, pas un rappel sans support. Conserver champs validés, présence/consultation de la note et réponse ; texte de note facultatif, local.

**Progression/confort/fondement.** Ajouter une troisième information avant toute autre complexification ; diction locale et taille du texte indépendantes. S03/S09 : appui aux stratégies de mémoire dans ABI/TBI, extrapolation au scénario. P0 : note autorisée seulement dans la bonne condition ; « 15 h » et « 15 heures » équivalents ; information non entendue à cause d’une coupure = incident ; action finale effectivement réalisée, pas seulement stratégie choisie.

## 9. EX-REV-008 — Estimer puis organiser son temps

**Cible/actuel.** CT-TEM/CT-PLA : estimation et arbitrage, aujourd’hui surtout QCM. **Proposition d’entraînement :** estimer une tâche concrète puis examiner l’écart et préparer une marge.

**Phases.** Consigne « Estimez le temps dont vous aurez besoin, puis faites la tâche à votre rythme. » Choisir une durée estimée pour classer quatre documents simples ; effectuer le classement ; voir durée active et pauses séparées ; comparer à l’estimation ; choisir une marge pour une tâche suivante similaire. Les documents restent visibles. Pas de course ni de délai éliminatoire.

**Aides/correction/observations.** Exemple préalable non mesuré ; aide à découper en étapes possible. Le classement a des critères explicites ; l’estimation n’a pas de « bonne durée universelle ». Afficher estimation, durée active mesurable, durée écoulée et différence signée en unités de temps, sans note de capacité. Si le temps n’a pas été capturé correctement, comparaison absente. Conserver seulement estimation, événements début/fin/pause et état de tâche.

**Progression/confort/fondement.** Nombre d’étapes puis contraintes, séparément ; chrono masqué par défaut. S05 justifie contrôle et stratégie, sans validation spécifique de cet exercice. P0 : une pause n’est pas confondue avec lenteur ; comparaison conserve le signe de l’écart ; aucune pénalité pour durée supérieure à l’estimation ; aucune déduction de vitesse de traitement générale. La gestion de pression temporelle fait l’objet d’EX-CAND-005, autre protocole.

## 10. EX-REV-009 — Tâches fonctionnelles conservées et mieux observées

Les actions principales sont déjà présentes ; les exigences portent sur objectifs, correction et résultats. Les modèles restent disponibles lorsqu’ils font partie de la tâche. Les données nouvelles ne sont promises comme disponibles qu’après implémentation.

| Tâche et consigne | Protocole/réponse/correction | Observations, progression et critères P0 |
|---|---|---|
| **Actualiser une consigne** : « Gardez les informations encore valables. » | Présentations successives remplaçant explicitement certaines informations, retrait puis application finale ; réécoute du message courant autorisée selon modalité, anciens messages masqués ; correction après validation. | Tracer état attendu, état rendu et anciennes valeurs : ancienne information conservée, valeur nouvelle erronée ou information inchangée perdue lorsque identifiable ; pas tout appeler inhibition. Varier nombre de mises à jour séparément du rythme. P0 : aucune ancienne lecture accessible au rappel ; champs sans changement correctement jugés. S01/S13. |
| **Repérer l’essentiel** : « Gardez ce qui répond à ce besoin. » | But visible, document et options ; sélection modifiable, validation puis explication de pertinence. Aide peut rappeler le critère, sans sélectionner silencieusement. | Sélections pertinentes, omissions et ajouts non pertinents ; compréhension contribue. Varier plausibilité des distracteurs séparément de densité. P0 : le critère reste visible ; pas d’étiquette inhibition pure. S11/S04, soutien indirect. |
| **Comparer deux documents** : « Repérez les écarts demandés. » | Deux documents consultables, critère explicite ; marquer les écarts, valider puis correction. Navigation n’est pas une alternance de règle. | Écarts repérés/manqués, fausses alertes ; conserver repères sélectionnés et aide. Augmenter nombre d’écarts ou distracteurs séparément. P0 : document visible qualifié ; aucun score mémoire/attention alternée. S11/S04. |
| **Chercher dans un document** : « Trouvez l’information pour réaliser cette action. » | Document visible → extraction → petite action cohérente (choisir le créneau correspondant) → validation/correction ; aide montre une zone seulement sur demande. | Extraction et action séparées ; texte libre incertain à vérifier. Varier structure du document ou demande. P0 : action admise définie par le document ; pas de score de rappel. S04, pertinence contextuelle indirecte. |
| **Reprendre après interruption** : « Reprenez le dossier à votre point d’arrêt. » | Conserver début de contrôle, détour non noté, dossier masqué puis point de reprise et achèvement ; aide de repérage en condition distincte. | Point de reprise exact, recommencement, étape omise et aide ; ne pas additionner le détour au score principal. Varier emplacement de l’interruption avant sa complexité. P0 : interruption réellement vécue ; ni double tâche simultanée ni vigilance attribuées. S05/S04. |

Temps de réponse non nécessaire à ces corrections sauf durée d’interruption prévue par la fiche existante. Les pauses libres, modalités et aides sont conservées pour interpréter le résultat, sans imposer de rythme ni de nouvelles images.

## 11. Hors révision de protocole dans ce lot

Anglais et Python restent en **Extra**, présentés comme connaissances linguistiques et programmation. Missions et carnet restent outils de préparation et retour d’expérience ; aucun score de transfert, fréquence ou observance ajouté. Les comparaisons d’historiques dont les modalités/aides ne sont pas connues restent descriptives et signalées.

Livraison proposée : EX-REV-001 à 003 et contrat éditorial en premier ; actions des stratégies EX-REV-005 à 008 ensuite, indépendamment des affinements EX-REV-004/009. Aucun calendrier ni développement réalisé par ce document. La recette de chaque future implémentation vérifie ses exemples et les exigences du cadre ; cette livraison documentaire ne modifie ni correcteur, ni contenu, ni données personnelles.

## Livraison locale EX-REV-005 à 008 — 10 octobre 2026

Les actions simulées des quatre fiches sont implémentées sous le protocole stratégies V2, avec trois variantes par parcours. Les QCM et leurs historiques sont conservés. La [spécification de la version servie](strategies-appliquees.md) précise les transitions, résultats observables, aides, correction conservatrice et limites. Validation locale dans le [plan](plan-developpement-cognitif.md#lot-4--livraison-locale-v2) ; aucune intégration dev/main de ce lot, aucun nouveau candidat sélectionné.
