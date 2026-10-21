# N-back — observation visuelle à rythme libre

10 octobre 2026 — EX-CAND-010 sélectionné explicitement par l’utilisateur. Destination : Exercices ciblés. Conception relue par GPT Astra au niveau ultra. Version initiale 1-back conservée dans les archives ; version V2 à trois distances explicites, distincte de « Position dans une séquence ».

## Tâche

Choisir 1-, 2- ou 3-back avant démarrage ; le dernier choix est mémorisé, défaut1. À chaque forme après les n premières, choisir Identique, Différent ou une absence déclarée, puis valider. La comparaison concerne exactement n places avant, pas un rappel à la fin de la série. Les n premières formes sont sans décision ni score. Exemple indépendant adapté à chaque n ; familiarisation facultative, corrigée et exclue des données. En1-back, A–B–B–C donne Différent / Identique / Différent.

16/17/18 présentations pour1/2/3-back, toujours15 décisions possibles et exactement cinq correspondances. Quatre formes SVG facilement distinguables, une teinte commune, aucune animation ni changement de place. Générateur isolé et versionné : tirer les positions cibles, copier la forme exactement n places avant sur une cible, choisir une autre forme ailleurs, puis vérifier indépendamment le masque complet des cibles. Une empreinte canonique retire le simple renommage des formes et exclut les structures déjà servies, y compris les archives V1 équivalentes. Tirages sous verrou ; après1000 collisions, erreur explicite sans ouverture ni consommation du quota. Séquence et version conservées au serveur ; aucun historique ni réponse attendue transmis avant fin.

## Déroulement et confort

Consigne initiale avec lecture Écouter/muet commune. Départ volontaire. Un symbole visible ; choix modifiable avant validation, sans choix présélectionné. Après validation, écran neutre sans ancien symbole, sélection ou feedback de justesse ; bouton Suivant pour poursuivre volontairement. Aucune cadence imposée ou temporisation automatique. Corrections seulement à la fin. Lecture des stimuli non proposée pour garder la modalité visuelle ; règle fixe toujours disponible.

La commande « Terminer la séance » et le masquage de l’onglet interrompent le bloc : aucune reprise silencieuse. Les archives et l’API conservent les raisons historiques d’interruption, dont la pause. Seules les réponses validées sont conservées, aucune position future n’est comptée fausse. À la fermeture/rechargement, une requête de clôture keepalive est tentée ; un arrêt brutal ou réseau indisponible peut laisser une archive ouverte, jamais qualifiée terminée ni reprise silencieusement. Une attente réseau ne permet pas une seconde décision ; un retry renvoie le même UUID et les mêmes données. Masquer immédiatement le stimulus lors d’une interruption, y compris pendant une requête.

## Résultats

Correspondances détectées et manquées ; non-correspondances rejetées et fausses alertes ; absences déclarées séparées ; nombre de décisions validées et statut complet/interrompu. Les dénominateurs correspondent aux seules positions répondues, premier symbole exclu. Pas de score cognitif global, diagnostic, norme, temps de réaction ou progression automatique. Les durées éventuellement déclarées décrivent une exposition libre, sans interprétation de vitesse.

Journal indépendant, hors FSRS et ancien type interne n-back. Trois ouvertures quotidiennes comme les autres exercices ciblés ; dérogation existante explicite. Aucun passage automatique selon semaine ou résultat. Les niveaux1/2/3 sont des configurations distinctes ; aucun dual n-back ni protocole à cadence fixe dans cette version.

## Fondements et limites

La mise à jour et la comparaison successive définissent la tâche. Voir l’étude primaire [Transfer of training from one working memory task to another](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2015.00086/full) et les limites de transfert consignées dans [FR-06](../10-clinique/recherche-exercices-feuille-de-route.md). Ces références ne valident pas ce protocole auto-rythmé pour le SPC. Cette observation décrit la séance ; elle ne mesure pas à elle seule la mémoire de travail générale.

## Acceptation

Exemple ABBC exact ; 16/15/5 sur de nombreuses graines ; aucun attendu/historique avant clôture ; premières réponses verrouillées et retries durables ; interruption à chaque phase sans erreurs futures ; sélection effacée et symbole retiré entre positions ; exemple hors journal ; navigation clavier et écran étroit. Vérification technique et recette à consigner dans le journal final.

Validation initiale V1 : 18 tests API n-back et 22 tests Node dédiés ; suite complète 494 pytest réussis (1 ignoré) et 93 Node réussis. Génération vérifiée sur100graines, interruption et masque réseau, dénominateurs nuls et retour du cache navigateur couverts. Recette complète et mobile320px consignée dans [le plan](plan-developpement-cognitif.md#ex-cand-010--véritable-n-back-livré-localement). Aucun commit/push.

## Couverture sur trois mois — V2

Rythme confirmé : cinq séances courtes par semaine **au total**, treize semaines, soit **65 séances réparties entre les cartes**. La V2 vérifie 65 créations persistées distinctes par n, y compris après redémarrage : 195 séries testées au total. Cela couvre ce volume sans exiger une hausse de n. Le niveau reste stable jusqu’à une modification volontaire.

| Niveau | Formes initiales sans réponse | Total de formes | Décisions / cibles |
|---|---:|---:|---:|
| 1-back | 1 | 16 | 15 / 5 |
| 2-back | 2 | 17 | 15 / 5 |
| 3-back | 3 | 18 | 15 / 5 |

Les égalités aux décalages voisins de 1 à n+1, hors n, sont archivées après clôture : une non-cible répétée à une autre distance est un leurre ; une cible présentant une autre égalité est une coïncidence auxiliaire. Elles ne créent pas de fausse correction ou de feedback anticipé. Les résultats d’un bloc interrompu portent uniquement sur les décisions validées. Les archives V1 gardent leur protocole et leurs champs.

Les études primaires [Soveri et al., 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138734) et [Beatty et al., 2015](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2015.00086/full) fondent les distinctions méthodologiques de leurres et de charge. Leurs cadences et volumes diffèrent : elles ne valident pas une dose clinique de 65 séances dans Orthogone.

Validation V2 : 32 tests API et 28 tests Node dédiés ; suite complète 508 pytest réussis, 1 ignoré, et 99 Node réussis. Recette 2-back complète et exemples 2/3-back, initialisations multiples et persistance du choix vérifiées. L’[inventaire des autres cartes](couverture-trois-mois-inventaire.md) exclut anglais/Python et distingue contenu inédit, répétition espacée et montée de palier.
