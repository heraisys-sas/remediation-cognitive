# 2026-09-30 — Dérogation explicite à la limite de séances (accueil)

Demande d'Olivier : un commutateur sur l'accueil pour désactiver le plafond de séances du jour (anti-fatigue). Implémenté sur la branche d'essai (`deduction-corrections`), ADR-021.

- Backend : `DemarrageOptionnel.sans_limite_sessions` ; dérogation accordée aux thèmes d'**entraînement** seulement (l'évaluation reste à 1/jour). Le compteur du jour continue de compter (désactiver le réglage retrouve l'état réel). Règle du domaine : `dosage.derogation_limite_sessions`.
- Interface : commutateur `#case-sans-limite` en bas de l'accueil (au-dessus de Programme/Missions/Repères), réglage conservé (localStorage `remediation.sansLimiteSessions`, comme la lecture automatique) ; note d'accompagnement qui change d'état ; résumé de fin adapté ; message 429 propre à l'évaluation.
- Pièges : le contrôle Node `verifier_session.js` exécute le VRAI `demarrerSession` — tout nouvel appel (ici `sansLimiteActivee`) doit être stubé dans son harnais et couvert par un scénario ; le type d'erreur JS s'écrit `"reseau"` (sans accent) dans app.js.
- Contrôles : `node tools/verifier_session.js` vert (2 scénarios ajoutés, 5 au total) ; pytest complet à rejouer après cette session. Serveur :8000 non redémarré — redémarrer pour voir le changement en ligne.
