# Dictée native Apple, interface

Le bouton de dictée privilégie maintenant le pont natif lorsque l'application est
ouverte sur localhost/127.0.0.1/::1. Le micro est ouvert dès le clic ; le moteur est contrôlé lors de la transcription.
Capture mono en mémoire, conversion WAV PCM16 16 kHz puis POST vers le même serveur
local. Aucune réponse attendue n'est fournie au transcripteur. L'utilisateur termine
la capture au bouton ; arrêt automatique après 55 secondes. La réponse reste
modifiable avant validation et passe par le correcteur commun.
Annulation et libération du micro au changement d'exercice ; résultats tardifs ignorés.
Le repli navigateur exige processLocally et le pack fr-FR installé, sans téléchargement.
Les autres modifications graphiques présentes dans le checkout ont été conservées.

Correction latence : aperçus cumulatifs toutes les 600 ms sans requêtes concurrentes, résultat remplaçable selon le contexte. Arrêt final sans retranscription si le dernier aperçu couvre déjà tout le signal. Silence signalé explicitement, délai borné. La validation de réponse termine d’abord la dictée et ne juge pas un aperçu provisoire.

Démarrage : suppression du contrôle réseau local préalable à la capture. Le signal « Parle maintenant » attend le premier bloc audio, conservé dans le tampon ; taille de bloc réduite à 2048. Tests de libération du micro après annulation et de signal de disponibilité après premier bloc. Le problème rapporté au micro réel reste à confirmer par l’utilisateur.
