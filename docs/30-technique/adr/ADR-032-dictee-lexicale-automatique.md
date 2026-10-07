# ADR-032 — Dictée lexicale automatique

## Contexte
La réponse orale peut éviter un détour par l'écriture dans le rappel lexical. Le démarrage manuel faisait perdre le début de certaines réponses. Une hypothèse provisoire de reconnaissance ne doit pas devenir une erreur d'exercice.

## Décision
Limiter l'automatisme aux items `evocation/rappel-indice`. Préparer le microphone natif pendant la lecture, sans conserver ni transcrire ses échantillons. Après la lecture (ou immédiatement si elle est désactivée), activer la capture destinée à la dictée strictement locale. Afficher les transcriptions successives et attendre 700 ms sans changement avant une vérification serveur sans effet sur la séance. La route POST `/{theme}/sessions/{session_id}/verifier-dictee` reçoit `item_id` et `transcription` (500 caractères maximum) et renvoie seulement `acceptee`.

Le correcteur lexical habituel reconnaît le mot, les variantes déclarées et les courtes contextualisations ; une négation interdit la validation automatique. Aucun seuil de similarité sémantique n'est ajouté aux réponses lexicales strictes. Seule une réponse acceptée passe par la soumission ordinaire, une fois, avec les indices consultés et le temps écoulé.

Le bouton « Répondre au clavier » arrête l'écoute, invalide les contrôles en cours, vide le champ et lui donne le focus. Le changement d'item ou d'écran annule également l'écoute. Relire la question suspend la capture pour ne pas reconnaître la voix de synthèse.

## Conséquences et limites
Les séries, nombres, QCM et productions en plusieurs étapes gardent leur fonctionnement. Refus du microphone ou panne de vérification permettent une saisie manuelle. La stabilisation temporelle est un compromis ergonomique, pas une mesure de confiance de reconnaissance. Le flux local fonctionne par retranscriptions cumulatives ; la latence dépend du poste. La première ouverture peut nécessiter l'autorisation micro du navigateur.
