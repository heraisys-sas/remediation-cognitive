# Plan sprint 1 — Cycle « calcul mental » jouable de bout en bout

## Énoncé de cadrage
J'ai [dépôt remediation-cognitive initialisé + feuille de route Phase 1 + GitHub prêt], l'utilisateur demande [lancer le développement], je livrerai [un cycle complet calcul mental jouable de bout en bout : moteur adaptatif + FSRS + séance + API + interface web + contenu, tests verts, poussé sur GitHub, + rapport de sprint].

## Hypothèses (à rappeler en livraison)
1. Périmètre = première itération Phase 1 : calcul mental complet end-to-end ; anglais et python en échantillons seulement.
2. Interface : SPA vanilla servie par FastAPI (pas de build npm) — ADR-003 à formaliser avant la migration React+Vite.
3. Stockage : JSON locaux hors dépôt (backend/data/, gitignored) pour le module non médical ; chiffrement différé.
4. Les agents ne committent pas : l'orchestrateur intègre, teste, committe et pousse.
5. taskId du cluster : sprint1 (aucun ID fourni par le système).

## Tâches numérotées

### Lot 1 [A1] — Moteur adaptatif
- Agent : moteur-adaptatif — fichiers : engine/** uniquement
- Sortie : .cluster/sprint1/subagent_moteur.md
- Contenu : FSRS (pip fsrs, fallback SM-2 documenté), fenêtre glissante, SessionRunner (12 items / 600 s / fatigue 1,25×RT ou ≥40 % erreurs → proposition d'arrêt), maîtrise 90 % × 3, tests pytest complets.
- Revue (R1/R2) : tests verts ; arrêt jamais forcé ; aucune dépendance backend.

### Lot 2 [A2] — Contenu de départ
- Agent : contenu-exercices — fichiers : content/entrainement/**, tools/generate_items.py, tools/validate_items.py
- Sortie : .cluster/sprint1/subagent_contenu.md
- Contenu : 9 paliers calcul mental (×2,×5,×10,×3,×4,×6,×7,×8,×9) conformes au schéma ; échantillons anglais (10 verbes) et python (10 items builtins, production + prédiction de sortie) ; validateur sans dépendance.
- Revue : validateur passe ; contenu 100 % original (aucun matériel ECPA/Pearson).

### Lot 3 [B1] — API backend (dépend : lots 1-2 + contrat)
- Agent : api-backend — fichiers : backend/** uniquement
- Sortie : .cluster/sprint1/subagent_api.md
- Contenu : endpoints du contrat (docs/30-technique/api-contract.md), stockage JSON backend/data/entrainement/, intégration moteur (sélection des items dus, correction serveur, FSRS/maîtrise en fin de séance), garde-fous serveur (429 à la 4ᵉ séance, réponse attendue jamais exposée avant réponse utilisateur, arret_propose jamais forcé), montage statique /ui, tests TestClient.

### Lot 4 [B2] — Interface web (dépend : contrat ; parallèle au lot 3)
- Agent : interface-web — fichiers : frontend/** uniquement
- Sortie : .cluster/sprint1/subagent_front.md
- Contenu : SPA vanilla dark (oklch doux, zéro clignotement — photophobie), une question à la fois, feedback immédiat, alerte fatigue bienveillante, bouton « Terminer la séance » toujours visible, vocabulaire neutre, a11y (focus, aria-live).

### Lot 5 [R1] — Revue exécution (dépend : lots 3-4)
- Agent : revue-execution — lecture seule, ne corrige rien
- Sortie : .cluster/sprint1/revue_execution.md
- Contenu : pytest complet, uvicorn + cycle E2E scripté (health, themes, session, réponses, fin), garde-fous (429, réponse attendue masquée, absence endpoint bilan), rapport risques code.

### Lot 6 [R2] — Revue conformité clinique/produit (dépend : lots 3-4)
- Agent : revue-conformite — lecture seule, ne corrige rien
- Sortie : .cluster/sprint1/revue_conformite.md
- Contenu : verdict par point (vocabulaire neutre, aucune norme, arrêt proposé jamais forcé, dosage 5–10 min/12 items/3 séances, correction immédiate, contenu conforme et original, séparation des stockages).

## Graphe de dépendances
1 → 3 ; 2 → 3,4 ; contrat → 3,4 ; 3,4 → 5,6 ; 5,6 → intégration → livraison.

## Intégration et livraison (orchestrateur)
Corriger les écarts graves signalés par les revues → pytest complet → commit + push GitHub → rapport de sprint dans DELIVERY/.
