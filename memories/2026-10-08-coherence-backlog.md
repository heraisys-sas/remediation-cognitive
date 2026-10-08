# Revue et suivi — 8 octobre 2026

Revue de PR #22 (main 8b3510b) : scènes versionnées, chargement avant exposition, retrait avant rappel et rejeu compatibles avec la refonte #21. Les deux passes sont intentionnelles (ADR-035) ; le rappel final ne change pas la première réponse retenue pour résumé/FSRS/maîtrise. Test de résumé renforcé, sans modification de cette décision.

Backlog actif clarifié ; #5 et #9 déjà livrés, #10 couvert par simulations Windows/macOS et désormais Linux. #6 reste ouvert : corpus relu, mesures réelles distinctes par fournisseur, mode dégradé et seuils à justifier ; aucune calibration inventée. Prototypes PR #15 intégrés par PR #22, encore sans code. Checkout utilisateur et serveur préservés.

Précision utilisateur en cours de revue : le rappel final est l’exercice, la découverte sert à mémoriser. La conclusion précédente est donc supersédée par ADR-039 et la correction API/client : découverte sans effets sur progression, rappel final seul retenu. Les historiques antérieurs restent inchangés.
