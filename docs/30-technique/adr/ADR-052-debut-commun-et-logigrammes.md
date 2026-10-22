# ADR-052 — Début commun et logigrammes

## Contexte
Deux activités adultes complètent les parcours. Elles ne constituent ni épreuves diagnostiques ni thérapies validées de façon spécifique. Les historiques de Calcul mental et Déduction doivent être préservés.

## Décision
Créer les thèmes isolés `debut-commun` (« Débuts de mots communs ») et `logigrammes` (« Croiser les indices »), servis par le catalogue et les séances habituelles. Le segment lexical exige une égalité écrite NFC/casse/espaces externes uniquement, avec variantes explicites : aucun filet sémantique ni validation automatique issue d’Évocation. La dictée manuelle reste une saisie à vérifier.

Le logigramme utilise des catégories et contraintes explicites ; le tableau offre des associations natives réversibles avec retour « À déterminer ». Il ne remplit aucun autre lien. Les indices restent visibles et accessibles en lecture. Les aides sont des méthodes ; une première erreur ouvre un second essai avant révélation. La grille externe sert de support d’organisation, sans promesse d’entraînement général de la mémoire de travail.

Le contrat API est étendu par le type `logigramme` et ses catégories/contraintes publiques. Les mots complets lexicaux et la preuve de résolution restent privés côté banque ; les réponses ne sont exposées qu’au feedback existant. Aucun moteur ni stockage nouveau, aucun service IA.

## Conséquences
Progression, aides, dosage et feedback existants sont réutilisés. Le tableau v1 ne représente pas les exclusions intermédiaires ; les sélections sont entièrement réversibles. La preuve déductive et l’unicité sont vérifiées hors interface. Relecture orthophoniste informelle toujours à réaliser avant extension d’usage.
