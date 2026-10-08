# Spécification — prototypes d’épreuves cognitives

Version 1 — 7 octobre 2026. Statut : spécification de prototypes à développer ; aucune épreuve implémentée ou validée par ce document.

Remplace la backlog ajoutée au commit `acf74b54ccb64710f0fcfd3afcb37b64b371462b`. Les idées proviennent de l’utilisateur ; les règles opérationnelles ci-dessous sont des décisions de conception révisables, sans valeur de protocole clinique standardisé. Référence produit : ADR-038.

## 1. Problème, objectifs et périmètre

L’utilisateur souhaite essayer une correction différée, une reproduction de figures et trois tâches orales de couleurs. Une liste d’idées ne suffit pas à définir le comptage, les interruptions ou les comparaisons. L’expérience doit rester peu chargée et adaptée à une personne qui souhaite pouvoir s’arrêter facilement.

Objectifs vérifiables : démarrer volontairement une tâche ; connaître sa consigne ; quitter à tout moment ; retrouver les réponses et leurs corrections ; distinguer une erreur de réponse d’une incertitude de reconnaissance ; comparer seulement des configurations compatibles.

Périmètre : prototypes locaux, familiaux, dans une rubrique séparée des exercices de remédiation. « Familiarisation » et « Mesure personnelle » sont deux modalités des prototypes, pas deux nouveaux modules. La mesure décrit une séance sans diagnostic, percentile, norme populationnelle ni score global de capacités. Cette spécification ne réactive pas le projet historique de bilan standardisé ou d’IRT.

Hors version 1 : efficacité thérapeutique revendiquée, calibration clinique, adaptation automatique de difficulté, notation automatique du dessin libre, N-back, Corsi, double tâche et recherche visuelle. Ces quatre dernières idées sont conservées au §10.

## 2. Parcours commun et interface (P0)

Histoires utilisateur :
- En tant qu’utilisateur fatigable, je veux une consigne à la fois et un départ explicite pour ne pas être surpris par un stimulus ou un chrono.
- Je veux interrompre une épreuve sans être obligé de la finir.
- Je veux corriger une transcription sans que ma correction efface l’enregistrement brut.
- Je veux retrouver mes réglages habituels sans voir tous les paramètres à chaque visite.

États : `configuration → consigne → pret → en_cours → termine|interrompu|incident → verification → resultat`. La vérification ne relance pas le chronomètre. L’aperçu de consigne utilise des exemples distincts de la liste mesurée.

Exigences :
- Accès secondaire « Prototypes », sans nouvelles cartes imposées sur l’accueil principal ; aucune épreuve ne se lance à l’ouverture de cette rubrique.
- Une consigne principale, une zone de tâche et une action principale par étape. Aides et détails repliés. Retour clavier et focus cohérents.
- Conserver le fond ardoise mat ; aucun flash, défilement animé, pulse, son de compte à rebours ou célébration.
- Bouton audio unique : « Écouter » au repos, SVG haut-parleur barré pendant la lecture ; emplacement et dimensions stables, nom accessible « Arrêter la lecture ».
- La consigne peut être lue avant le départ. Aucune synthèse ne joue pendant une mesure orale de couleurs.
- « Terminer » reste accessible pendant l’épreuve, sans confirmation temporisée. Les réponses déjà reçues sont conservées. Le résultat porte `interrompu`, sans extrapolation vers une séance complète.
- Chrono discret, sans changement de couleur ni alerte visuelle ; masquer son affichage est une préférence de confort conservée et tracée.
- Zoom 200 %, clavier, lecteur d’écran, préférence de mouvement réduit et viewport de 375 px vérifiés. Les listes de 50 doivent rester lisibles : pagination instantanée si elles ne tiennent pas, jamais réduction forcée des caractères. La pagination et le viewport sont tracés pour les comparaisons.
- Résumé bref et « Retour à l’accueil » principal ; métriques et comparaison sous « Voir les détails ». Aucune injonction à terminer la série, aucun taux d’observance.

### Réglages persistants et mode dérogatoire

