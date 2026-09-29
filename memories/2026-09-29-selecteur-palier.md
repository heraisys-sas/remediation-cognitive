# 2026-09-29 — Déduction : le choix de palier part au serveur

- Défaut confirmé par Codex, reproduit : sélecteur « Essai — palier N » ignoré — POST /sessions sans corps ; un choix palier 2 servait la grille df-1-01.
- Correction : corps JSON {"palier": N} quand un palier est choisi ; auto sans corps (inchangé) ; réessais réseau/bandeau conservent le palier ; `app.js?v=20260929a`.
- Contrôle effectif : `tools/verifier_session.js` exécute le vrai demarrerSession+apiFetch sur fetch simulé (3 scénarios), branché dans pytest (skip si Node absent). Test d'API dédié : forcé/auto/422. Filtrage `selectionner_items` strict par palier — revérifié.
- Pièges : un scanner de blocs JS doit gérer les commentaires français (apostrophes) et ne jamais contenir les séquences délimiteurs de commentaire dans un commentaire ; pytest local 220 passed, 0 skipped.
