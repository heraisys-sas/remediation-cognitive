# Inventaire de couverture sur trois mois

État audité le 10 octobre 2026, avant la nouvelle progression du n-back. Hors Anglais — verbes irréguliers et Python, conformément à la demande. Cet inventaire mesure la disponibilité du contenu, pas l’efficacité clinique ni une durée de traitement validée.

## Hypothèse de volume

Trois mois sont représentés par 13 semaines. Rythme confirmé par l’utilisateur : cinq séances courtes par semaine, soit **65 séances au total**, réparties entre les cartes. Il existe **14 cartes** dans ce périmètre : 11 cartes standards, Mémoires immédiates, Application des stratégies et N-back. Les mots lus et entendus occupent une seule carte, avec des parcours et modalités indépendants. Une alternance uniforme représente environ 4,64 séances par carte ; elle est un scénario de dimensionnement, pas une prescription.

Le scénario de stress est différent : 65 séances **dans chaque carte**. Cela demanderait 780 présentations pour un quota de 12, 390 pour un quota de 6 et 260 pour un quota de 4. Aucun stock statique actuel ne garantit 65 séances entièrement inédites dans un seul palier. Répéter après un intervalle peut être utile et prévu par FSRS ; une indisponibilité des items non dus et une répétition volontaire ne sont pas la même chose.

## Stocks statiques et parcours réellement exposés

Les paliers indiqués sont les paliers locaux du parcours. Les nombres sont les identifiants distincts, pas le nombre de questions internes ou de rendus audiovisuels. Les totaux sources peuvent inclure des anciens items qui ne sont plus sélectionnés par les parcours visibles : ils ne constituent pas un stock jouable supplémentaire.

| Carte / parcours | Stock et répartition par palier | Maximum par séance | Observation |
|---|---|---|---|
| Calcul mental | 320 : 18, 14, 18, 18, 24, 24, 24, 36, 36, 36, 36, 36 | 12 | 12 paliers, départ P5 ; seulement 2 à 3 séances inédites complètes par palier adulte. |
| Retenir et manipuler — chiffres dans l’ordre | 55 : 18, 18, 10, 9 | 12 | Départ P3 ; les deux derniers paliers ont moins de 12 items. |
| Retenir et manipuler — chiffres inversés | 36 : 9, 10, 9, 8 | 12 | Manipulation distincte de la restitution endroit. |
| Retenir et manipuler — mots | 72 : 18 par palier, quatre paliers | 12 | Une séance complète inédite par palier, puis une part de nouveautés. |
| Retenir et manipuler — associations | 25 : 8, 9, 8 | 12 | Stock court ; départ P2. |
| Retenir et manipuler — position | 28 : 8, 10, 10 | 12 | Rappel terminal, à distinguer du véritable n-back séquentiel. |
| Mémoriser des séries — immédiat | 24 lus + 24 entendus : 8 par palier et modalité | 4 | Deux séances inédites par palier/modalité. |
| Mémoriser des séries — différé | 4 lus + 4 entendus | 4 | Une séance inédite par modalité. |
| Mémoriser des séries — première série | 4 lus + 4 entendus | 4 | Une séance inédite par modalité ; pas de progression locale. |
| Actualiser une consigne | 36 : 12, 12, 12 | 4 | Trois séances inédites par palier. |
| Comparer deux documents | 36 : 12, 12, 12 | 4 | Trois séances inédites par palier. |
| Repérer l’essentiel | 36 : 12, 12, 12 | 4 | Trois séances inédites par palier. |
| Au quotidien | 88 : 12, 12, 12, 12, 12, 12, 8, 8 | 12 | Une séance inédite aux six premiers paliers ; séances plus courtes ensuite. |
| Déduction | 100 : 20 par palier, cinq paliers | 6 | Trois séances complètes inédites par palier. |
| Méthodes — PQRST guidé | 4 | 12 | Quatre documents, séance nécessairement plus courte que le quota ; pas de progression locale. |
| Méthodes — PQRST rappel | 12 | 12 | Un seul palier ; une séance complète inédite. |
| Méthodes — choisir plan, auto-instruction, vérifier plan, chercher information | 8 chacun | 12 | Un palier par parcours. |
| Garder le cap — reprendre | 12 | 4 | Trois séances inédites. |
| Garder le cap — adapter / vérifier | 4 chacun | 4 | Une séance inédite par parcours. |
| Retrouver le mot | 288 : 24 par palier, douze paliers | 10 puis 8 puis 6 | Départ P2 ; 2 à 4 séances complètes inédites par palier. |
| Retrouver le contexte | 10 scènes et messages avec images distinctes | 12 | Une série peut couvrir les dix scènes, puis rappel sans images : ce rappel ne crée pas dix nouveaux items. |
| Stratégie sémantique / phonologique | 6 chacun | 12 | Une seule banque courte par stratégie, pas de progression locale. |