Le navigateur conserve modalité, voix, dispositif de saisie, visibilité du chrono, profil et mode dérogatoire. Aucun bandeau « mode dérogatoire actif ». Le commutateur reste dans Réglages.

Les profils usuels sont accessibles normalement. Les overrides de durée, taille de liste, délais, complexité et dépassement de limites apparaissent uniquement en mode dérogatoire. Les modifications prennent effet au prochain départ ; la configuration d’une épreuve en cours est figée. Désactiver le mode suspend les overrides sans effacer leurs valeurs ; revenir au mode rétablit ces valeurs. Si le stockage local échoue, repli sur les valeurs par défaut et message discret dans Réglages.

Les aides ne révèlent pas de réponse pendant Mesure personnelle. Les données de familiarisation sont séparées dans les vues ; elles ne deviennent pas des mesures par un simple changement de mode.

## 3. Temps, interruption et familiarisation (P0)

Les durées de 45 secondes et les listes de 50 sont les paramètres demandés par l’utilisateur, pas des normes. Toute variante est explicitement tracée.

- Utiliser une horloge monotone côté client (`performance.now`) pour présentation et capture, plus une date de séance côté serveur. Le temps réseau et la préparation de la dictée sont exclus du temps actif.
- Vérifier la disponibilité du microphone avant départ ; démarrer le chrono seulement quand la capture est prête et la liste réellement visible. Si la visibilité ou la capture ne peuvent pas être datées, ne pas produire de temps de réaction.
- Un passage en arrière-plan, une perte de capture ou un rechargement interrompt la mesure. Ne pas la reprendre comme si elle avait été continue. Conserver l’état et proposer un nouveau départ volontaire, dans un nouvel essai lié au précédent.
- Familiarisation : exemples courts, correction autorisée, pause/reprise possible. Mesure personnelle : pas de correction pendant les couleurs ; la correction différée de la tâche du §4 fait partie du stimulus, elle n’est pas supprimée.
- Entre deux épreuves, écran stable avec « Continuer quand je suis prêt » et sortie. Aucun minimum de repos thérapeutique inventé. Une batterie regroupe A/B/C dans cet ordre mais chaque départ est volontaire ; noter l’ordre et le temps de repos.

## 4. Attention différée : contrat de réponse (P0)

Identifiant de famille : `attention-differee`. Profil initial proposé : 6 questions, écrit, un item de décalage. Banque originale avec questions, réponses admises et version ; niveau = difficulté du contenu, sans inférence sur les capacités.

Déroulement déterministe :
1. Présenter Q1. Recueillir R1 explicitement et la verrouiller sur « Enregistrer et continuer » ; « Je ne sais pas » enregistre une absence déclarée.
2. Présenter Q2 entièrement, sans correction de Q1. En oral, attendre la fin réelle de l’énoncé ; en écrit, l’utilisateur active « J’ai lu la question ».
3. Afficher la correction de Q1 dans une zone séparée nommée « Question précédente ». En écrit, Q2 reste consultable. En oral, conserver le même support écrit pour la modalité mixte ; la modalité purement orale est une variante distincte.
4. Après acquittement de cette correction, recueillir R2 ; poursuivre le même cycle.
5. Après R6, un écran de clôture révèle sa correction, sans fausse Q7. Ce dernier item est marqué `sans_interference_suivante` et exclu des analyses de délai entre nouvelle question et correction.

Chronométrer séparément : acquisition de réponse (activation de la zone de réponse → verrouillage), présentation de question et correction précédente. Ne pas appeler l’ensemble « temps de réaction ». Une absence mentale sans saisie est `non_observable`, pas une erreur.

En Familiarisation, proposer des explications après les corrections. Variantes P1 : oral/mixte, délai additionnel, deux questions intercalaires avec une file de corrections explicitement étiquetées et vidée à la fin. Chaque variante a sa propre version de protocole.

Critères : Q1 n’est jamais corrigée avant la présentation complète de Q2 ; R1 ne peut plus être modifiée après correction ; chaque correction correspond au bon identifiant ; le dernier item reçoit sa correction ; une sortie avant réponse ne transforme pas les questions futures en omissions.

