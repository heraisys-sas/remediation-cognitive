# ADR-039 — Le rappel final est l’exercice des scènes de contexte

## Contexte

Précision de l’utilisateur le 8 octobre 2026 : les questions de découverte servent à mémoriser ; le véritable exercice est le rappel final. La première réponse enregistrée par item retenait auparavant la découverte pour résumé, FSRS et maîtrise (ADR-035), ce qui ne correspond pas à cette intention.

## Décision

Champ additif `memorisation: bool = false` dans POST …/reponses. Le client l’envoie à true pendant la découverte des scènes uniquement. Le serveur le réserve aux items rappel-source illustrés et refuse son usage après une réponse de rappel déjà enregistrée. La correction immédiate et la réponse attendue restent disponibles, mais aucun essai moteur, maîtrise, carte FSRS, temps de référence ou reprise supplémentaire n’est enregistré.

Au rappel final, le client ne transmet pas ce champ : la correction et la persistance ordinaires s’appliquent. Le résumé indique « Questions du rappel final ». Un arrêt pendant la découverte conserve une durée de séance mais zéro question de rappel ; l’interface affiche « Rappel non commencé » plutôt que 0 % de réussite. Un rappel partiel ne compte que les questions réellement répondues.

Les scènes, messages et IDs ne changent pas. Les historiques déjà produits par l’ancien comportement ne sont pas réinterprétés : il est impossible de reconstruire les résultats du rappel final à partir de ces premières réponses. La correction vaut pour les nouvelles séances avec le frontend associé. Les autres exercices et anciens clients sans ce champ conservent leur contrat.

## Conséquences

Les erreurs d’encodage restent corrigées sans provoquer une fausse maîtrise ni pénaliser le rappel réussi. Une bonne réponse immédiate ne masque plus une erreur au rappel final. Tests : les deux sens de divergence, absence d’effet FSRS/maîtrise/baseline d’une découverte seule, refus hors scènes, et transition JavaScript entre passes.