Sources brutes : Retenir et manipuler 216 items ; Retrouver des mots et leur contexte 350 ; Mémoriser des séries 32 lus et 32 entendus ; Méthodes 48. Les filtres des parcours excluent certains anciens formats. Les quotas sont des plafonds ; le moteur n’invente pas les items manquants. La durée et l’arrêt anticipé peuvent réduire les présentations effectives.

## Génération et variété réelle

| Carte | Capacité / progression actuelle au moment de l’inventaire | Limite importante |
|---|---|---|
| Retenir un code | 12 configurations, 4 exercices par bloc ; P3 initial = 4 chiffres. Sans répétition, nombre de codes = 10!/(10−n)! ; à n=4 : 5 040. | Codes régénérés sans registre global d’exclusion ; un code peut revenir. Répétitions longues : charge accrue, difficulté non strictement monotone. |
| Refaire le chemin | 8 paliers (2 à 9 positions), plateau fixe de 9, 4 exercices par bloc ; à n=3 : 9×8×7=504 chemins. | À n=2 : 72 chemins ; pas de garantie interséance contre les doublons. |
| Quel objet était où ? | 7 configurations, 2 à 6 objets puis rétention accrue ; 4 exercices par bloc. Nombre de placements = n!, donc 6 seulement à trois objets, 720 à six. | La réserve mélangée ne crée pas un nouveau placement à mémoriser. Le bas palier est structurellement répétitif ; conserver cette simplicité si nécessaire. |
| Qu’est-ce qui a changé ? | 7 configurations par condition forme/couleur/association ; 4 exercices par bloc. Tirages de formes/couleurs uniques, positions fixes. | Ne pas déplacer les formes pour fabriquer artificiellement de la nouveauté : cela changerait ce qui est mesuré. Conditions et temps de rétention distincts, pas autant de contenus indépendants. |
| Application des stratégies | 4 tâches × 3 situations = 12 scénarios ; un scénario par séance, rotation circulaire par tâche. | Une situation revient à la quatrième séance de la même tâche. Pas de paliers adaptatifs, ni garantie de renouvellement sur trois mois. Avec/sans note sont des conditions d’aide, pas six scénarios. |
| N-back (version 1-back initiale) | 16 formes, 15 décisions, exactement 5 correspondances ; 4 symboles. 4 × C(15,5) × 3¹⁰ = **709 296 588** séquences admissibles. | Variété énorme mais aucune progression de n dans la version initiale. Nombre combinatoire ≠ prévention explicite des doublons, ni progression ni efficacité validée. |

Les mémoires immédiates montent après deux blocs éligibles avec au moins trois réponses exactes sur quatre ; redescendent après deux blocs avec au plus une. Les anciennes séances, aides et interruptions n’attestent pas la maîtrise. Les parcours statiques suivent leur maîtrise et FSRS, pas un calendrier de déblocage : trois séances consécutives à 90 % pour avancer, avec garde supplémentaire pour les étapes finales présentes. Il est possible de rester longtemps à un palier et de revoir les mêmes items ; on ne doit pas forcer une progression pour remplir le calendrier.

## Priorités de consolidation

1. Programme : l’état audité comporte **8 semaines**, pas 13. Étendre le calendrier sans accélérer ni imposer une montée de palier et sans rattrapage des jours manqués.
2. N-back : prévoir une progression explicite et des traces comparables par n, en conservant la nature observationnelle de la carte ciblée et le rythme libre ; traiter les nouveaux n comme des conditions distinctes.
3. Variété de situation : les stratégies appliquées, le contexte illustré, les rappels différés et première série, PQRST guidé, SFA/PCA et Garder le cap présentent les stocks les plus courts. De nouvelles situations doivent être cohérentes et relues ; ne pas simplement dupliquer un texte avec un nouvel identifiant.
4. Génération : les codes et chemins ont assez de combinaisons pour la variété au palier courant, mais nécessitent une politique de non-répétition si une garantie est annoncée. Les objets à faible charge ne peuvent devenir infinis sans changer leur nature ; des répétitions espacées restent normales.
5. Recette du parcours long : tester date de fin à 91 jours, progression lente, interruptions et rappel FSRS. Les totaux seuls ne prouvent pas l’absence de séance vide à un jour donné.

## Reproduction

`python3 tools/auditer_couverture.py` produit un JSON déterministe des stocks, types, paliers, quotas et hypothèses, sans lire les données utilisateur. Options `--semaines` et `--seances-semaine` pour refaire le dimensionnement. Le rapport est un état initial daté ; le JSON suit les changements ultérieurs du code et du contenu.

## Décisions après audit

