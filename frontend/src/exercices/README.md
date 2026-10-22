# Répertoire réservé aux exercices

Les comportements livrés sont dans `frontend/src/exercises/`. Le catalogue serveur définit les parcours disponibles. « Position dans une séquence » pose une question après la série ; son type interne `n-back` n’est pas un n-back continu.

CPT, double tâche, Trail Making, Stroop et véritable n-back restent des candidats ou prototypes documentés, sans implémentation dans ce répertoire. Voir `docs/20-specs/plan-developpement-cognitif.md` et `docs/20-specs/candidats-cognitifs.md`.

Les quatre pratiques guidées de mémoire immédiate sont implémentées dans immediate-sequences.js, immediate-visual.js et le socle immediate-memory.js ; API dédiée sans FSRS. Voir ADR-045.
