# Pistes d'extension — « petits moteurs d'IA » (POC)

**Principe directeur** : local d'abord (aucune connexion), déterministe quand c'est possible, et **jamais l'IA en travers de la validation** — la machine propose, les outils vérifient, le contenu reste des données versionnées.

| Étape | Moyen | Ce que ça débloque | Coût |
|---|---|---|---|
| **0. Moteur de tolérance** *(déjà là)* | normalisation + variantes + distance d'édition | toutes les écritures d'une même réponse (« 15h » = « 15 h », « deux » = « 2 », « bicyclette » = « vélo », une faute de frappe) | aucun modèle |
| **1. Similarité lexicale** | TF-IDF / n-grammes de caractères + synonymes par item | réponses libres courtes : accepter « le toubib » pour « le médecin », « mal de tête » pour « mal à la tête » | ~0 Mo, instantané |
| **2. Empreintes sémantiques locales** | modèle d'embeddings minuscule (type all-MiniLM-L6-v2, ONNX, CPU) | comparer le **sens** : réponses rédigées (« raconte l'essentiel »), attributs SFA libres, feedback « presque » avec un score de proximité | ~80–150 Mo, CPU, < 100 ms, hors ligne |
| **3. Reconnaissance vocale locale** | Whisper tiny/base en local | répondre **à voix haute** (bien plus écologique qu'un clavier pour la mémoire et l'accès lexical, et moins fatigant pour un public post-commotionnel) | ~40–150 Mo, CPU |
| **4. Génération de contenu assistée** | petit LLM **hors ligne** (au moment de la conception, jamais à l'exécution) | produire des items par lot (définitions, textes, situations) — le volume de contenu cesse d'être un goulot ; tout passe par les validateurs et reste versionné | variable, hors runtime |
| **5. Tuteur adaptatif** | règles + statistiques d'erreurs (éventuellement un petit classifieur) | choisir l'indice suivant selon **le type d'erreur** (phonologique vs sémantique), doser la séance | nécessite un historique d'usage réel |

## Le pas qui change la nature du logiciel

C'est l'**étape 2**. Aujourd'hui, une réponse libre ne peut être jugée que par sa forme : on accepte des écritures équivalentes, pas des formulations différentes. Avec un petit modèle d'empreintes (80 Mo, CPU, hors ligne), on peut comparer ce que la personne **veut dire** — ce qui débloque les exercices de rappel libre, la reformulation d'un texte, et un retour nuancé (« presque — il manquait l'idée de… ») au lieu d'un binaire juste/faux.

## Ce que je ne recommande pas

- **Un LLM à l'exécution pour corriger** : lent, non déterministe, non testable. S'il est utilisé, ce doit être derrière un seuil et toujours avec un repli sur la règle explicite.
- **Un modèle qui « note » la personne** : on garde des règles lisibles et vérifiables. L'IA aide à *comprendre* la réponse, jamais à *évaluer* la personne.

## Ordre conseillé

1 (lexical, tout de suite) → 2 (empreintes, le vrai saut) → 3 (voix) → 4 (contenu) → 5 (adaptatif, après un pilote réel).
