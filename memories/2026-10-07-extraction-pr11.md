# Extraction critique de la PR #11

Base origin/main acf74b5, branche dédiée extraction-pr11, checkout séparé du travail utilisateur. Source revue c82bb7b. Décisions exhaustives dans docs/30-technique/revue-pr11.md. Stockage concurrent, UTC et corrections TTS ciblées repris ; changements de fatigue, renommages et fractionnement des capacités non repris. Une CI complète remplace les deux workflows. Validation locale : 341 tests réussis, 1 ignoré ; 1046 items, zéro anomalie. Test de concurrence processus utilise spawn avec terminaison bornée, pas fork d'un runtime ayant déjà lancé des threads.
