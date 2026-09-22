# Changelog

Format : [date] — [périmètre] — description. Les retours informels de l'orthophoniste sont journalisés ici, sans caution clinique.

## 2026-09-22 · Correctif — stabilité du contenu généré (isolation des tirages)

- **Constat (revue de commits)** — au sprint 4, l'ajout des paliers d'empan de mots a consommé 72 tirages sur un générateur aléatoire **partagé entre thèmes** : le thème `concentration`, généré ensuite, a été **réécrit à identifiants constants** (161 items sur 162, contenu différent, structure identique). Passé inaperçu car le message de commit ne parlait que d'ajouts.
- **Correctif** — tirages désormais **isolés par `thème:famille`** (`random.Random(f"{GRAINE}:{thème}:{famille}")`) dans `tools/generer_memo_concentration.py` et `tools/generer_evocation_social.py` ; `generer_rappel_series.py` déjà isolé par construction (une seule famille). Vérifié : générer un thème ne change plus les tirages d'un autre, ni ceux d'une autre famille.
- **Conséquence assumée** — cette isolation a elle-même **remplacé** du contenu : mémoire 216/216 items, concentration 162/162, evocation 24/50 (ordre des propositions), social 32/40 ; calcul mental et rappel de séries intactes. Aucune donnée d'usage n'existant à cette date, la décision est sans effet pour un utilisateur ; elle est consignée ici et dans `docs/30-technique/contenu-versionne.md`.
- **Règle écrite** — nouvelle page `docs/30-technique/contenu-versionne.md` : isolation des tirages, extension en fin de famille, **aucune régénération d'un contenu déjà servi** (remplacer les identifiants si nécessaire), modification annoncée dans le commit, contrôles obligatoires après génération. AGENTS.md pointe vers cette règle.
- **Contrôles** — validateur 53 fichiers / 691 items / 0 erreur ; réponses recalculées 0 anomalie ; 114 tests verts ; déterminisme confirmé (deux exécutions successives → empreinte identique).

## 2026-09-22 · Sprint 5 — programme d'entraînement de 8 semaines

- **Contenu** — `content/programmes/8-semaines.json` : 8 semaines × 7 jours (5 séances, 1 journée légère, 1 jour de repos), durée de 6 à 9 minutes selon la semaine, rotation des thèmes avec décalage hebdomadaire, **plafond de palier** par thème et par semaine (borne haute, jamais objectif). Généré par `tools/generer_programme.py`, validé par `tools/validate_items.py` (structure, thèmes réels, plafonds ≤ paliers disponibles, séance = un thème, repos sans thème).
- **API** — `GET /api/programme` : programme complet + **plan du jour** + règles. La date de début est posée au premier appel et ne bouge plus ; au-delà de la huitième semaine, le programme est « terminé » sans prolongation d'office. Stockage dédié (`backend/data/programme/`) limité à la date de début (ADR-006).
- **Interface** — bouton « Programme de 8 semaines » sur l'accueil (avec les missions) et écran dédié : plan du jour avec démarrage direct du thème proposé, vue d'ensemble des huit semaines, règles en clair.
- **Complexification** — encadrée par les bonnes pratiques : la maîtrise prime sur le calendrier, la fatigue est respectée, une journée manquée ne se rattrape pas, et après deux séances sous 50 % de réussite le palier courant est repris.
- **Vérification** — 114 tests verts (4 nouveaux sur le programme : plan du jour, avancement calendaire, stabilité de la date de début, fin de programme) ; validateur 53 fichiers / 691 items / 0 erreur.
- **Réserves** — relecture orthophoniste à faire ; aucun taux d'observance ni de complétion n'est calculé (ce ne serait pas une mesure clinique).

## 2026-09-22 · Sprint 4 — empan de mots, rappel de séries et correctifs d'usage

