# Rapport 03b — Revue langue & rendu (déduction)

- Dépôt : remediation-cognitive · branche amelioration-deduction-20260927 · HEAD 5e39cfb
- Relecteur : sous-agent indépendant du générateur (lecture humaine du français rendu)
- Périmètre : 80 grilles df-* (60 grilles 3×3, 20 grilles 4×4), paliers 01–04
- Rendu examiné : `frontend/src/app.js` — `predicatAtome`, `relationAtome`, `phraseAtome`, `sansEst`, `formaterEnonce`

## 1. Défaut B — rendu JS

### 1.1 Vérification officielle

`node tools/verifier_phrases.js` :

```
✓ 8 phrases dorées (types négatifs) rendues à l'identique
✓ 692 phrases et 1298 informations rendues sans anomalie
```

Conforme au résultat attendu (8 dorées + 692 phrases / 1298 informations, 0 anomalie).

### 1.2 Contrôle indépendant (mon propre pilote)

Méthode : fonctions de rendu extraites telles quelles de la tête de `frontend/src/app.js`
(constants + `nomsPour` → `formaterEnonce`, sans retouche), puis rendu de **toutes** les
phrases des 80 grilles df-* avec contrôles de forme, plus un rendu ciblé des 10 types demandés.

**Rendu ciblé — 8 types négatifs + 2 positifs** (sujet triangle vert / cible losange jaune, n=4) :

```
pas-voisin-gauche   → Le triangle vert n'est pas juste à gauche du losange jaune.
pas-voisin-droite   → Le triangle vert n'est pas juste à droite du losange jaune.
pas-voisin-dessus   → Le triangle vert n'est pas juste au-dessus du losange jaune.
pas-voisin-dessous  → Le triangle vert n'est pas juste en dessous du losange jaune.
pas-a-droite-de     → Le triangle vert n'est pas plus à droite que le losange jaune.
pas-a-gauche-de     → Le triangle vert n'est pas plus à gauche que le losange jaune.
pas-au-dessus-de    → Le triangle vert n'est pas plus haut que le losange jaune.
pas-en-dessous-de   → Le triangle vert n'est pas plus bas que le losange jaune.
voisin-dessus       → Le triangle vert est juste au-dessus du losange jaune.
a-droite-de         → Le triangle vert est plus à droite que le losange jaune.
```

