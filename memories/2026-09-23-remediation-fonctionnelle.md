# 2026-09-23 — Remédiation fonctionnelle (retournement de cadrage)

## Le signal

Une orthophoniste a pointé un « gros problème conceptuel » : les exercices développés (empan, n-back, chaînes de calcul, séries, double tâche) sont des **entraînements aux tests d'évaluation**, pas de la remédiation. Elle demande des entraînements qui **remédient aux lacunes** (mémoire de travail altérée, planification altérée), pas des exercices qui mesurent.

## La réponse

Le reproche est juste. Un test mesure une fonction ; s'y entraîner améliore surtout le test (effet test-retest), le transfert vers la vie quotidienne est faible. La remédiation, elle, travaille la fonction **dans des situations de vie, avec des stratégies**, pour qu'elle se répare et se transfère.

Trois gestes :

1. **Documenter le retournement** — `docs/10-clinique/remediation.md` : pourquoi « s'entraîner au test » ne remédie pas ; ce qu'est un exercice de remédiation (écologique, stratégique, métacognitif, gradué) ; taxonomie par fonction altérée ; et le devenir des épreuves (déplacées vers une section « évaluation » quand le module bilan existera).
2. **Livrer un premier lot fonctionnel** — thème « Au quotidien » (36 items) : prise de message (mémoire de travail), étape suivante (planification), estimation de durée (anticipation). Chaque consigne enseigne une stratégie.
3. **Règle dans AGENTS.md** — « Remédiation, pas évaluation : aucun nouvel exercice d'allure évaluative. » Les épreuves existantes ne sont pas supprimées : elles restent des repères de progression, en attendant leur déplacement.

## Choix de conception

- L'estimation de durée est corrigée par **fourchette**, pas à la valeur près : une estimation n'est pas une mesure.
- Le validateur vérifie qu'une question de prise de message est **retrouvable dans le message affiché** — et a attrapé une réponse dérivée (« celui de 16 h 42 ») non présente telle quelle dans le stimulus.
- Les familles suivantes (par où commencer, remettre les étapes dans l'ordre, repérer une info dans un courrier, mémoire prospective) sont listées, pas encore construites : on garde la ligne « à quoi ça sert demain ? ».

## Leçon

Le cadrage précédent confondait **mesurer** et **remédier**. Les « familles classiques » (PASAT, d2, empan, n-back) sont majoritairement des paradigmes d'évaluation : les avoir prises pour des entraînements était l'erreur exacte que la clinique distingue depuis longtemps. La remédiation exige du matériel écologique et des stratégies explicites — pas plus de difficulté, mais plus de sens.

## Reste à faire

- Relecture orthophoniste du nouveau contenu (et du document de cadrage).
- Construire les familles fonctionnelles restantes.
- Déplacer les épreuves vers « évaluation » quand le module bilan existera.

## 2026-09-26 — le garde-fou de durée jetait la réponse en cours

Signalement : au 4ᵉ test d'une séance de déduction, « la séance n'est plus disponible » (409).

- Cause : au-delà de 600 s, le serveur refusait la réponse **en cours** (409) au lieu de clore
  la séance. Les grilles de déduction sont longues : la limite tombait au milieu d'un exercice.
- Règle corrigée : **on ne jette jamais le travail fait**. La réponse est enregistrée, puis la
  séance se clôt ; le client est prévenu (`seance_terminee: true`) et propose le résumé. Une
  réponse *suivante* reçoit 409.
- Corollaire : `POST …/fin` devient **idempotent** (renvoie le même résumé) — sinon l'interface
  ne pouvait pas afficher le résumé après une clôture automatique (409). Contrat d'API mis à jour.
- Principe à garder : un garde-fou de dosage doit arrêter la **proposition** d'exercices, jamais
  invalider un exercice déjà commencé.