- **Correctifs** — le champ de saisie est de nouveau vidé à chaque nouvelle question (régression du sprint 3, vérifiée dans un navigateur) ; le rythme de présentation est rendu explicite (« 3 éléments · un toutes les 0,92 s ») et le blanc inter-éléments passe à 120 ms, ce qui lève l'ambiguïté d'un « environ 2 s » qui pouvait se lire comme une pause.
- **Empan de mots** — nouveaux paliers 9 à 12 du thème mémoire : 3 → 5 mots à l'endroit, puis 3 et 4 mots à l'envers (72 items). L'ordre est significatif ; la saisie est tolérante aux accents et à la casse.
- **Thème « Rappel de séries »** — 4 paliers, 32 items : une série de 4 mots, puis deux et trois séries avec rappel **de l'ensemble**, puis **rappel différé** (20 s d'attente, question sur toutes les séries ou sur la première seulement). Réussite au **seuil** déclaré par l'item ; l'interface affiche les mots retrouvés et manquants.
- **Interface** — section « Extra » regroupant Python et Anglais en bas de l'écran d'accueil ; compte à rebours visible (et passable) pour le rappel différé ; bandeau de série pendant l'affichage ; bilan de rappel sans jugement.
- **Contrôles** — validateur enrichi (rythme d'affichage borné 400–2000 ms, empan de mots, rappel libre : séries, portée, seuil, délai, unicité des mots) ; `tools/verifier_reponses.py` étendu ; **691 items, 0 anomalie** ; 110 tests verts.
- **Docs** — ADR-005, contrat d'API (rappel libre, mode « series », attente), module-entraînement, taxonomie, README de contenu.
- **Réserves** — relecture orthophoniste à faire ; le rappel partiel reste un repère de travail, jamais un score de mémoire.

## 2026-09-21 · Sprint 3 — accès au mot et vie sociale (90 items + 8 missions)

- **Contenu** — deux nouveaux thèmes : `evocation` (« Retrouver le mot » : reconnaissance, rappel indicé à indices progressifs, rappel de la source — 5 paliers × 10) et `social` (« Vie sociale » : vignettes d'émotion, réponses adaptées, lecture d'intention — 4 paliers × 10), plus 8 missions hors écran. Total : **587 items** ; validateur 0 erreur (contrôle bloquant : aucun indice ne contient la réponse, la réponse figure toujours parmi les propositions).
- **Familles d'exercices** — récupération indicée (catégorie → attaque phonologique → forme écrite), reconnaissance, mémoire de la source, cognition sociale et pragmatique. Matériel original ; principes issus des familles classiques, aucun contenu protégé reproduit.
- **API** — ouverture du champ optionnel `indice_utilise` (essai « assisté » quand la réponse est affichée : aucune erreur commise, mais FSRS en échec et taux de réussite non gonflé) ; résumé enrichi de `assistees` et `sans_aide` ; nouveau périmètre `/api/social` (missions + carnet) avec **stockage séparé** (`backend/data/journal/`) — ADR-004.
- **Interface** — propositions cliquables, indices révélés un par un (« Un indice » puis « Voir la réponse »), écran « Missions hors écran » avec préparation, note de retour et carnet ; contrôle de cohérence interface ↔ HTML automatisé (`tools/verifier_interface.py`).
- **Tests** — 106 passed (dont 10 nouveaux : tolérance accents/casse, essai assisté, bornes d'indice, missions, carnet, isolation des stockages) ; contrôle de bout en bout sur serveur réel (7 thèmes, missions, note de carnet, séance d'accès au mot, `/ui` servi).
- **Réserves** — relecture orthophoniste des 90 items et des 8 missions à faire (`a_revoir`) ; le carnet reste local et mono-utilisateur.

## 2026-09-20 · Vérification des réponses de contenu

- **Outil** — `tools/verifier_reponses.py` : recalcule la réponse attendue de chaque item depuis son énoncé (empan endroit/envers, n-back, paires associatives, chaînes et cascades, double tâche, séries à règle avec unicité de la solution) et compare au fichier ; lecture seule, code de sortie 1 en cas d'anomalie. Résultat sur le contenu actuel : 497 items, **0 anomalie**, identifiants uniques.
- **Usage** — à relancer après toute régénération de contenu, en complément de `tools/validate_items.py` (structure et schéma).

## 2026-09-15 · Sprint 2 — mémorisation & concentration (306 items)

- **Contenu** — deux nouveaux thèmes : `memoire` (8 paliers × 18 = 144 items : empan endroit/envers 3→6 chiffres, paires associatives mot–nombre 2→4, sonde n-back N=2→4) et `concentration` (9 paliers × 18 = 162 items : calcul chaîné 3→7 opérations, cascades de soustractions, double tâche de filtrage 5→9 éléments, séries à règle). Génération déterministe (graine 20260904, `tools/generer_memo_concentration.py`) ; validateur multi-thèmes (31 fichiers, 497 items, 0 erreur) ; familles classiques d'entraînement cognitif implémentées en original — logique assimilée (PASAT, d2), aucun matériel protégé copié.
- **API** — correction par thème étendue : `memoire` = texte sans espaces/casse (empans tapés avec espaces valides), `concentration` = numérique ; types `chaine-calcul`, `serie-manquante`, `paires-associatives` au schéma ; `contenu.affichage` (sequence/liste) documenté au contrat — le temps de mémorisation ne compte pas dans `temps_ms`, note d'honnêteté sur le stimulus présent dans le payload (usage mono-utilisateur assumé).
- **Interface** — phase de mémorisation sur `/ui` : consigne → « Afficher » → stimulus temporisé (élément par élément ou liste, bouton « Passer ») → stimulus masqué → question → saisie ; clavier numérique étendu aux nouveaux types ; zéro déplacement de mise en page (espaces réservés), dark oklch inchangé.
- **Tests** — 99 passed (96 + 3 : correction mémoire tolérante, correction concentration numérique, cycle E2E mémoire avec affichage temporisé) ; validateur 0 erreur.
- **Docs** — fondements (familles classiques), protocoles (fatigue progressive conçue dans le contenu), taxonomie (table familles/fonctions), module-entraînement (Mémoire/Concentration), contrat API.
- **Réserves** — relecture orthographique `a_revoir` sur les 306 items générés ; prerequis anglais/python inchangés ; ADR-003 (front vanilla → React+Vite) toujours à formaliser.

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
