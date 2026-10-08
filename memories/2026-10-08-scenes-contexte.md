# Scènes de source — 8 octobre 2026

L’utilisateur a demandé les contextes en scènes et les messages sur leurs supports. Dix photos imagegen originales depuis FICHES_SOURCE, deux WebP par scène, 640/960 px, qualité 82, 13–112 Ko. Manifeste versionné et nouveaux IDs avec empreinte ; seul palier-04.json remplacé, messages/options/réponses inchangés.

Frontend : Afficher déclenche chargement/décodage puis 12 s ; contexte jamais énoncé ni légendé, message seul transcrit pour mobile ; image retirée avant rappel. Réessayer en cas d’échec, callbacks annulés si phase remplacée. Générateur aligné sur manifeste, sans régénération du thème. ADR-035, README des images et contenu.

Contrôles : validation 98 fichiers 0 erreur, identifiants/routes, syntaxe JS, 49 tests backend ciblés, Chrome dix scènes et scénario réseau lent/erreur, cohérence générateur/JSON/empreintes. Photos contrôlées visuellement. Sources/brutes dans generated_images, assets consommés dans frontend/images/contextes. Aucun push effectué dans cette session.