La culture générale peut influer sur les réponses : les résultats restent des comptes de cette tâche, pas une mesure isolée de l’attention.

## 5. Reproduction de figures (P0 / P1)

Famille : `figure-reproduction`. MVP : palette de formes, modèle original composé de 4 éléments, exposition proposée de 15 s, reproduction sans délai imposé. Ces valeurs sont des choix de prototype modifiables en mode dérogatoire.

Phases : consigne → départ volontaire → exposition → masquage complet → reconstruction → validation → comparaison côte à côte. Ne pas laisser le modèle dans le DOM accessible, un canvas secondaire ou un panneau d’aide après masquage. La comparaison apparaît uniquement après validation.

P0 : formes prédéfinies sélectionnables, ajout, déplacement, taille, rotation, suppression et annulation. Alternative aux gestes : boutons ou champs permettant le déplacement et l’ajustement au clavier. Coordonnées normalisées au canevas pour gérer le redimensionnement ; cibles confortables et noms accessibles. Conserver modèle versionné, liste des objets et image de la production locale.

Retour MVP : images côte à côte et description factuelle des éléments présents, absents ou ajoutés uniquement lorsqu’une correspondance est certaine. Pas de pourcentage global de mémoire. Les ambiguïtés restent à vérifier.

P1 : dessin libre souris/stylet/doigt avec annulation, image conservée et comparaison manuelle ; un changement de dispositif ou de mode rend les séances distinctes. Difficulté contrôlée par nombre d’éléments, intersections, orientation et proportions, sans adaptation automatique.

P2 : étude séparée de correspondance géométrique avec tolérances documentées et cas adverses ; aucun score automatiquement interprété comme capacité mnésique. Les performances motrices et le dispositif restent des facteurs de la tâche.

Critères : modèle inaccessible après exposition ; annuler restaure le dernier état ; redimensionner conserve les positions relatives ; quitter conserve uniquement ce qui a été produit ; comparaison impossible avant validation.

## 6. Trois séries de couleurs (P0)

Familles `couleurs-lecture`, `couleurs-denomination`, `couleurs-interference`. Chaque essai dure 45 s et utilise 50 stimuli en boucle. Ordre de lecture fixe gauche→droite puis haut→bas, illustré avant départ ; chaque occurrence est identifiée par `(liste_id, cycle, index)`.

Profil initial de prototype : quatre couleurs — rouge, bleu, vert, jaune — avec codes sRGB figés par version de stimulus et noms admis définis dans le contenu. L’équilibrage de 50 utilise des comptes 13/13/12/12 ; la permutation est déterministe par famille/graine. Dans la condition incongruente, aucune paire mot/encre identique. Les triplets A/B/C utilisent les mêmes effectifs de mots/encre/carrés, pas uniquement le même vocabulaire.

| Série | Stimulus | Réponse attendue |
|---|---|---|
| A | Nom de couleur en noir | Lire le mot |
| B | Carré coloré | Nommer la couleur |
| C | Mot avec encre d’une autre couleur | Nommer l’encre |

A utilise une surface locale claire, mate, limitée à la zone de tâche, pour rendre le noir lisible ; cadre de l’application sombre inchangé. B/C utilisent également cette surface pour ne pas introduire une différence de fond entre conditions. Montrer cette surface avant départ pour que l’utilisateur puisse vérifier son confort. Une variante sur fond sombre est possible, versionnée séparément, avec texte neutre clair en A ; elle n’est pas mélangée aux résultats de la variante noire.

La palette doit être lisible sur cette surface ; une difficulté à distinguer les couleurs permet de quitter ou choisir une autre activité. Ne pas remplacer la couleur par son nom pendant B/C : cela changerait la tâche. Ne pas présenter ces variantes comme accessibles à tous les profils visuels.

Aucun feedback de justesse pendant l’essai, aucune synthèse de stimulus. Retour au début de liste sans flash ni animation. Si une pagination est nécessaire, utiliser une action explicite « Suite » et journaliser ce changement ; ne pas déduire la position de la seule reconnaissance vocale.

