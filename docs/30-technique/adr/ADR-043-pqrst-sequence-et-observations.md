# ADR-043 — PQRST séquencé et observations séparées

9 octobre 2026 — implémentation d’[EX-REV-001](../../20-specs/corrections-exercices-existants.md#2-ex-rev-001--pqrst-réellement-séquencé). Corpus, identifiants et historiques conservés.

## Contexte

Les cinq étapes PQRST étaient affichées ensemble ; texte, notes et réponses restaient accessibles au test. Le retour global ne distinguait ni absence déclarée, ni relecture, ni réponse après modèle. L’utilisateur autorise le développement des corrections documentées dans la spécification v1.1.

## Décision

L’interface affiche un écran à la fois : départ volontaire → P et retour bref → Q non notée et question possible → R sans minuterie → S sans support → comparaison avec résumé modèle → T1 puis T2 sans support → correction serveur. Chaque réponse est verrouillée avant l’étape suivante. Les deux corrections T apparaissent seulement après les deux réponses. Le modèle après S est conservé ; T est donc explicitement qualifié de rappel après ce modèle.

Les anciens supports quittent le DOM et le texte utilisé par Écouter ; la lecture est arrêtée à chaque transition. Texte, question personnelle, question modèle et aides sont retirés avant S/T. Le contrôle audio existant est réutilisé ; aucune lecture automatique supplémentaire. Les champs PQRST sont saisis au clavier, les choix par boutons/clavier ; aucune mesure de latence ni nouvelle dictée automatique.

P, Q, S et chaque T permettent une absence explicitement déclarée. Le champ vide seul n’avance jamais. S et chaque T autorisent une relecture supplémentaire : première réponse ou absence verrouillée, texte réaffiché puis retiré, tentative aidée distincte. Une relecture lors de T1 qualifie aussi la condition de T2. Maximum : deux tentatives par rappel, trois relectures par séquence. Une reprise d’un item déjà corrigé dans la séance est identifiée.

Le retour S est une **comparaison locale avec un modèle**, sans note intermédiaire. Le correcteur serveur conserve ses critères bornés et son seuil éditorial ; une idée non reconnue est présentée comme à vérifier, sans prétendre comprendre toute paraphrase. Les tentatives aidées reçoivent un retour séparé, mais ne remplacent pas les premières réponses utilisées par le comportement de notation historique. [ADR-027](ADR-027-accompagnement-pqrst-local.md) reste applicable : accompagnement Apple facultatif après correction finale uniquement, deux relances, sans modification du résultat.

## Contrat additif

Le corps existant `reponse` conserve `"1"`, `"2"`, `"4"` et `"5"` pour les premières réponses ; `null` signifie une absence déclarée lorsqu’une trace de cette version est fournie. Sans `_pqrst`, le correcteur conserve le comportement historique et n’ajoute pas d’observation de protocole masqué.

```json
{
  "_pqrst": {
    "version": "pqrst-sequence-v1",
    "phase": "fin",
    "etapes_realisees": ["P", "Q", "R", "S", "retour-S", "T1", "T2"],
    "modele_avant_test": true,
    "reprise_apres_correction": false,
    "statuts": {"1": "reponse", "2": "absence_declaree", "4": "reponse", "5.0": "reponse", "5.1": "reponse"},
    "tentatives": {
      "4": [{"reponse": "La première formulation", "condition": "sans_relecture", "modalite": "clavier"}],
      "5.0": [{"reponse": "Un choix proposé", "condition": "sans_relecture", "modalite": "choix"}],
      "5.1": [{"reponse": "Un choix proposé", "condition": "sans_relecture", "modalite": "choix"}]
    },
    "relectures": [],
    "interruptions": {}
  }
}
```

Les réponses de cet exemple sont illustratives : le serveur vérifie l’appartenance des choix aux options du véritable item et l’égalité entre chaque première tentative et la réponse principale. La forme complète exige toutes les étapes dans l’ordre et `phase: fin`. Les chaînes sont bornées à 2 000 caractères, les champs inconnus refusés, les tentatives/relectures bornées ; les compteurs d’interruption sont des entiers de 1 à 10 000 par phase connue. Conditions : `sans_relecture`, `apres_relecture`, `reprise_interrompue` ; elles doivent correspondre aux relectures/interruption déclarées. Cette trace décrit ce que le client rapporte, pas une mesure indépendante du comportement.

`normaliser_observation_pqrst(item, reponse, partielle=True)` dans le correcteur valide et normalise sans noter. `corriger_sequence` l’appelle avec `partielle=False`, puis ajoute `sequence.observation` au résultat : protocole, étapes, absences, aides, interruptions et correction de chaque tentative. Les résultats initiaux et aidés restent distincts. Aucun nouveau contenu ni score de capacité générale.

Les libellés d’interface sont centralisés dans `messages.PQRST_INTERFACE`, injectés dans une copie du contenu public sous `interface_pqrst` ; les banques versionnées restent inchangées.

## Pause, sortie et persistance

Pause volontaire et perte de visibilité retirent les supports et arrêtent la voix. Les réponses validées sont conservées en mémoire ; un rappel repris porte la condition `reprise_interrompue`. Une interruption pendant relecture est attribuée au rappel concerné. Aucun temps de pause n’est soustrait pour fabriquer une mesure continue. La fiche méthode finale est consultable dans un panneau replié.

`snapshotPqrst()` fournit une copie des réponses déjà validées et de la phase courante, sans le brouillon en cours. Le contrat additif `POST /{theme}/sessions/{session_id}/observations`, corps `{item_id, reponse}`, permet au gestionnaire de conserver ce checkpoint après validation partielle, sans correction, réponse moteur ou modification FSRS. Une observation finale corrigée ne doit pas être écrasée par un checkpoint tardif. L’intégration de sortie appelle le checkpoint avant de nettoyer l’écran. `nettoyerSequence()` retire le suivi de visibilité et les supports résiduels.

La mémoire des sous-étapes n’est pas une sauvegarde permanente à chaque frappe : une fermeture brutale avant checkpoint peut perdre la séquence inachevée. Les données déjà envoyées demeurent dans le journal local ; aucun historique ancien n’est reconstruit. Aucun audio ni conversation d’accompagnement conservé.

## Vérification

Tests comportementaux : trajet complet avec masquage DOM/audio, première réponse conservée après aide, absence déclarée, pause pendant relecture, aide T1 portée à T2, checkpoint partiel sans correction, rejet des traces incohérentes/hors bornes et compatibilité des réponses historiques. Les tests existants de correction PQRST et d’accompagnement Apple restent applicables. La recette visuelle vérifie écran étroit, focus, arrêt audio et séparation des réponses avant/après feedback.
