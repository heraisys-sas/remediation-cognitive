# ADR-036 — Rejouer un palier terminé

## Contexte

La personne souhaite une case « Rejouer un palier terminé » sous « Dépasser la limite de séances », activable seulement en mode dérogatoire et conservée à la prochaine visite.

## Décision

La case reste dans les réglages dérogatoires masqués hors mode. Elle est aussi désactivée hors mode. Son choix est mémorisé en localStorage ; couper le mode conserve ce choix mais neutralise son effet. Aucun indicateur permanent ajouté.

Champ API facultatif `rejouer_palier: bool = false` dans le démarrage de séance. Le client ne le demande que si mode et case sont activés. Il autorise à compléter la sélection du palier courant ou choisi avec des items vus non dus, sans attendre FSRS. La sélection reste due/nouvelle en priorité puis non due, avec quota et séparation de parcours existants, y compris les paliers comportant des étapes. Ce réglage ne choisit pas un ancien palier automatiquement : le sélecteur dérogatoire existant permet de le choisir.

La limite de séances est indépendante ; les cartes et la progression ne sont pas réinitialisées. Les réponses jouées sont enregistrées selon les règles habituelles. Sans le champ, la sélection précédente reste identique. Aucune modification du moteur ni des contenus.

## Validation

49 tests backend ciblés dont le rejeu API d’un palier entièrement non dû et les quotas/séparation de palier pour contenu simple ou à étapes. Contrôle Chrome de l’activation conditionnelle, persistance au rechargement, paramètre envoyé seulement avec le mode actif et conservation du choix après désactivation/réactivation. Syntaxe JS et cohérence des identifiants vérifiées.
