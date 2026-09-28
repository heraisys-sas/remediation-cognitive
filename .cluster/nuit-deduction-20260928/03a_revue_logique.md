# 03a — Revue logique (nuit Déduction, volet 3a)

- Dépôt : `remediation-cognitive`, branche `amelioration-deduction-20260927`, HEAD `5e39cfb`
- Sous-agent « Revue logique » — LECTURE SEULE ; ce rapport est le seul fichier écrit.
- Méthode : script Python **propre** (`.openclaw/tmp/verif_03a.py`, hors dépôt, écrit pour cette revue — pas celui des tests), important uniquement `tools/deduction_commun.py` (`_vrai_binaire`, `propager`, `pred_indice`, `resoudre_par_deduction`, `atomes`).
- Corpus : 80 grilles `df-*` réparties en 4 paliers de 20 (`content/entrainement/deduction/paliers/palier-0{1,2,3,4}.json`).
- Durée d'exécution des vérifications : 0,1 s (aucun timeout rencontré).

## 1. Défaut A — complémentarité des négations binaires

**Protocole** : pour n=3 (9 cases) et n=4 (16 cases), toutes les paires de cases distinctes (i1 ≠ i2) — 72 + 240 = 312 paires — croisées avec les 8 couples positif/négatif :

`voisin-gauche/pas-voisin-gauche`, `voisin-droite/pas-voisin-droite`, `voisin-dessus/pas-voisin-dessus`, `voisin-dessous/pas-voisin-dessous`, `a-droite-de/pas-a-droite-de`, `a-gauche-de/pas-a-gauche-de`, `au-dessus-de/pas-au-dessus-de`, `en-dessous-de/pas-en-dessous-de`.

Vérité évaluée par `_vrai_binaire` de `deduction_commun` : **2 496 tests**.

**Résultat : CONFORME.** Pour toute paire de cases distinctes et tout couple de types, `pas-X(i1,i2) == not X(i1,i2)` sans aucune exception. Le code des négations (`tools/deduction_commun.py`, bloc `pas-voisin-*` / `pas-a-droite-de` / `pas-a-gauche-de` / `pas-au-dessus-de` / `pas-en-dessous-de`) est l'exact complément du code positif.

**Note factuelle (mineure)** : le contenu généré n'exerce actuellement **aucun** type de négation binaire (0 occurrence dans les 80 grilles ; usage binaire relevé : `autre-colonne` 155, `voisin-droite` 121, `voisin-gauche` 120, `voisin-dessous` 99, `voisin-dessus` 99, `comparaison` 92, `oppose` 86, `autre-ligne` 65, `a-droite-de` 11, `au-dessus-de` 7, `en-dessous-de` 3, `voisin-diagonale` 1). Le correctif du défaut A est donc validé **au niveau du solveur** ; le contenu ne le couvre pas encore (aucune phrase `pas-*` binaire générée). Non bloquant : la conformité du prédicat est établie pour tout usage futur.

## 2. Défaut C — recoupement

