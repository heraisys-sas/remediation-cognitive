# ADR-030 — Interface discrète et mode dérogatoire persistant

## Contexte

Le public fatigable doit pouvoir commencer sans lire les réglages d’essai. L’utilisateur demande de conserver le mode dérogatoire et les réglages entre visites, sans bandeau d’état.

## Décision

Regrouper les réglages de voix et le mode dérogatoire dans un panneau fermé par défaut. Les paliers d’essai et le dépassement de limite apparaissent uniquement en mode dérogatoire. Mémoriser le mode, les paliers par thème/parcours, la modalité et le parcours. Désactiver le mode suspend les dérogations sans effacer les choix. Migrer une ancienne limite levée vers le mode dérogatoire actif.

L’accueil utilise des surfaces mates et des actions sobres. Les ressources, parcours et résultats détaillés sont repliés. La confirmation de fin n’expire plus après cinq secondes. Le résumé propose un retour à l’accueil. Les contenus et le contrat API restent inchangés.

## Conséquences

La persistance utilise le stockage local du navigateur ; en cas d’indisponibilité, fonctionnement normal sans persistance garantie. Aucun indicateur supplémentaire de mode actif. La pause de séance et le découpage des tâches PQRST restent des chantiers distincts : cette évolution n’altère pas les stimuli ni le calcul des temps.

## Vérification

Contrôle des identifiants/routes et syntaxe JavaScript ; Chrome avec réponses API fictives : mode masqué/visible, conservation après rechargement, palier conservé, bypass suspendu en mode normal, absence de débordement à 375/768/1100 pixels. Inspection des captures desktop/mobile. Aucun historique réel créé par ces essais.