### Comptage oral et vérification

P0 : capture locale disponible, transcription brute avec horodatages de segments quand disponibles, écran de vérification après les 45 s. Repli : observation et comptage manuels si capture non disponible ; sans capture ni observateur, l’essai reste réalisable mais sans score automatique.

Une liste répétée de couleurs n’offre pas toujours un alignement unique. L’algorithme propose un alignement, garde les ambiguïtés et ne le valide pas silencieusement. Après l’essai, la personne ou l’accompagnant peut confirmer le dernier stimulus tenté, la correspondance réponses/stimuli et les erreurs de reconnaissance. Conserver l’alignement suggéré et sa révision, avec auteur/type de correction et date.

- Les tokens de réponses lexicales sont distincts des événements de reconnaissance, qui peuvent répéter un résultat provisoire.
- Une autocorrection liée au même stimulus avant passage au suivant compte une seule réponse finale ; conserver la première réponse et la correction spontanée à part.
- Une répétition vocale ne fait pas avancer automatiquement d’un stimulus.
- Une omission est comptée uniquement pour un stimulus confirmé comme sauté entre deux réponses alignées. Les stimuli non atteints à 45 s ne sont pas des omissions.
- Les réponses sont éligibles selon le début de leur segment vocal strictement avant la limite ; un segment sans datation suffisante qui chevauche la limite est `a_verifier`. La transcription arrivant après 45 s peut être traitée si la parole correspondante était avant la limite.
- Une réponse mal reconnue est `reconnaissance_incertaine`, pas une erreur cognitive. Les scores définitifs exigent un alignement vérifié ; sinon afficher « Comptage à vérifier » et les comptes provisoires clairement distingués.
- Aucun temps de réaction par item calculé sur la date d’arrivée réseau ou de transcription. Les listes simultanément visibles ne donnent pas une date de présentation individuelle ; un protocole séquentiel nécessiterait une autre version.

Critères : 50 stimuli versionnés ; C toujours incongruente ; arrêt à 45 s selon horloge monotone ; retour de liste journalisé ; résultats ASR provisoires non doublés ; aucun stimulus futur compté omis ; alignement ambigu visible ; révision humaine conservée sans altérer la transcription brute.

## 7. Résultats et comparaison (P0 / P1)

Comptes : réponses correctes `C`, incorrectes `E`, omissions confirmées `O`, éléments ambigus `U`, autocorrections `AC`. Les items tentés comprennent `C+E+O` uniquement après alignement vérifié. Le nombre de réponses prononcées est un autre compte, qui peut inclure répétitions et corrections.

- Précision : `C / (C + E + O)` uniquement après vérification ; dénominateur nul → valeur absente, jamais 0 %.
- Débit correct : `60 × C / duree_active_s`. Un essai interrompu peut afficher ce débit avec sa durée réelle mais il est exclu des comparaisons avec les essais complets.
- A/B/C : tableau disponible à la demande, sans code couleur bon/mauvais ni score composite.
- P1, coût d’interférence descriptif : `(debit_B - debit_C) / debit_B × 100`, seulement si B>0 et deux essais complets compatibles et vérifiés. Valeur négative conservée ; aucun seuil d’interprétation. A reste une référence distincte, pas le dénominateur caché.
- Tendances intra-individuelles seulement, avec même famille, protocole, configuration, modalité, dispositif, mode de présentation et règle de comptage. Sinon afficher « Configuration différente » et les séances séparément. Répétition des stimuli tracée ; aucune amélioration clinique déduite d’une hausse de score.

## 8. Données et intégration technique (P0)

Stockage local séparé du stockage entraînement selon ADR-002. Aucun accès aux historiques FSRS ni jointure automatique pour régler ces prototypes. Aucun service tiers pour voix, transcription ou image. Conservation d’un audio éventuel facultative et explicite, désactivée par défaut ; suppression locale de l’essai et de ses fichiers associés disponible. Les images produites, transcriptions et réponses ne sont ni commitées ni envoyées en télémétrie.

