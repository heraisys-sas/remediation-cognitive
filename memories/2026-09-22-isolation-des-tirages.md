# 2026-09-22 — Isolation des tirages de contenu (correctif post-revue)

## Origine

Revue des commits demandée par l'utilisateur : en relisant `47ebca4` (sprint 4), j'ai comparé le contenu livré à celui du sprint 2 et constaté que **161 des 162 items du thème `concentration` avaient été réécrits** — mêmes identifiants, mêmes structures, valeurs différentes. `calcul-mental` (171) et `memoire` paliers 1 à 8 (144) étaient intacts, ce qui rendait la réécriture invisible.

## Cause

`tools/generer_memo_concentration.py` tirait tout d'**un seul `random.Random(GRAINE)`** : d'abord `memoire`, puis `concentration`. Les 72 items d'empan de mots ajoutés au sprint 4 ont consommé 72 tirages **avant** la génération de `concentration` : le flux ne démarrait plus au même endroit. Les paliers de mémoire 1 à 8, générés avant, sont restés identiques — d'où la discrétion du changement.

## Correctif appliqué (demandé : isolation + règle, sans empreinte de contenu)

1. **Tirages isolés par `thème:famille`** — `random.Random(f"{GRAINE}:{thème}:{famille}")` dans `generer_memo_concentration.py` (chaque famille : empan, mots, paires, n-back, chaîne, cascade, double tâche, série) et dans `generer_evocation_social.py` (mélange des propositions par famille). `generer_rappel_series.py` était déjà isolé (une seule famille) — commentaire ajouté pour l'expliquer.
2. **Règle écrite** — `docs/30-technique/contenu-versionne.md` : isolation des tirages, extension en fin de famille, aucune régénération d'un contenu déjà servi (remplacer les identifiants si un changement s'impose), modification annoncée dans le message de commit, contrôles obligatoires après génération. AGENTS.md renvoie vers cette page.
3. **Empreinte de contenu volontairement NON ajoutée** (demande explicite) : le sujet reste ouvert, la règle écrite en tient lieu pour l'instant.

## Vérifications

- **Isolation prouvée** : générer `memoire` puis `concentration` (ou l'inverse) donne un résultat identique ; une famille ne dépend pas des autres familles.
- **Déterminisme** : deux exécutions successives des quatre générateurs → empreinte identique.
- **Contrôles** : validateur 53 fichiers / 691 items / 0 erreur ; réponses recalculées 0 anomalie ; 114 tests verts.

## Effet sur le contenu (assumé et documenté)

L'isolation change les séquences de tirage : mémoire 216/216 items remplacés, concentration 162/162, evocation 24/50 et social 32/40 (ordre des propositions seulement) ; calcul mental et rappel de séries intacts. **Décision assumée** : aucune donnée d'usage n'existe à cette date (pas d'utilisateur réel, seulement des données d'essai), et attendre aurait figé des générateurs instables — avec le risque de refaire exactement la même réécriture silencieuse au prochain ajout. À compter de cette date, la règle « on ne régénère pas un contenu servi » s'applique sans exception.

## Leçon

Un générateur aléatoire partagé rend le contenu **dépendant de l'ordre d'ajout** : ajouter du contenu ailleurs réécrit ce qui existe. L'isolation par périmètre nommé règle le problème une fois pour toutes, et le message de commit doit dire quand du contenu est remplacé — pas seulement quand il est ajouté.
