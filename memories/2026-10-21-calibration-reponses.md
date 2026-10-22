# 21 octobre 2026 — mesurer la correction libre, issue #6

Travail isolé sur `fix/calibration-reponses`, sans modifier le checkout du serveur,
les contenus versionnés, les historiques ou le moteur. Corpus de 38 cas issus des
12 prises de message et deux inversions synthétiques, outil de mesure sans réseau,
quatre sorties avant/après lexical et Apple NLEmbedding réel.

Correctif restreint : les négations ne passent plus via la réponse contenue dans
une phrase ; les permutations des mêmes mots ne sont pas acceptées par proximité.
Seuil 0,78 inchangé. ADR-051, procédure et limites documentées.

Mesures avant → après : lexical 4 → 0 fausses acceptations, 1 → 1 faux refus ;
Apple 7 → 3 fausses acceptations, 0 → 0 faux refus. Apple accepte encore trois
substitutions de personne/lieu. Ne pas fermer #6 : il faut des critères/variantes
par item et une relecture indépendante, puis élargir les contre-exemples. La
proximité Apple de « chez la voisine » (.8831) est trop proche de « la cave » (.8952)
pour justifier un seuil par ajustement opportuniste.

Validation : 448 pytest réussis, 1 ignoré ; 14 tests ciblés réussis avec le Python
Apple ; Ruff backend/engine/tools vert ; compilation et diff-check réussis.
Aucune nouvelle dépendance, aucun push/PR/merge dans ce lot.

## Finalisation du 22 octobre après interruption du sous-agent

Reprise par le parent des changements non commités. Politique déterministe des
prises-message finalisée (égalité, variantes explicites et enveloppes neutres),
sans modification des contenus. Une cible négative explicite reste possible ;
sa polarité doit correspondre. 70 cas : avant lexical 8 FA/6 FR, Apple réel
15 FA/2 FR ; après 0/0 pour les deux. Les rapports avant/après sont conservés.
Aucun seuil choisi, aucun contrôle indépendant revendiqué. Les critères et
variantes se substituent au score pour ces faits précis ; les autres contrats
restent inchangés.

450 pytest réussis/1 ignoré avant le dernier test de cible négative ; puis
17 tests ciblés réussis, Ruff vert et deux mesures --strict réussies (lexical et
Python Apple réel). L’issue #6 garde le suivi de corpus indépendant/relecture ;
les faux positifs reproduits sont corrigés mais la généralisation n’est pas
prouvée.
