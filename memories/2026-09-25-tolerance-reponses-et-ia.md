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
