# ADR-047 — Actions observables des stratégies

10 octobre 2026 — accepté et implémenté localement, lot 4 V2 autorisé ; intégration dans `dev` et livraison sur `main` non réalisées pour ce lot.

## Contexte

Les QCM permettent de reconnaître une stratégie sans montrer son application. Le lot 4 ajoute des actions simulées de planification, rappel externe, prise de note et estimation, en conservant les QCM comme familiarisation. La première version locale avait un scénario par parcours ; l’arbitrage de poursuite a retenu trois variantes pour pratiquer sur d’autres situations.

## Décision

Le protocole `strategies-appliquees-v2` sert trois variantes par parcours, soit douze scénarios. À l’ouverture enregistrée, une rotation par parcours choisit le successeur de la dernière variante persistée, sans dépendre des résultats. Une interruption ne remet pas la rotation en arrière ; les conditions de note partagent cette rotation. Il n’y a ni nouveau palier ni adaptation clinique.

Les journaux conservent le protocole et l’ID de scénario ; contenu et réponses attendues restent dans une banque versionnée. Les scénarios V1 sont conservés et les journaux anciens sans ID retrouvent leur scénario original. La correction horaire V1 garde sa règle historique ; les nouvelles formes admises concernent V2. Aucun ancien contenu servi ou historique n’est remplacé.

La nouvelle API `/api/strategies` et ses journaux restent hors FSRS et des anciens historiques. L’outil atomique existant est réutilisé uniquement pour lecture/écriture/verrouillage ; pas de moteur générique d’exercices ajouté. Les transitions valident ordre des phases et données admises, verrouillent premières réponses, enregistrent les événements minimaux. UUID client fixe jusqu’à confirmation : retry identique renvoie l’accusé persisté, contenu différent rejeté.

Notes dans la page seulement ; disponibilité et ouverture observées, texte exclu du journal. Conditions aidées séparées. Une clôture partielle est une interruption. Durées locales déclarées validées, réseau et pauses distincts ; mesure douteuse absente. Résultats descriptifs, aucun score global ou attribution diagnostique.

## Conséquences

La banque varie la situation sous les mêmes règles, sans revendiquer une difficulté homogène ou un transfert au quotidien. La correction de production libre reste conservatrice : formulations admises ou « À vérifier ». La création de séance choisit une variante et compte une ouverture ; seule une étape identifiée et la clôture disposent du contrat de rejeu idempotent. Reprise UI après rechargement et consultation des anciens journaux restent hors de cette version.

Voir [spécification réellement servie](../../20-specs/strategies-appliquees.md), tests API/Node et recette du [plan](../../20-specs/plan-developpement-cognitif.md). Le lot 5 reste soumis à sélection explicite. Aucun changement des trois exercices protégés.

## Addendum — enrichissement V3 du 10 octobre 2026

GO utilisateur pour douze situations par tâche : neuf ajouts sous IDs V3, protocole V3 pour les nouvelles sessions. Les banques actives comptent 48 situations ; les 16 contenus historiques restent inchangés. Rotation conservée sur douze entrées, mêmes transitions/charge/observations. Tests de conservation, reprise V2 et passage V3.