Le n-back V2 dispose maintenant de trois paliers volontaires (1/2/3-back), avec 15 décisions et cinq cibles à chacun ; total 16/17/18 formes. Le choix est mémorisé et aucune date ne force une augmentation. L’anti-doublon canonique persistant tient compte des anciens blocs V1 ; 65 créations distinctes **par palier** sont testées, y compris après redémarrage. La réserve couvre donc le besoin de trois mois même si toutes les séances restaient au même n. Cela ne prescrit pas 65 séances de n-back.

Pour les autres cartes, le stock global convient à une alternance sur 65 séances, avec répétition espacée et liberté de rester au palier actuel. Il ne garantit pas 65 séances inédites pour chaque parcours : le tableau ci-dessus signale précisément les banques courtes. L’inventaire initial précède le GO d’enrichissement ; les banques effectivement livrées sont décrites ci-dessous. Le programme logiciel existant demeure de huit semaines : un programme actif de treize semaines nécessiterait une nouvelle version et un choix explicite, sans allonger silencieusement les programmes déjà commencés.

### Exemple de répartition des 65 séances

C’est un dimensionnement possible, pas un calendrier thérapeutique :

| Carte | Séances sur treize semaines | Répartition / répétition prévue |
|---|---:|---|
| N-back | 12 | Dernier niveau confortable, montée volontaire ; au moins65 séries nouvelles disponibles par n |
| Mémoires immédiates | 12 | Environ trois par parcours, paliers selon réponses et confort |
| Application des stratégies | 8 | Deux par tâche : douze situations disponibles par tâche |
| Retrouver des mots et leur contexte | 6 | Alterner mot, contexte et stratégies ; retour des scènes connu et identifiable |
| Déduction | 4 | Progression logique sans changement forcé par semaine |
| Calcul mental | 4 | Paliers actuels, pratique et répétition espacée |
| Méthodes pour retenir et s’organiser | 3 | Parcours au choix ; ne pas confondre quota12 et douze longs documents PQRST |
| Au quotidien | 3 | Situations et stratégies selon palier actuel |
| Garder le cap | 3 | Varier reprendre/adapter/vérifier ; douze situations disponibles pour adapter et vérifier |
| Actualiser une consigne | 2 | Palier actuel et répétition espacée |
| Comparer deux documents | 2 | Palier actuel |
| Repérer l’essentiel | 2 | Palier actuel |
| Retenir et manipuler | 2 | Conditions distinctes, pas deux mesures interchangeables |
| Mémoriser des séries | 2 | Alterner modalité/parcours ; différé et première série ont chacun douze items par modalité |
| **Total** | **65** | **Cinq séances par semaine au total**, jamais cinq par carte |

Une semaine manquée ne se rattrape pas. Ce tableau ne modifie pas les quotas, FSRS, le calendrier existant ou le niveau d’une personne. L’essai d’usage reste à faire. Voir [le contrat n-back actualisé](nback.md).

## Banques enrichies après GO — état final du 10 octobre 2026

Le tableau initial ci-dessus est conservé pour retracer l’audit. Les stocks actuels remplacent les valeurs courtes :

| Parcours | Avant | Livré |
|---|---:|---:|
| Application des stratégies, chaque tâche | 3 | 12 (48 au total) |
| PQRST guidé | 4 | 12 textes |
| Garder le cap — adapter / vérifier | 4 chacun | 12 chacun |
| Rappel différé, par modalité | 4 | 12 |
| Première série, par modalité | 4 | 12 |
| SFA / PCA | 6 chacun | 18 chacun |
| Retrouver le contexte | 10 | 20 scènes illustrées |

Soit **126 nouveaux contenus** : 90 items statiques et 36 simulations. Les sources éditoriales versionnées sous tools/content_sources sont chargées par les générateurs ; leur régénération est testée. Tous les anciens items sont conservés. Les dix nouvelles photos générées avec imagegen intégré sont exportées en WebP 640/960 pixels, 20–41 Ko et 35–71 Ko respectivement ; vingt fichiers pèsent ensemble 767 Ko. Les prompts exacts figurent dans frontend/images/contextes/manifest.json. Textes et supports ont été vérifiés visuellement. Le rappel de contexte conserve dix scènes maximum par séance et les deux passes. Les distracteurs, revus par Astra, restent compatibles avec le message pour réduire la réponse par simple inférence.

Revue GPT Astra ultra centrée sur les nouveaux contenus, consignes et réponses ; ambiguïtés et contradictions corrigées. Aucun point ne nécessitait une nouvelle recherche scientifique : les paradigmes ne changent pas. Métadonnées de relecture orthophonique à revoir ; revue IA distincte de cette validation. Le dimensionnement reste **65 séances réparties**, avec répétitions espacées et progression selon maîtrise. Il ne garantit pas 65 séances inédites dans chaque carte. Le programme actif de huit semaines n’est pas remplacé.
