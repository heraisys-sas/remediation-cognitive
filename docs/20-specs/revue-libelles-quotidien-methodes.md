# Revue des tâches et libellés — 30 septembre 2026

**État historique avant correction.** Les défauts de plans, de document masqué et de QCM peu discriminants ci-dessous ont été traités dans [ADR-019](../30-technique/adr/ADR-019-plans-verifiables-et-documents-consultables.md) : 96 items remplacés. Les autres limites décrites ne sont pas assimilées à des défauts résolus.

Lecture des 88 items Au quotidien et des 48 items Méthodes, et du routage de l’interface. Analyse de ce que le logiciel demande effectivement ; ce document ne démontre pas une efficacité clinique.

## Classement retenu

Conserver Au quotidien : les situations courantes en sont le fil conducteur. Pas de rubrique autonome « mémoire de travail » sur la seule base des items actuels. Le palier 1 demande un rappel immédiat d’un détail, sans transformation explicite ni mise à jour pendant une autre activité. Le qualifier exclusivement de mémoire de travail serait trop précis au regard de la tâche.

Méthodes devient « Méthodes pour retenir et s’organiser ». Les descriptions des paliers nomment les actions observables. Le palier 1 rappelle PQRST mais ne guide pas toutes ses étapes ; le palier 6 les fait effectivement pratiquer. Les QCM de choix de plans ne constituent pas à eux seuls un protocole complet de Goal Management Training.

## Au quotidien : couverture des huit familles

| Palier / nombre | Demande réelle | Limite observée |
|---|---|---|
| 1 / 12 | Message affiché puis rappel libre d’un détail | Ni prise de notes ni action réelle à effectuer ; « retenir un message » est plus fidèle que « prendre un message ». |
| 2 / 12 | Choisir la prochaine étape | Certaines conditions manquent : un repas n’implique pas nécessairement de préchauffer un four. |
| 3 / 12 | Donner une durée en minutes | Fourchettes fixes pour des situations dépendant des habitudes et du contexte. |
| 4 / 12 | Reconnaître une première action utile | Ne vérifie pas le passage effectif à l’action ; distracteurs souvent manifestement inadéquats. |
| 5 / 12 | Choisir routine, rappel ou organisation préventive | Toutes les réponses ne sont pas des intentions « si… alors » ; ne demande pas de construire son propre plan. |
| 6 / 12 | Choisir une action parmi trois | Plusieurs réponses visent à prévenir une récidive plutôt qu’à résoudre le problème présent (rendez-vous déjà oublié). |
| 7 / 8 | Choisir un support ou rappel | Chevauchement avec P5 ; certaines préférences sont dépendantes du contexte. |
| 8 / 8 | Choisir une priorité ou une préparation | Pas une mesure ni un entraînement direct de vitesse ; privilégier « prioriser quand le temps manque ». |

## Méthodes : couverture des six familles

| Palier / nombre | Demande réelle | Limite observée |
|---|---|---|
| 1 / 12 | Reconnaître la réponse après masquage du texte | Rappel de PQRST dans la consigne, sans production guidée des étapes. |
| 2 / 8 | Choisir une suite d’étapes | Le but est déjà fourni ; la personne ne le choisit pas. |
| 3 / 8 | Choisir une question à se poser | Reconnaissance d’une auto-instruction, pas formulation autonome. |
| 4 / 8 | Repérer une étape annoncée comme mal placée | Défauts de validité du contenu, voir ci-dessous. |
| 5 / 8 | Reconnaître une information après masquage du document | Décalage avec « chercher dans un document » : le document n’est plus visible à la réponse. |
| 6 / 4 | Séquence PQRST avec question et reformulation produites | Mise en œuvre effective ; correction de reformulation par mots-clés, à distinguer d’une compréhension évaluée sémantiquement. |

## Corrections de contenu à traiter séparément

- Priorité : `mt-4-verif-04` affiche « Verser l’eau / Faire bouillir l’eau / Ajouter les pâtes », pourtant annoncé mal ordonné. `mt-4-verif-06` (« Signer le courrier / Écrire l’adresse / Mettre le timbre ») n’a pas non plus d’erreur d’ordre nécessaire. `mt-4-verif-02` (emballer puis réserver puis transporter) est plausible. Reconcevoir ces items avec des dépendances explicites et une erreur incontestable, nouveaux identifiants et vérification des réponses.
- Méthodes P5 : choisir entre une vraie recherche avec document visible et un rappel après lecture. Le libellé est ici aligné sur le comportement existant ; le décalage de la consigne reste à corriger avec le contenu.
- Au quotidien P2/P4/P5/P6/P7/P8 : enrichir les alternatives plausibles et préciser les contraintes ; un simple renommage ne résout pas la facilité des distracteurs.
- Ces paliers correspondent surtout à des familles différentes : leur numérotation ne démontre pas une difficulté croissante.

## Portée de cette livraison

Descriptions des cartes et manifests, nom de Méthodes, documentation et générateurs de manifests ajustés. Aucun item, réponse, identifiant, score ou parcours déplacé. La description Déduction mentionne aussi le 4×4 désormais disponible. Les limites ci-dessus ne sont pas déclarées résolues par ce changement éditorial.
