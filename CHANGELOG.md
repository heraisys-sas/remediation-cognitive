# Changelog

Format : [date] — [périmètre] — description. Les retours informels de l'orthophoniste sont journalisés ici, sans caution clinique.

## 2026-09-03 · Sprint 1 — cycle calcul mental jouable

- **Moteur** — FSRS 6.3.2 (paquet officiel) encapsulé derrière `engine/srs/fsrs.py` ; `SessionRunner` (12 items / 600 s, fatigue = proposition seulement) ; maîtrise 90 % × 3 avec historique par palier ; fenêtre glissante ±1 palier.
- **Contenu** — 191 items : 9 paliers de calcul mental (×2, ×5, ×10, ×3, ×4, ×6, ×7, ×8, ×9 ; 19 items/palier) + échantillons anglais (10 verbes) et Python (10 builtins, production + prédiction de sortie) ; validateur sans dépendance (`tools/validate_items.py`, 0 erreur) ; 100 % original.
- **API** — contrat figé (`docs/30-technique/api-contract.md`) : thèmes, démarrage de séance (sélection due FSRS + nouveaux, réponse attendue jamais exposée), correction serveur par thème, fin de séance (FSRS + maîtrise + persistance JSON sous `backend/data/entrainement/`) ; garde-fous serveur : 3 séances/jour/thème, 12 items, durée max 600 s appliquée (auto-clôture de dosage ≠ fatigue), aucun endpoint bilan.
- **Interface** — SPA vanilla sur `/ui` (sans build) : dark oklch, contrastes ≥ 7:1, zéro clignotement (`prefers-reduced-motion` respecté), une question à la fois, feedback immédiat, bouton « Terminer la séance » toujours visible, alerte d'arrêt bienveillante, a11y (focus, aria-live, inputmode).
- **Revues intégrées** — exécution E2E réelle (serveur + cycle scripté : 24/25 vérifications) et conformité clinique (7 points OK, rien de grave). Correctifs : résumé de séance sur items *répondus* (et non servis), déduplication des essais, verrou sur le compteur journalier, baseline RT adaptative (médiane des temps corrects), durée max serveur, titre d'API neutralisé.
- **Tests** — 96 passed (engine 55 + backend 41), dont tests de régression des quatre constats de revue.
- **Réserves connues** — quota 3 séances/jour *par thème* (global à trancher) ; errorless d'entrée de palier et prerequis anglais/python à compléter ; READMEs de dev servis sous `/ui` ; ADR-003 (front vanilla → React+Vite) à formaliser.

## 2026-09-03 · Cadrage

- **Décision licence** — **BSD-3-Clause** choisie (code et contenu original) ; `LICENSE` rempli. Le dépôt peut désormais être diffusé ; hébergement GitHub créé en privé dans un premier temps.
- **Décision produit** — module Python cadré : mémorisation de concepts et de commandes du langage ; thématique cognitive à double dividende (l'effort de mémorisation est l'exercice, le contenu acquis est une compétence durable). Formats : errorless → production → prédiction de sortie ; cap de complexité de 2 niveaux d'imbrication en phase initiale.
- **Décision réglementaire (rappel)** — scission Entraînement (hors MDR) / Rééducation + Bilan (usage strictement familial) ; voie DM classe I différée en Phase 3.
- **Projet** — création du squelette d'arborescence (monorepo), documentation de cadrage, ADR-001 et ADR-002, schéma d'item normalisé.