La négation se lit naturellement (« n'est pas juste au-dessus du … »), les 10 phrases sont
complètes, avec verbe et point final. ✔

**Contrôle global sur les 692 phrases réelles :**

- 692 phrases rendues, toutes commencées par « Le », toutes terminées par « . »
- 0 chaîne vide, 0 « undefined / null / NaN / [object », 0 prédicat orphelin (« et . », « , . »)
- 0 double espace, 0 espace avant ponctuation, 0 ponctuation doublée, 0 « de le / à le »
  (contractions « du / au / des » correctes partout)
- Structures de chaîne : 167 enchaînements « , qui … », 0 fallback « , et le … »
  (chaque maillon est toujours rattaché au précédent — chaînes cohérentes), « et » présent
  dans les 692 phrases (tête + liste, conforme au format annoncé)
- Longueurs : min 64, médiane 96, max 209 caractères — variation naturelle, pas de phrase
  tronquée ni d'accumulation mécanique.

Note de comptage : mon compteur d'informations donne 1551 atomes contre 1298 côté officiel ;
l'écart (253) = les 110 « ligne » + 143 « colonne » positifs, que la table ATTENDUS de
l'outil officiel ne couvre pas délibérément. Convention de comptage, pas un défaut.

## 2. Sens des phrases (lecture humaine)

Échantillon affiché — 8 premières phrases (énoncé 1) de chaque palier :

**Palier 1 (chaînes de voisinage, 3×3)**
- df-1-01 · Le cercle bleu est sur la ligne du milieu et juste à droite du triangle rouge, qui est juste en dessous du carré rouge.
- df-1-02 · Le triangle vert est sur la ligne du haut et juste à gauche du triangle rouge, qui est juste à gauche du carré rouge.
- df-1-03 · Le carré bleu est dans la colonne du centre et juste à gauche du cercle bleu, qui est juste au-dessus du carré vert.
- df-1-04 · Le carré vert est sur la ligne du bas et juste à gauche du cercle rouge, qui est juste en dessous du triangle rouge.
- df-1-05 · Le carré vert est dans la colonne de gauche et juste au-dessus du carré rouge, qui est juste à gauche du triangle bleu.
- df-1-06 · Le carré bleu est dans la colonne de gauche et juste au-dessus du triangle vert, qui est juste à gauche du carré vert.
- df-1-07 · Le carré rouge est dans la colonne du centre et juste au-dessus du cercle vert, qui est juste à droite du cercle bleu.
- df-1-08 · Le carré rouge est sur la ligne du bas et juste en dessous du carré vert, qui est juste en dessous du carré bleu.

**Palier 2 (négations simples)**
- df-2-01 · Le cercle vert n'est pas dans la colonne de gauche et n'est pas sur la même ligne que le carré rouge.
- df-2-02 · Le triangle rouge n'est pas dans un coin et n'est pas dans la même colonne que le cercle rouge.
- df-2-03 · Le cercle rouge n'est pas dans un coin et n'est pas sur la même ligne que le carré rouge.
- df-2-04 · Le cercle rouge n'est pas dans un coin et n'est pas dans la même colonne que le carré bleu.
- df-2-05 · Le triangle bleu n'est pas sur la ligne du bas et n'est pas sur la même ligne que le cercle rouge.
- df-2-06 · Le triangle bleu n'est pas sur la ligne du bas et n'est pas sur la même ligne que le triangle rouge.
- df-2-07 · Le triangle bleu n'est pas dans un coin et n'est pas dans la même colonne que le triangle rouge.
- df-2-08 · Le carré rouge n'est pas sur la ligne du bas et n'est pas dans la même colonne que le cercle rouge.

**Palier 3 (chaînes longues : diagonales, opposé, comparaison)**
- df-3-01 · Le carré vert est sur la diagonale montante (du coin haut droit au coin bas gauche) et sur la même ligne que le triangle bleu, à sa gauche, qui est à l'opposé du carré bleu, de l'autre côté du centre.
- df-3-02 · Le cercle rouge est sur la diagonale montante (du coin haut droit au coin bas gauche) et plus bas que le cercle bleu, qui est sur la même ligne que le triangle bleu, à sa gauche.
- df-3-03 · Le triangle rouge est sur la diagonale descendante (du coin haut gauche au coin bas droit) et à l'opposé du cercle bleu, de l'autre côté du centre, qui est sur la même ligne que le cercle rouge, à sa gauche.
- df-3-04 · Le cercle vert est sur la diagonale montante (du coin haut droit au coin bas gauche) et sur la même ligne que le triangle rouge, à sa gauche, qui est à l'opposé du triangle bleu, de l'autre côté du centre.
- df-3-05 · Le cercle bleu est sur la diagonale montante (du coin haut droit au coin bas gauche) et plus à droite que le triangle rouge, qui est sur la même ligne que le carré bleu, à sa gauche.
- df-3-06 · Le triangle bleu n'est pas dans un coin et à l'opposé du carré bleu, de l'autre côté du centre, qui est sur la même ligne que le cercle rouge, à sa gauche.
- df-3-07 · Le cercle bleu est sur la diagonale montante (du coin haut droit au coin bas gauche) et sur la même ligne que le cercle rouge, à sa gauche, qui est plus à droite que le triangle vert.
- df-3-08 · Le triangle vert est sur la diagonale montante (du coin haut droit au coin bas gauche) et sur la même ligne que le cercle rouge, à sa gauche, qui est à l'opposé du carré bleu, de l'autre côté du centre.

**Palier 4 (4×4 : lignes/colonnes numérotées, losange)**
- df-4-01 · Le carré vert n'est ni dans un coin ni sur le bord et juste au-dessus du losange bleu.
- df-4-02 · Le losange rouge est dans la colonne 3 et juste en dessous du triangle bleu.
- df-4-03 · Le carré vert est dans la colonne 4 et juste au-dessus du losange bleu.
- df-4-04 · Le carré rouge est dans la colonne 4 et juste en dessous du carré bleu.
- df-4-05 · Le triangle rouge est sur la ligne 3 et juste en dessous du losange vert.
- df-4-06 · Le losange vert est dans un coin et juste à droite du carré vert.
- df-4-07 · Le triangle vert est sur la ligne 1 et juste au-dessus du cercle vert.
- df-4-08 · Le carré rouge est dans la colonne 4 et juste à droite du triangle rouge.

**Contrôle sémantique indépendant** : chaque atome des 80 grilles (1551 informations) a été
re-vérifié contre la solution stockée (`reponse.grille`) avec ma propre table de vérité :
- « juste au-dessus » = sujet exactement une ligne **au-dessus** de la cible (cible une ligne en dessous du sujet) ✔
- « juste à gauche / à droite » = même ligne, colonnes adjacentes, sens corrects ✔
- « plus à droite / plus haut / plus bas » = comparaison stricte de colonne/ligne ✔
- les 8 négations (pas-voisin-*, pas-a-droite-de, pas-a-gauche-de, pas-au-dessus-de, pas-en-dessous-de) sont vraies pour la solution : aucune négation ne contredit la grille ✔
- « ni dans un coin ni sur le bord », « pas-bord », « opposé », « comparaison », « voisin-diagonale » cohérents ✔
- Résultat : **0 incohérence** sur 1551 informations (après correction d'un bug dans MON
  script de vérification, pas dans le produit : j'avais inversé gauche/droite).

Aucune phrase tronquée, aucun « et . », aucun double espace, aucun « undefined » sur la totalité.

## 3. Qualité de langue

- **Accords** : toutes les figures (carré, cercle, triangle, losange) sont masculines →
  « du carré bleu », « du losange jaune » systématiquement corrects ; aucun « de la losange ».
- **Contractions** : « que le … » correct ; 0 « de le / à le » sur 692 phrases.
- **Majuscules** : toutes les phrases commencent par « Le » ; aucune majuscule interne parasite.
- **Ponctuation** : point final partout, virgules de chaîne bien posées (« …, qui … », « …, à sa gauche »).
- **Longueur** : 64–209 caractères, médiane 96 — variation naturelle entre grilles.
- **Négations** : formulations idiomatiques (« n'est pas juste au-dessus du… »,
  « n'est pas plus haut que… », « n'est ni dans un coin ni sur le bord »).

**Formulation gênante repérée (mineure)** — quand un atome « à l'opposé …, de l'autre côté
du centre » est suivi d'une clause « , qui … », l'antécédent de « qui » est momentanément
ambigu (le lecteur peut le rattacher un instant à « le centre » avant de corriger) :
- df-3-03, énoncé 1 : « …à l'opposé du cercle bleu, de l'autre côté du centre, qui est sur la même ligne que… »
- df-3-18, énoncé 2 (phrase la plus longue, 209 car.) : même motif.

Le sens reste récupérable (tous les sujets de clause sont des figures nommées, jamais « le
centre »), et le contrôle sémantique confirme l'antécédent voulu. Amélioration facultative :
centrer l'apposition «, de l'autre côté du centre » en fin de clause quand un maillon
« qui » suit, ou redémarrer la chaîne par «, et le … ». Fréquence très faible, non bloquant.

## 4. Verdict

**Constats BLOQUANTS : aucun.**

**Constats mineurs :**
1. Lisibilité : « qui » momentanément ambigu après l'apposition « de l'autre côté du centre »
   (localisations : df-3-03 é1, df-3-18 é2). Optionnel, cosmétique.
2. Comptage : 1551 informations rendues vs 1298 annoncées — différence purement conventionnelle
   (l'outil officiel ne couvre pas « ligne »/« colonne » positifs : 110 + 143). Aucune action.

### Conclusion : **LIVRAISON POSSIBLE**

- Vérification officielle : conforme (8 dorées + 692 phrases / 1298 informations, 0 anomalie).
- Contrôle indépendant : 0 défaut de forme, 0 incohérence sémantique sur les 80 grilles,
  8 types négatifs + positifs rendus en français naturel et fidèle aux solutions.
