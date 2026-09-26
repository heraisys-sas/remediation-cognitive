# 2026-09-25 — Tolérance des réponses + pistes d'extension IA

## Le bug signalé

« Dans les méthodes, 15h n'est pas accepté pour 15 h. »

**Cause** : ma normalisation des heures (`(\d)\s*[:h]\s*(\d)`) exigeait un chiffre **après** le « h » — donc elle traitait « 14 h 30 » mais pas « 15 h ». Une heure seule passait à travers.

**Correctif** : la normalisation devient `(\d)\s*[:h]\s*(\d*)` → « 15 h » = « 15h » = « 15:00 » = « 15h00 » (heure pleine ramenée à « 15h »). Et elle s'applique désormais à **toutes** les familles à texte (méthodes, quotidien, accès au mot), plus seulement à la prise de message.

## Capacités ajoutées (petit moteur, aucun modèle)

- **`reponse.variantes`** : un item peut déclarer ses synonymes (« bicyclette » pour « vélo », « frigo » pour « réfrigérateur »). Contrôlé par le validateur (liste de chaînes non vides, distinctes de la réponse).
- **Tolérance de frappe** (accès lexical) : distance d'édition ≤ 1 (≤ 2 si le mot est long). L'exercice porte sur la mémoire, pas sur l'orthographe.

## La question posée

« Comment étendre les capacités du logiciel ? Avec un tout petit moteur d'IA ? »

Réponse écrite dans `docs/30-technique/pistes-extension-ia.md`, en cinq étapes : (0) le moteur de tolérance déjà en place, (1) similarité lexicale sans modèle, (2) **empreintes sémantiques locales** (~80 Mo, CPU, hors ligne) — le vrai saut : juger le sens et non la forme, (3) reconnaissance vocale locale (répondre à voix haute), (4) génération de contenu hors ligne, (5) tuteur adaptatif (après un pilote réel).

Principe tenu : local d'abord, déterministe quand possible, et l'IA **jamais en travers de la validation** — elle propose, les outils vérifient, le contenu reste versionné.

## Contrôles

**811 items / 0 erreur**, **134 tests**.

## Suite (même jour) — les réponses dictées en chiffres

Bug : une réponse orale « six » dans un exercice de concentration était refusée (6 attendu).

Cause : `_corriger_numerique` n'acceptait que les chiffres ; la conversion lettres → chiffres existait mais n'était branchée que sur les réponses **en texte**.

Correctif : un convertisseur français complet (unités, dizaines, irréguliers « soixante-dix » / « quatre-vingt-dix », « cent », « mille », traits d'union, « et », ponctuation finale de la dictée) branché sur **toutes** les comparaisons numériques — calcul mental, concentration, estimation.

À retenir : la **similarité sémantique ne sert pas aux nombres** (« deux » et « 2 » ne sont proches qu'à 0,33 pour le modèle). Deux outils distincts, chacun sur son terrain : le sens pour le texte, une conversion exacte pour les nombres.

## 2026-09-26 — horaires en toutes lettres + filet sémantique encadré

Signalement : « 15 heures » refusé pour « 15 h » (thème méthodes).

- Cause : le motif d'heure coupait « heures » en deux (« 15heures »). Corrigé par
  `_normaliser_horaires` : heures, minutes, « et quart », « et demie », « moins le quart »,
  « midi »/« minuit », périodes (« du soir » → +12 h si < 12 h).
- Règle retenue : **écrire l'heure n'est pas l'exercice**. Toutes les formes françaises
  équivalentes sont acceptées, et verrouillées par des tests.
- Le moteur sémantique du poste (`capacites.proche`, empreintes Apple, seuil 0,78) est
  désormais branché sur les réponses **libres** de « méthodes », mais **pas sur les choix
  multiples** : là, les leurres sont proches par construction et la tolérance de sens
  accepterait une mauvaise proposition.
- Mesures du jour sur ce poste : « le toubib » ≈ « le médecin » 0,858 (accepté),
  « je consulte le docteur » ≈ « je vais chez le médecin » 0,771 (juste sous le seuil),
  « la migraine » ≈ « le mal de tête » 0,536 (refusé) — le seuil de 0,78 est prudent.
