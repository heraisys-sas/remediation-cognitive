# Application des stratégies — lot 4

10 octobre 2026 — lot 4 V3 enrichi et validé automatiquement en local, après GO de poursuite et arbitrage GPT Astra ultra. Les [fiches EX-REV-005 à 008](corrections-exercices-existants.md) gardent leurs objectifs et fondements ; ce document décrit la version servie. Les anciens QCM, contenus et historiques restent disponibles. Cette livraison locale ne constitue pas une intégration dans `dev` ou `main`.

## Quatre simulations originales

Chaque parcours dispose de **douze situations originales**, sous le protocole `strategies-appliquees-v3` : 48 scénarios actifs au total. Ils gardent la même structure de tâche et varient la situation, les informations ou les documents. Leur rotation n’est ni une progression de difficulté ni une adaptation clinique. Aucun candidat du lot 5 n’est sélectionné ou inclus.

| Parcours | Déroulement effectivement implémenté | Résultats distincts |
|---|---|---|
| Préparer et utiliser un plan | Dossier, inscription à un atelier ou prêt de matériel ; trois actions compléter/signer/joindre, contraintes visibles ; enregistrer l’ordre initial ; annoncer joindre avant signer ; réviser sans imposer un changement si déjà compatible ; exécuter ; vérifier sans révélation ; terminer | Compatibilité plans initial/final et exécution ; ordre des actions, vérification réalisée. Tous les ordres valides acceptés |
| Utiliser un rappel | Dossier/pièce d’identité, réservation/billet ou matériel/liste ; intention si–alors puis choix de pièce et condition avec/sans rappel ; deux vérifications simples ; signal propre au scénario ; ouvrir le rappel facultatif ; joindre une pièce ; fermer l’occasion explicitement | Programmé, délivré, ouvert ; action au signal, incorrecte, prématurée si réalisée ou occasion terminée sans action. Sortie avant signal interrompue |
| Prendre un message | Appeler le secrétariat à 15 h, envoyer le formulaire à 10 h ou imprimer le billet à 18 h ; note facultative par défaut, condition sans note distincte ; masquer ; restituer quoi/quand ; réaliser l’action et choisir l’heure ; correction | Restitution et action séparées. Note présente/ouverte, aides et pause. Production libre incertaine à vérifier ; équivalences horaires explicites |
| Estimer et organiser son temps | Quatre documents à classer : factures/courrier, voyage/santé ou cuisine/jardin ; estimer la durée ; classer les documents visibles ; examiner la comparaison ; préparer une marge | Classement, estimation, temps actif, pauses, durée écoulée et attente interface séparés ; écart signé actif moins estimation, sans note de capacité |

## Rotation et conservation

Le serveur choisit la variante suivante à partir de la dernière séance persistée du même parcours : 1 → 2 → 3 → 1. La rotation survit au redémarrage, est commune aux conditions avec/sans note et avance dès l’ouverture enregistrée, même si la séance est ensuite interrompue. Elle ne dépend ni de la réussite, ni des aides, ni de la durée. La première variante V2 reprend la situation initiale ; ouvrir V2 après des séances V1 peut donc présenter un contenu déjà rencontré.

Chaque journal conserve `version` et `scenario_id`, et le résultat restitue ces références. Le contenu et les réponses attendues restent dans la banque versionnée ; les quatre scénarios V1 y sont conservés. Un ancien journal sans `scenario_id` retrouve le scénario original de son parcours et garde sa version ainsi que sa tolérance historique de correction horaire. Aucun résultat historique n’est recalculé selon les nouvelles tolérances V2.

Pour le rappel, le texte de l’intention est retiré après configuration. Un rappel révélé suit la pièce effectivement configurée, même erronée ; il n’est pas silencieusement corrigé. L’action prématurée est possible dans l’API et distinguée, mais l’interface présente l’action de joindre seulement au signal : aucune absence de précocité ne peut être déduite de cet accès.