**Protocole** (script propre, via `deduction_commun.propager`) : pour les 60 grilles des paliers 2, 3, 4 —
(a) chaque phrase propagée **seule** ne doit laisser aucun domaine singleton (ni contradiction) ;
(b) `rang_premiere_certitude` (propagation cumulée dans l'ordre de présentation) doit être ≠ 1.

**Résultats (paliers bloquants) :**

| Palier | n | Grilles | Phrases fixant seules | Grilles rang=1 | Autres anomalies |
|---|---|---|---|---|---|
| 2 | 3 | 20 | **0** | **0** | 0 |
| 3 | 3 | 20 | **0** | **0** | 0 |
| 4 | 4 | 20 | **0** | **0** | 0 |

**CONFORME** : aucune phrase prise seule ne détermine de position dans les 60 grilles des paliers 2-4, et la première certitude exige toujours ≥ 2 phrases cumulées. Aucune contradiction détectée à la propagation, aucune grille sans certitude.

**Palier 1 — mesure seule** (décision documentée : initiation séquentielle, non bloquant), 20 grilles n=3 :

- 1 grille : 0 phrase fixant seule, 1ʳᵉ certitude au rang 2 (ex `df-1-15`)
- 2 grilles : 0 phrase fixant seule, 1ʳᵉ certitude au rang 3 (ex `df-1-11`)
- 1 grille : 1 phrase fixant seule, 1ʳᵉ certitude au rang 1 (ex `df-1-20`)
- 5 grilles : 1 phrase fixant seule, 1ʳᵉ certitude au rang 2 (ex `df-1-03`)
- 4 grilles : 1 phrase fixant seule, 1ʳᵉ certitude au rang 3 (ex `df-1-01`)
- 2 grilles : 1 phrase fixant seule, 1ʳᵉ certitude au rang 4 (ex `df-1-10`)
- 4 grilles : 2 phrases fixant seules, 1ʳᵉ certitude au rang 1 (ex `df-1-02`)
- 1 grille : 2 phrases fixant seules, 1ʳᵉ certitude au rang 3 (ex `df-1-14`)

Bilan palier 1 : 6/20 grilles donnent une certitude dès la 1ʳᵉ phrase (rang=1) et 13/20 contiennent au moins une phrase fixant seule — conforme à la philosophie d'initiation « chaîne ordonnée » assumée (`PALIERS_RECOUPMENT_BLOQUANT = {2,3,4}`), non jugé.

## 3. Logique produit

**Périmètre** : contrôles sur les **80 grilles** (déductibilité, absence du type « case », unicité des combinaisons figure×couleur, vérité de chaque phrase pour la solution stockée, vérité des aides) + vérité/type/progressivité des aides détaillés sur un **échantillon de 3 grilles par palier** (rangs 1, 10, 20).

**Résultats :**

- **Déductibilité** : les 80/80 grilles sont entièrement déterminées par `resoudre_par_deduction` (propagation pure, sans hypothèse). 0 exception.
- **Aucun placement direct** : aucun énoncé (ni atome du champ `et`) ne contient le type « case » dans les 80 grilles. 0 exception.
- **Solution stockée** : chaque `reponse.grille` contient exactement n×n combinaisons figure×couleur **uniques** (9 pour n=3, 16 pour n=4). 0 exception.
- **Vérité des phrases** : chaque énoncé de chaque grille est vrai pour la solution stockée (`pred_indice` vrai pour tous les atomes). 0 exception.
- **Aides (`contenu.indices`)** : 3 aides par grille sur tout le corpus ; sur l'échantillon (12 grilles), toutes **vraies pour la solution** et de type `ligne` / `colonne` / `case` uniquement (progressives : position d'un jeton unique, jamais de relation binaire). Répartition observée dans l'échantillon : palier 1 = {ligne, colonne, case}, palier 2 = {case, ligne / case, colonne / colonne, ligne}, palier 3 = {ligne / colonne, ligne / case, ligne}, palier 4 = {colonne / case, ligne / case, colonne}.

Détail échantillon (phrases, aides, types d'aides, déductible) :

- `df-1-01` : 4 phrases, 3 aides {ligne, colonne}, True — `df-1-10` : 4/3 {case}, True — `df-1-20` : 4/3 {case, ligne}, True
- `df-2-01` : 11 phrases, 3 aides {case, colonne}, True — `df-2-10` : 11/3 {case, ligne}, True — `df-2-20` : 11/3 {colonne, ligne}, True
- `df-3-01` : 4 phrases, 3 aides {ligne}, True — `df-3-10` : 5/3 {colonne, ligne}, True — `df-3-20` : 4/3 {case, ligne}, True
- `df-4-01` : 16 phrases, 3 aides {colonne}, True — `df-4-10` : 15/3 {case, ligne}, True — `df-4-20` : 15/3 {case, colonne}, True

Densité observée : palier 1 = 4 phrases/grille ; palier 2 = 11 ; palier 3 = 4-5 ; palier 4 = 15-16.

## 4. Verdict

**Constats BLOQUANTS : aucun.**

**Constats mineurs (non bloquants) :**

1. **Négations binaires jamais exercées par le contenu** — fichiers `content/entrainement/deduction/paliers/palier-0{1,2,3,4}.json` (toutes grilles) : 0 occurrence des types `pas-voisin-*`, `pas-a-droite-de`, `pas-a-gauche-de`, `pas-au-dessus-de`, `pas-en-dessous-de`. Le correctif du défaut A est conforme dans `tools/deduction_commun.py` mais le générateur ne produit pas (encore) de phrases négatives binaires : la conformité n'est testée que par cette revue, pas par le contenu.
2. **Rarement exercés** : `a-droite-de` (11), `au-dessus-de` (7), `en-dessous-de` (3), `voisin-diagonale` (1) sur 80 grilles — présence très inégale des types relationnels.
3. **Palier 1** : 6/20 grilles avec certitude dès la 1ʳᵉ phrase, 13/20 avec au moins une phrase fixant seule — cohérent avec la décision « initiation non bloquée », rappelé pour trace.

### Conclusion : **LIVRAISON POSSIBLE**

- Vérification 1 (défaut A) : **conforme** (2 496 tests, 0 violation).
- Vérification 2 (défaut C) : **conforme** sur les 60 grilles des paliers 2-4 (0 phrase fixant seule, 0 rang=1) ; palier 1 mesuré, conforme à la décision documentée.
- Vérification 3 (logique produit) : **conforme** (80/80 déductibles, 0 « case », solutions et aides correctes, aides progressives ligne/colonne/case).
- Aucune correction requise pour livrer. Les constats mineurs 1-2 sont des pistes d'enrichissement pour le générateur, hors périmètre de cette nuit.
