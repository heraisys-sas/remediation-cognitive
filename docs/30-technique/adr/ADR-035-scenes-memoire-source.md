# ADR-035 — Scènes illustrées pour retrouver le contexte

## Contexte

L’utilisateur demande de remplacer les phrases de contexte par des scènes générées montrant les messages existants sur leur support. Les scènes sont révélées uniquement par « Afficher », puis masquées avant le rappel. Les images doivent être légères pour le web.

## Décision

Remplacer les dix items rappel-source du palier 4 par dix versions illustrées avec nouveaux identifiants `ev-4-source-image-v1-*`. Messages, options, réponses et durée de 12 secondes restent identiques. La table ancien/nouveau, les contextes et les empreintes sont dans `frontend/images/contextes/manifest.json`. Les autres contenus ne sont pas régénérés.

Champ additif `contenu.affichage.image` : `src`, `srcset`, `width`, `height`, `alt`, `sha256`. Le mode reste `liste`, compatible avec les schémas existants ; ses éléments contiennent le message sans libellé de contexte. Les anciens clients peuvent montrer ce message mais ne présentent pas la scène : utiliser le frontend versionné associé. Les routes et réponses de correction ne changent pas.

Photographies générées avec imagegen intégré à partir des contextes et messages fictifs versionnés, sans donnée réelle. WebP 640/960 pixels, qualité 82 ; 13–112 Ko par fichier. Pas de chargement global ni d'image base64 dans les items. Dimensions réservées et srcset pour sélectionner la taille utile.

La scène n’est demandée qu’après l’action Afficher. Les 12 secondes commencent après chargement et décodage. Un échec ou un délai de chargement de 15 s propose Réessayer et laisse Terminer disponible ; aucune transition automatique au rappel sans scène. Les callbacks de chargement sont ignorés si la phase est annulée.

L’alternative accessible, la voix et la transcription lisible sous la photo donnent le message seul. La transcription est masquée à l’accessibilité pour éviter une double lecture ; l’image porte le même texte alternatif. Les indices visuels du contexte restent par nature non équivalents pour un utilisateur non voyant : aucune équivalence de cette variante visuelle avec une variante textuelle n’est revendiquée. Aucun contexte dans une légende ou dans la synthèse automatique. Le stimulus est retiré du DOM avant rappel.

## Conséquences

Les nouveaux IDs évitent de réutiliser l’historique d’un item textuel sous une présentation modifiée. Le générateur reproduit cette famille depuis le manifeste d’images. Modifier une scène future exige une nouvelle version d’asset, empreinte et identifiant, sans écraser l’asset servi.

Vérification : 98 fichiers de contenu, 0 erreur ; 49 tests backend ciblés ; contrôle générateur/JSON/empreintes ; Chrome sur les dix scènes, révélation, retrait au rappel, réseau lent et image indisponible. Les images sont inspectées visuellement ; la lecture orthophonique reste `a_revoir`.

## Complément — deux passes de contexte (2026-10-08)

La demande précisée conserve la première itération existante : Afficher → scène et message → question sans scène → correction, pour chaque item. À la fin, « Passer au rappel » démarre une seconde itération des mêmes messages dans le même ordre. Les questions arrivent directement sans nouvelle présentation ni phrase de contexte. Les libellés de progression distinguent Découverte et Rappel.

Pendant le rappel, une réponse erronée révèle la scène correspondante dans la correction ; une réponse correcte ne la révèle pas. La correction est vidée au passage suivant, y compris son image. Une image indisponible conserve la correction textuelle. Les assets et leurs poids ne changent pas.

Le client ne programme pas les reprises errorless supplémentaires pour cette variante : tous les items ont déjà un second passage prévu. Les autres parcours gardent leur comportement. L’arrêt volontaire et l’arrêt serveur permettent de terminer avant le rappel. Aucun nouveau contrat API ni changement du moteur : les secondes réponses sont acceptées comme essais supplémentaires. Le résumé et l’historique FSRS existants restent fondés sur les premières réponses ; ce rappel ne fournit pas un score distinct ni une mesure clinique.

Validation : cinq tests Node sans dépendance, test API des deux passes, 50 tests backend ciblés, scénario Chrome mobile complet de 20 réponses, contrôle des images masquées/révélées et absence de débordement.
