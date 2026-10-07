# Dictée automatique lexicale

Demande : ouvrir le micro après la question, reconnaître une bonne réponse sans essais parasites, permettre le clavier avec champ vidé. Implémentation limitée aux items evocation/rappel-indice. Contrôle serveur sans mutation, orchestration frontend séparée, annulation lors de lecture/changement écran. ADR-032. Modifications natives et interface préexistantes conservées, pas de commit global pour ne pas mélanger le travail concurrent. Vérification réelle avec la voix utilisateur encore nécessaire.

## Premier mot perdu (micro du Mac)
Préparation du micro pendant la lecture, conservation des échantillons seulement après activation. Tests : silence/phrase lus pendant préparation exclus, premier bloc réponse conservé, transitions de lecture et annulation vérifiées. 7 tests ciblés passent. Test du helper sur silence 0,6 s et « gare » tronqué/complet/avec silence final : 0,12–0,15 s, « gare » reconnu sans répétition ; le « oui » utilisateur non reproduit. Pas de capture réelle utilisateur effectuée.

Autorisation avancée avant montrerItem au démarrage de séance lexicale. Flux réservé transféré au premier démarrage de capture, libéré à la sortie. Refus désactive la dictée automatique pour la séance ; la dictée manuelle reste disponible. Tests d'ordre d'exécution, refus, réutilisation du flux et fermeture.
