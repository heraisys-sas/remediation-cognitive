# 2026-09-30 — Évaluation hebdomadaire et dérogation étendue

Demande d'Olivier : intégrer l'évaluation dans l'exception et passer sa limite à **une séance par semaine** (au lieu d'une par jour). Fait sur la branche d'essai, à la suite du commutateur d'accueil.

- Domaine : `LIMITES_SESSIONS` (limite + fenêtre par catégorie) ; helpers `limite_sessions`, `fenetre_sessions`, `debut_fenetre` (lundi de la semaine). `derogation_limite_sessions` retiré — la dérogation couvre tous les thèmes (la règle, c'est le drapeau lui-même).
- Compteur : la « date » de `compteur-seances.json` est désormais le **début de fenêtre** (aujourd'hui, ou lundi pour l'évaluation) — même format, lecture inchangée (début stocké ≠ attendu → 0). Conséquence : les compteurs d'évaluation existants (datés du jour) sont lus comme fenêtre vide une fois — sans conséquence en essai familial.
- Contrat : champ additif `fenetre_sessions` dans le résumé de fin ; l'interface phrase par fenêtre (« ta mesure de la semaine »). Refus 429 de l'évaluation : « déjà faite cette semaine ».
- Outil : `tools/reinitialiser_seances.py` rouvre la fenêtre réelle (jour / semaine) et importe le domaine pour connaître la catégorie.
- Pièges : tester la réouverture hebdomadaire exige l'horloge injectée (`creer_app(..., horloge=...)`).
- Contrôles : `pytest` 254 passed ; `node tools/verifier_session.js` vert ; l'outil en dry-run montre « journée du 30/09 » (entraînement) et « semaine du 28/09 » (évaluation). Serveur :8000 toujours sur l'ancien code (non redémarré).