Contrat proposé à figer lors de l’implémentation dans l’ADR/API dédié :
- `session_id`, `schema_version`, `protocol_version`, `family`, `mode`, date et statut ;
- configuration effective immutable, profil, overrides, graine, `stimulus_ids`, empreinte de contenu ;
- ordre, pagination, viewport, dispositif, modalité, voix, capture et règle de segmentation ;
- événements de présentation/response/correction/arrêt horodatés monotoniquement, durée active et motif d’interruption ;
- transcription brute et révision, alignement proposé/vérifié, ambiguïtés, réponses normalisées ;
- image et objets de reproduction, référence du modèle ;
- métriques dérivées, version du calcul et état provisoire/vérifié.

Une sauvegarde répétée d’un même événement est idempotente. Échec réseau : garder le brouillon, permettre réessai sans doubler les réponses ; ne pas poursuivre une mesure orale après perte de capture. Échec persistance : informer que le résultat n’a pas été enregistré, garder une sortie accessible.

Contenus originaux, génération isolée par famille et IDs dérivés du contenu ; aucune régénération d’un contenu déjà servi. Schémas, tests et règles de correction versionnés avant premier usage. Libellés centralisés selon les conventions du dépôt. Les limites de séances restent proposées selon la doctrine existante ; toute dérogation passe par le mode prévu au §2.

## 9. Livraison et validation

| Lot | Livrable | Condition de sortie |
|---|---|---|
| 1 — P0 | Infrastructure, configuration, états, sauvegarde séparée, consignes, sorties | Cas sans microphone, interruption, rechargement et erreurs réseau vérifiés ; absence d’exposition de données réelles |
| 2 — P0 | A/B/C avec vérification humaine | Cas limites de 45 s, ambiguïtés, boucle, omissions et autocorrections couverts ; aucun score présenté comme vérifié sans confirmation |
| 3 — P0 | Attention différée, un item de décalage | Tests d’ordre des corrections, verrouillage de réponse et dernière question |
| 4 — P0 | Figures avec palette | Masquage complet, clavier, annulation et persistance testés |
| 5 — P1 | Dessin libre, variantes, comparaison | Versions/configurations incompatibles exclues des tendances |

Pas de date imposée. Les premiers lots peuvent être essayés séparément sans attendre une batterie complète.

Validation : scénarios déterministes sur événements fictifs pour les mesures ; inspection mobile/desktop/zoom 200 % ; clavier et lecteur d’écran ; mouvement réduit ; essais de confort courts et interrompables avec les personnes concernées. Collecter les difficultés d’usage sans objectif de complétion, de fréquence ou d’observance. Une relecture clinique/métrologique peut préciser l’interprétation ultérieure ; elle n’est pas présentée comme déjà obtenue et n’empêche pas le développement du prototype local.

Décisions restantes, ciblées : conception/ingénierie doivent figer les codes couleur et vérifier leur contraste avant livraison B/C ; ingénierie doit vérifier les horodatages effectivement fournis par la dictée locale avant de promettre des mesures individuelles ; revue du contenu doit fixer les réponses admises des 6 questions. Si ces dépendances échouent, proposer comptage manuel et données brutes, jamais remplacer les informations manquantes par des scores inventés.

## 10. Pistes conservées, hors version 1

N-back visuel/auditif, double tâche, séquences spatiales de type Corsi, recherche visuelle avec distracteurs : à reprendre chacune dans une fiche séparée avec consigne, réponses, règles de mesure, conditions de sortie et impact sur la charge. Aucun ajout à la remédiation fonctionnelle par défaut. Le scoring automatique du dessin et l’adaptation de difficulté restent également des études séparées.

## 11. Remplacement de cette spécification

Ce document devient la source de travail unique pour ces prototypes. Une version plus précise pourra remplacer ses exigences ; mettre à jour le lien de feuille de route et la référence ADR dans le même changement. Supprimer alors le document supersédé si aucun lien actif ne le requiert : Git conserve la trace historique. Ne pas garder simultanément une ancienne TODO et une spécification concurrente.
