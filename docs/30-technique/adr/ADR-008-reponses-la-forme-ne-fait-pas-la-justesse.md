# ADR-008 — Réponses : la forme ne fait pas la justesse

**Statut** : accepté (2026-09-26)

*Suivi (2026-09-26)* : **les montants et les quantités relèvent d'une équivalence déterministe**, jamais du moteur statistique — « 180 € », « 180€ », « 180 eur » et « cent quatre-vingts euros » valent « 180 euros » ; « 280 € » ne vaut pas « 180 euros ». Cas signalé en usage réel : une réponse dictée écrit volontiers le symbole ou le nombre en toutes lettres.

*Suivi (2026-09-26)* : **le filet sémantique ne traverse jamais un jalon de sens** — jours, mois, moments de la journée, nombres (chiffres ou lettres, sauf « un/une », le plus souvent articles). Mesuré en usage réel : « vendredi soir » était accepté pour « jeudi soir » (proximité 0,85), « jeudi matin » pour « jeudi soir » (0,81) et « 14 h 30 » pour « 15 h 30 » (**0,999**). Accepter une réponse fausse est plus grave que refuser une réponse juste : dès que les jalons diffèrent, seul l'écrit compte, et une variante acceptable se **déclare dans l'item** (`reponse.variantes`).

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

*Audit du 2026-09-26 — tous les champs à réponse libre (ceux où la dictée est proposée) :*

| Champ libre (dictée) | Tolérance de forme | Tolérance de sens | Borne |
|---|---|---|---|
| Calcul mental, concentration (valeurs) | chiffres ↔ mots, symboles d'unité (`180 €`) | — | valeur exacte |
| Mémoire — séquences chiffrées (empans, nombre associé) | espaces, **mots** (« zéro sept un »), casse | — | ordre strict |
| Mémoire — empan de mots | accents, casse, ponctuation | non (l'ordre **est** la tâche) | séquence exacte |
| Évocation (mot retrouvé) | accents, casse, variantes déclarées, faute de frappe | oui (empreintes locales) | jamais à travers un jalon |
| Quotidien — prise de message | heures et montants sous toutes leurs formes | oui (« la cave » pour « la porte de la cave ») | jour, moment, nombre **stricts** |
| Rappel libre (séries, mémoire) | accents, casse, pluriel simple | non (mots-clés) | seuil déclaré par l'item |
| Méthodes et familles à choix | casse, accents | **non : jamais sur un choix multiple** | leurres proches par construction |
| Python (code) | aucune (le code est exact) | non | **dictée retirée** : une dictée ne restitue ni indentation ni symboles |

Deux manques corrigés par cet audit : les **séquences chiffrées dictées en mots** (« cinq quatre neuf » pour « 549 ») étaient refusées, et la **dictée était proposée pour du code Python**. La batterie de tests `test_reconnaissance_vocale.py` verrouille, pour chaque champ, une forme dictée **acceptée** et une réponse fausse **refusée**.

## Conséquences

- (+) Une réponse juste n'est plus refusée à cause de sa forme : c'est la première cause de frustration constatée en usage.
- (+) L'usage d'un moteur local respecte le principe « aucune donnée ne quitte le poste », et le repli garantit que le logiciel fonctionne sans modèle installé.
- (+) La portabilité est claire : iPad/macOS ont les empreintes système ; Windows/Linux ont le repli lexical, et la note `docs/30-technique/pistes-extension-ia.md` documente le pas suivant (petit modèle ONNX, hors ligne) si la sémantique y devient nécessaire.
- (−) Le seuil prudent laisse passer des refus : « je consulte le docteur » pour « je vais chez le médecin » (proximité 0,77) reste refusé. Deux leviers existent : abaisser le seuil, ou déclarer des variantes par item — le second est préférable, il est explicite et testable.
- (−) Chaque exercice à réponse libre doit choisir **comment** il est jugé (clé normalisée, variantes, proximité de sens) : ce choix est une décision de contenu, pas un réglage technique.
