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


---

## Où tourne le logiciel ? (local vs serveur, et capacités de l'OS)

Le logiciel est **déjà local-first** : un service FastAPI sur la machine, une interface dans le navigateur, des données en fichiers JSON locaux, aucun appel réseau. C'est le bon point de départ, et cela décide de tout le reste.

| | **Local** (aujourd'hui) | **Serveur distant** |
|---|---|---|
| Modèles (voix, empreintes) | tournent sur la machine, hors ligne, coût nul | à héberger : coût, latence, montée en charge |
| Audio des exercices | **ne quitte jamais l'appareil** | doit être **téléversé** — consentement, données de santé |
| Mise à jour | manuelle | centralisée |
| Multi-appareils | un poste | partout |

Pour un POC familial, sous le contrôle d'une spécialiste, **le local s'impose** : pas d'infrastructure, et l'audio ne sort pas de l'appareil.

### Ce que les systèmes fournissent déjà (sans embarquer de modèle)

| Capacité | macOS / iOS | Windows | Android | Navigateur |
|---|---|---|---|---|
| Reconnaissance vocale | `SFSpeechRecognizer` (**mode sur l'appareil** possible) | `Windows.Media.SpeechRecognition` | `SpeechRecognizer` (`EXTRA_PREFER_OFFLINE`) | `SpeechRecognition` |
| Synthèse vocale | `AVSpeechSynthesizer`, `say` | `System.Speech.Synthesis` / SAPI | `TextToSpeech` | `speechSynthesis` |
| **Empreintes de phrases** | `NaturalLanguage` → `NLEmbedding` (**intégré, hors ligne**) | à fournir (ONNX) | à fournir (TFLite) | à fournir (`transformers.js`) |
| OCR / vision | `Vision` | `Windows.Media.Ocr` | ML Kit | limité |

**Nuance importante** : « capacité du navigateur » ne veut pas dire « sur l'appareil ». Le `SpeechRecognition` de Chrome passe souvent par les serveurs de Google — donc **pas** local du point de vue de la vie privée. Le même nom d'API a un comportement différent selon le navigateur : Safari (Siri) est sur l'appareil, Chrome non. Pour un usage sensible, il faut soit l'API native avec le drapeau « sur l'appareil », soit **embarquer** un petit moteur (whisper.cpp, modèle quantifié) qui tourne partout en local.

### Architecture conseillée : une couche de capacités, avec repli

Une seule abstraction, et pour chaque capacité une priorité claire :

1. **API native sur l'appareil** si elle existe et si le drapeau « sur l'appareil » est disponible ;
2. sinon **petit moteur embarqué** (whisper.cpp pour la voix, MiniLM int8 via ONNX Runtime pour les empreintes — même code sur macOS, Windows et Linux) ;
3. sinon **repli sur la saisie clavier**.

Avantages : le cœur du logiciel reste identique partout ; on n'embarque un modèle **que** là où le système ne le fournit pas ; et la promesse de confidentialité tient sur toutes les plateformes.

### Pour ce POC

- **Rester local** (aucun changement aujourd'hui) ; le serveur ne se justifiera que pour du multi-utilisateur ou du suivi à distance.
- **Voix** : commencer par l'API native avec drapeau « sur l'appareil » (Apple/Android), sinon whisper.cpp embarqué ; **éviter** le `SpeechRecognition` de Chrome pour un usage sensible.
- **Empreintes (étape 2)** : sur macOS/iOS, `NLEmbedding` est **gratuit et hors ligne** — le vrai saut sémantique y coûte zéro ; ailleurs, MiniLM int8 (~25 Mo) avec ONNX Runtime.
- **Tablette pour la personne** : le modèle « serveur local sur un ordinateur + navigateur » convient au foyer ; si le besoin devient un usage nomade, une enveloppe native (iOS/Android) permettrait d'utiliser directement les capacités de l'appareil.
