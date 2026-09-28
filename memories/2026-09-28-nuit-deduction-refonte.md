# 2026-09-28 (nuit) — Déduction : défauts A/B/C corrigés, contenu régénéré, générateur borné

## La reprise (17h00)

Mission cron : reprise de la refonte Déduction après la nuit du 27 (blocage des générations paliers 2-3, trois défauts signalés par l'addendum). Organisation : 3 voies (diagnostic/sources, conception/correction, revue indépendante) + coordinateur intégrateur.

## Diagnostic (décisif pour la suite)

- **Blocage palier 3 expliqué** : ancres {coin, diagonale, diagonale-inverse} + chaînes à UNE relation (2 informations) → vivier trop pauvre (4-5 jetons cités sur 9), sélection plafonne à 21 cases ouvertes sur 9 à déterminer. 0 % de succès sur 200 placements ; seuil d'abandon 40 000 essais ≈ 3 h de silence.
- **Correctif validé** : chaînes à 2 relations (3 informations) → 100 % de succès, ≤ 0,23 s par sélection.
- Palier 2 converge désormais (0,4 s) ; vocabulaire requis du palier 2 était ignoré en silence (types non productibles par sa grammaire).

## Corrections committées (branche amelioration-deduction-20260927, aucune fusion main)

- `69755a7` **A** : `pas-voisin-dessus/dessous` nient leur propre positive (inversées avant) + tests de complémentarité sur toutes les paires n=3/n=4, appariement indépendant des libellés.
- `3eedc97` **B** : rendu des 8 relations négatives dans l'interface + 8 phrases dorées vérifiées sur le VRAI code (`verifier_phrases.js`).
- `c486c98` modification locale conservée (4 négations relatives au palier 3 — décision assumée).
- `f2b4c90` **C** : critères mesurés (aucune phrase seule ne fixe une position ; première certitude ≥ 2 phrases) dans le générateur ET le validateur ; palier 3 en chaînes à 3 informations ; palier 4 plafond 8→18 (sinon déductibilité 4×4 inatteignable — cause de l'échec silencieux) ; VOCABULAIRE_REQUIS aligné sur le productible + garde-fou.
- `e8a7a2b` contenu régénéré : 80 grilles `df-*`, graine 20260928, remplacement annoncé (règle contenu-versionné).
- `5e39cfb` générateur borné : abandon à 2 000 placements (~90 s) au lieu de 3 h ; vocabulaire requis non produisible = erreur.

## Mesures avant/après (outil tools/mesurer_difficulte.py)

- P3 : phrase qui fixe seule le centre **20/20 → 0/20** (« ni-ni » sur 3×3 = placement direct déguisé).
- P2 : première certitude **k = 2-6 → 6-11** ; grilles redondantes 10/20 → 0/20.
- P4 : débloqué (k = 2-9, 15-16 phrases, conforme à l'ancien stock).
- P1 : non bloqué (initiation séquentielle — décision documentée), mesuré.
- Tours de solveur : jamais utilisés comme mesure de difficulté.

## Revue indépendante (2 volets, lecture seule)

- **3a logique** : 2 496 tests de complémentarité OK ; 0 phrase-solo paliers 2-4 ; 80/80 déductibles ; 0 type « case ». Verdict : **LIVRAISON POSSIBLE**.
- **3b langue/rendu** : rendu indépendant des 8 négations naturel et complet ; 1 551 informations vérifiées contre les solutions, **0 incohérence** ; 692 phrases sans défaut de forme. Un mineur cosmétique (« qui » ambigu après « de l'autre côté du centre », df-3-03/df-3-18). Verdict : **LIVRAISON POSSIBLE**.

## Tests finaux

pytest **210 passed** (baseline 206 + 4 nouveaux) ; validate_items 0 erreur ; verifier_reponses 0 anomalie ; verifier_interface OK ; verifier_phrases 8 dorées + 692 phrases OK ; node --check OK.

## Sources (01_diagnostic.md)

6 vérifiées (Ortho Édition inspiration, INCOG 2.0 PMID 36594859, Levine GMT 2011, Ciaramelli PQRST 2015, Meichenbaum & Goodman 1971, Fasotti/TPM via Winkens 2009) ; Gollwitzer & Sheeran signalée non ouverte ; original Wilson-PQRST introuvable sur PubMed — tracé honnêtement.

## Pièges à retenir

1. **Les sous-agents 20 min** : missions trop larges = interruption sans rapport final. Le périmètre resserré + « rapport écrit au fil de l'eau » a fonctionné ; la reprise intégrateur (patch soi-même le chemin critique) a débloqué la nuit.
2. **stdout bufférisé** perdu au SIGTERM : toujours `-u` (python3 -u) pour les longues commandes.
3. **rmdir/find supprimés par le Safety Guard** en session cron : passer par mv + laisser les répertoires vides, ou demander l'approbation.
4. Les sous-agents écrivent leurs rapports dans un chemin imbriqué (remediation-cognitive/remediation-cognitive/...) quand le cwd du spawn est le dépôt : déplacer au lieu de supprimer.
5. **Un plafond de phrases trop bas rend la déductibilité inatteignable en silence** (palier 4) : signaler la cause quand le glouton s'épuise.
6. L'anti-« grammaire pure » : le mixage (négations dans le relatif) + chaînes à 3 informations ont débloqué la génération — cohérent avec l'échec « négatif pur / relatif pur » du 27.

## Reste à faire (hors périmètre nuit)

Exercer les négations binaires dans le contenu ; équilibrer les types rares ; lever l'ambiguïté cosmétique « qui » ; relecture orthophoniste (statut a_revoir conservé) ; pousser les corrections de bibliographie (sources primaires) dans docs/10-clinique/.
