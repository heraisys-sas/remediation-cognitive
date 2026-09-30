# ADR-021 — Dérogation explicite à la limite quotidienne de séances

Date : 2026-09-30. Statut : adopté sur la branche d'essai.

Demande d'Olivier : pouvoir désactiver, depuis l'accueil, la limite du nombre de séances du jour (anti-fatigue) — sans passer par un outil en ligne de commande.

## Décision

Un commutateur « Dépasser la limite de séances du jour » est placé sur l'accueil, dans la zone des accès secondaires (au-dessus de Programme / Missions / Repères). Il lève le plafond de séances du jour **pour les thèmes d'entraînement** ; l'**évaluation reste plafonnée à une séance par jour** (répéter une mesure la fausse — règle antérieure conservée).

- Le réglage est conservé côté client (`localStorage`, comme la lecture automatique), **désactivé par défaut** ; son état reste visible sur l'accueil.
- Chaque démarrage de séance transmet `sans_limite_sessions` dans le corps `DemarrageOptionnel` ; **c'est le serveur qui accorde ou refuse** — l'interface ne contourne pas la règle, elle la demande explicitement (contrat d'API mis à jour).
- Le **compteur du jour continue de compter** toutes les séances, y compris sous dérogation : le dosage reste juste, et désactiver le réglage en cours de journée retrouve l'état réel.
- Le résumé de fin de séance remplace la ligne « séances restantes » par « Limite levée… » lorsque la dérogation est active (entraînements).

## Conséquences

- La limite de séances du jour n'est plus « non contournable » : elle devient un **défaut actif + une dérogation explicite**, honorée côté serveur et vérifiée (tests d'API ; contrôle JS de la requête réellement construite).
- Aucun changement de contenu, du moteur, du critère de maîtrise, ni des autres garde-fous (durée proposée, fatigue proposée).
- `tools/reinitialiser_seances.py` reste l'outil d'exploitation (remise à zéro du compteur) ; le commutateur ne le remplace pas.

## Ajustement du 30 septembre (soir)

Demande d'Olivier : intégrer l'évaluation dans l'exception, et ramener son plafond à **une séance par semaine** (au lieu d'une par jour). La fenêtre d'évaluation est la semaine calendaire (lundi–dimanche) ; la dérogation lève la limite pour la fenêtre en cours, comme pour l'entraînement. Le motif du plafond ne change pas — répéter une mesure la fausse — et l'espacement hebdomadaire le sert mieux qu'un plafond quotidien ; la dérogation reste un choix explicite de la personne. Conséquence technique : le compteur stocke désormais le **début de fenêtre** (le jour, ou le lundi pour l'évaluation) ; le résumé de fin expose `fenetre_sessions`.