Les notes restent en mémoire locale de la page, sans texte envoyé au serveur ni conservation après fermeture de séance/page. Une ouverture montre une consultation de l’outil, sans prouver une lecture mentale. Dans la condition sans note, message et restitution précédente sont retirés de l’écran et de la lecture pendant l’action. Le bouton « Revoir le message » réexpose l’encodage, avec lecture facultative via « Écouter ». La réexposition et la pause avec reprise d’encodage sont tracées comme aides ; la première restitution reste conservée.

La correction de « quoi » utilise des formulations explicitement admises par scénario ; une autre production non vide reste « À vérifier ». Les heures attendues acceptent leurs formes chiffrées et certaines formes écrites explicites, par exemple « 15 », « 15 h », « 15 heures », « 15:00 » et « quinze heures ». Aucune similarité sémantique ni interprétation d’une intention non saisie n’est ajoutée.

## Durée, confort et sauvegarde

Mesure locale monotone par segments de classement ; réseau hors temps actif, pause explicite et invisibilité séparées. Une perte de visibilité invalide la comparaison. Serveur vérifie types, bornes et somme actif + pauses + attente interface = écoulé ; données incohérentes donnent une comparaison absente. Ce sont des observations déclarées par le client, pas une mesure clinique contrôlée. Chrono masqué pendant la tâche, aucun délai éliminatoire.

Une étape active, une commande principale, arrêt de séance accessible, pauses et brouillons conservés dans la page. Lecture commune locale avec bouton Écouter/pictogramme muet. Clavier et téléphone pris en compte. Le bouton principal garde le focus ; la saisie multiligne conserve Entrée.

API et journaux indépendants dans `strategies`, sans modification FSRS, score composite ou reclassement des anciens résultats. Chaque transition est validée au serveur. UUID d’étape et contenu exact conservés pendant retry : un échec bloque la progression, une confirmation durable autorise la suivante. Même étape rejouée avec autre contenu refusée. Fin répétée idempotente ; sortie partielle qualifiée interrompue sans correction complète. Trois ouvertures par jour, dérogation explicite existante.

## Vérification et limites

Tests des ordres valides, transitions et premières réponses, clôture et retry après redémarrage, rotation des douze situations de chaque parcours, conservation des journaux V1, masquage des réponses attendues, aides et notes exclues du serveur, rappel configuré réellement consulté, absence/signal et action prématurée, équivalences horaires conservatrices, temps signé et capture incohérente. Tests Node du retrait DOM/audio, retry identique, note locale, pause/visibilité, réseau hors temps actif et contrainte annoncée après sauvegarde.

Validation initiale de la V2 (avant enrichissement) : **476 tests pytest réussis, 1 ignoré ; 71 tests Node réussis**, dont 26 pour les stratégies, 35 pour les mémoires et 10 pour les contextes. Ruff et le contrôle d’interface passent. Détails et état de recette dans le [plan](plan-developpement-cognitif.md#lot-4--livraison-locale-v2).

La relecture professionnelle et l’essai avec le public visé restent à réaliser. Douze situations par parcours ne constituent pas des formes psychométriquement équivalentes. Pas de reprise UI après fermeture/rechargement ni consultation des anciens journaux. Les anciens QCM restent des introductions, distinctes de ces actions simulées. Ces simulations n’établissent ni efficacité thérapeutique ni transfert réel au quotidien.

## Enrichissement V3 — 10 octobre 2026

Neuf situations supplémentaires par tâche, IDs simulation-4 à simulation-12-v3. Les quatre originaux V1 et douze scénarios V2 restent strictement identiques et résolubles ; les trois scénarios V2 demeurent les premières entrées des banques actives. La rotation continue après la dernière ouverture V2, puis revient après douze situations. Pas de hausse du nombre d’actions, de documents ou d’options. Les nouveaux rappels et messages alternent la position du choix attendu. Relecture éditoriale GPT Astra ultra, sans certification clinique.

La vérification du plan utilise les libellés génériques « actions » et « Vérifier mon plan », adaptés aux cadeaux, sorties et ateliers autant qu’aux dossiers. Contrôles dédiés : 32 tests API, rotation 12+1 pour chaque tâche et conservation des contenus et journaux V1/V2.
