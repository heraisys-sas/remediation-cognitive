# ADR-008 — Réponses : la forme ne fait pas la justesse

**Statut** : accepté (2026-09-26)

## Contexte

Trois refus en apparence anodins, tous signalés en usage réel :

- « 15 heures » refusé pour « 15 h » ;
- « six » refusé pour 6 ;
- « bicyclette » refusé pour « vélo ».

Dans les trois cas, la réponse était **juste**. L'exercice porte sur le raisonnement, la mémoire ou l'accès lexical — jamais sur l'orthographe, l'écriture des nombres ou celle de l'heure.

Le risque inverse est réel : une tolérance trop large accepterait une réponse fausse. Sur un choix multiple, les autres propositions sont des **leurres proches par construction** (« devant la gare » / « derrière la gare ») : une tolérance de sens y accepterait la mauvaise réponse.

## Décision

**1. On juge le contenu, pas l'écriture.** Sont équivalents : la casse, les accents, la ponctuation, les espaces, les nombres en lettres, les heures sous toutes leurs formes françaises (« 15 h », « 15 heures », « quinze heures », « 15:00 », « 15 heures 30 », « trois heures et demie », « quinze heures moins le quart », « midi et demi », « 8 heures du soir » = 20 h), les variantes déclarées par l'item (`reponse.variantes`) et une petite faute de frappe (distance d'édition 1, 2 pour un mot long).

**2. Le moteur sémantique du poste est utilisé quand il existe.** L'application interroge le système au démarrage : sur macOS et iPad, les **empreintes de phrases d'Apple** (Natural Language) — calculées **sur l'appareil**, rien ne quitte le poste ; ailleurs, un repli **lexical sans dépendance** (n-grammes de caractères + recouvrement de mots). Le seuil est volontairement prudent (0,78) : il rattrape des synonymes proches (« le toubib » ≈ « le médecin »), pas des reformulations libres.

**3. Le filet sémantique ne s'applique jamais à un choix multiple.** Là, seule l'égalité (normalisée) compte : les leurres sont proches par construction. Il ne s'applique qu'aux réponses **libres** (une phrase, pas une valeur courte : ni un nombre, ni une heure, ni un code).

**4. Aucune validation par un modèle à l'exécution.** Pas de LLM pour corriger : lent, non déterministe, non testable. S'il devait y en avoir un, ce serait derrière un seuil, avec repli sur la règle explicite — et jamais en travers de la validation.

**5. Un ajout de tolérance se prouve par un test.** Chaque équivalence acceptée et chaque refus attendu sont verrouillés par des tests (heures, nombres, variantes, garde-fou des choix multiples).

## Conséquences

- (+) Une réponse juste n'est plus refusée à cause de sa forme : c'est la première cause de frustration constatée en usage.
- (+) L'usage d'un moteur local respecte le principe « aucune donnée ne quitte le poste », et le repli garantit que le logiciel fonctionne sans modèle installé.
- (+) La portabilité est claire : iPad/macOS ont les empreintes système ; Windows/Linux ont le repli lexical, et la note `docs/30-technique/pistes-extension-ia.md` documente le pas suivant (petit modèle ONNX, hors ligne) si la sémantique y devient nécessaire.
- (−) Le seuil prudent laisse passer des refus : « je consulte le docteur » pour « je vais chez le médecin » (proximité 0,77) reste refusé. Deux leviers existent : abaisser le seuil, ou déclarer des variantes par item — le second est préférable, il est explicite et testable.
- (−) Chaque exercice à réponse libre doit choisir **comment** il est jugé (clé normalisée, variantes, proximité de sens) : ce choix est une décision de contenu, pas un réglage technique.
