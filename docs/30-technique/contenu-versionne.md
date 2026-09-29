# Contenu versionné — règles de génération et de modification

Le contenu d'entraînement (`content/`) est de la **donnée versionnée**, pas du code : il est généré, validé, relu et suivi dans Git comme n'importe quel autre artefact. Ces règles existent parce qu'une extension de contenu a déjà réécrit, sans le dire, un thème entier (voir « Historique »).

## 1. Tirages aléatoires isolés par `thème:famille`

Chaque famille d'exercices tire ses items d'un générateur **qui lui est propre**, dérivé de la graine et de son nom :

```python
random.Random(f"{GRAINE}:{thème}:{famille}")   # jamais un flux partagé
```

Pourquoi : avec un générateur partagé, ajouter une famille ou un palier **décale le tirage de tout ce qui suit**. Le contenu déjà livré est alors réécrit silencieusement — mêmes identifiants, exercices différents — alors que le message de commit ne parle que d'un ajout.

Corollaire pratique : une extension s'ajoute **en fin de famille**. Ajouter un palier à la fin de la séquence d'une famille ne touche pas les paliers précédents.

## 2. On ne régénère pas un contenu déjà servi

Un contenu est « servi » dès qu'une donnée d'usage existe pour ses identifiants (carte de répétition espacée, historique de maîtrise, temps de référence). Régénérer ce contenu ferait pointer la même progression sur des exercices différents.

Trois issues, dans cet ordre de préférence :

1. **Ne pas régénérer** — on ajoute, on n'altère pas.
2. **Remplacer les identifiants** des items concernés (nouvelle génération = nouvel identifiant), pour que l'ancienne progression reste cohérente avec l'ancien exercice.
3. **Régénérer sans changer les identifiants** uniquement s'il n'existe **aucune** donnée d'usage — et le dire explicitement.

Depuis le 2026-09-29, le générateur « déduction » **dérive l'identifiant du contenu lui-même** (`identifiant_item` : empreinte sha256 tronquée du contenu pédagogique canonique — date, auteur et identifiant exclus). Une re-génération identique garde les mêmes identifiants ; tout contenu modifié en reçoit de nouveaux : la règle 2 y devient automatique, et une collision d'empreinte échoue bruyamment à la génération.

## 3. Toute modification de contenu se dit

Le message de commit mentionne, quand c'est le cas : quel thème, quels identifiants, combien d'items, et pourquoi. Un relecteur doit pouvoir distinguer un **ajout** d'un **remplacement** sans lire le diff ligne à ligne.

## 4. Contrôles après chaque génération

```bash
python3 tools/validate_items.py       # structure, schéma, invariantes (0 erreur attendu)
python3 tools/verifier_reponses.py    # réponses recalculées depuis l'énoncé (0 anomalie attendu)
python3 -m pytest -q                  # suite complète
```

Ces contrôles garantissent que le contenu est **valide** ; ils ne détectent pas un remplacement silencieux (c'est justement la raison des règles 1 et 2).

## Historique

- **Correction du 2026-09-29** — le générateur « déduction » utilisait des identifiants positionnels (`df-<palier>-<rang>`), réutilisés à contenu changé (reproduction : la graine produisait un `df-1-01` aux énoncés différents du livré — un remplacement silencieux, précisément le cas que ces règles interdisent). Les identifiants sont désormais dérivés du contenu (empreinte du contenu canonique ; garde-fou anti-collision). Les 47 items des paliers 2–4 dont l'aide a été harmonisée ont reçu de nouveaux identifiants (correspondance : `.cluster/correction-deduction-20260929/mapping_aides_anciens_nouveaux.md`).
- **Sprint 4 (2026-09-22)** — l'ajout des paliers d'empan de mots a consommé 72 tirages sur un générateur partagé **avant** la génération du thème « concentration » : 161 des 162 items de ce thème ont été réécrits à identifiants constants. Le contenu restait valide (0 erreur), mais le changement était invisible dans le message de commit. Détecté lors de la revue de commits du 2026-09-22.
- **Correction du 2026-09-22** — tirages isolés par `thème:famille` dans `tools/generer_memo_concentration.py` et `tools/generer_evocation_social.py` (déjà isolés par thème pour `generer_rappel_series.py`, une seule famille). Cette correction a elle-même **remplacé** le contenu des thèmes mémoire, concentration, evocation et social — décision assumée et documentée, aucune donnée d'usage n'existant à cette date. **À compter de cette date, la règle 2 s'applique sans exception.**
