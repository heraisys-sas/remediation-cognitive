# État de l'intégration — 20:30 (coordinateur)

## Ce qui est fait et validé

- **Défaut A** : corrigé et committé (`69755a7`). Repro vérifiée : case0→case3, `voisin-dessus`=True et `pas-voisin-dessus`=False. Complémentarité des 8 paires positif/négatif vérifiée sur TOUTES les paires de cases distinctes, n=3 et n=4. Tests dans `backend/tests/test_deduction.py` (appariement positif↔négatif déclaré explicitement, indépendant des libellés).
- **Défaut B** : corrigé et committé (`3eedc97`). Les 8 types négatifs rendus dans `relationAtome`. `tools/verifier_phrases.js` étendu : 8 phrases dorées exactes sur le VRAI code de rendu + contrôle de sens sur tout le contenu (721 phrases, 1145 informations : 0 anomalie).
- **Outil de mesure** : `tools/mesurer_difficulte.py` fonctionnel (`--csv`). État AVANT archivé : `.cluster/nuit-deduction-20260928/contenu_avant/` + `mesures_avant.csv` (80 grilles).
- Baseline tests : 206 passed, validateurs verts.

## Mesures AVANT (extrait utile)

- palier 1 : 15/20 grilles avec phrase-solo (toléré : palier séquentiel d'initiation, critères C visent les paliers avancés), redondances entre phrases 0/20.
- palier 2 : 0 phrase-solo mais **10/20 grilles avec phrases retirables** (redondance entre phrases) ; redondances internes moyennes 8,6.
- palier 3 : **20/20 grilles avec une phrase qui fixe SEULE le centre** — c'est systématiquement une chaîne ancrée par `ni-ni` ou `pas-bord` + `voisin-diagonale` (sur 3×3, « ni coin ni bord » = le centre : placement direct déguisé). 4/20 grilles avec phrases retirables.
- palier 4 : 0 phrase-solo, 5/20 grilles avec phrases retirables.

## Diagnostic génération (constaté par le coordinateur)

1. **Le contenu stocké provient d'une grammaire antérieure** (GRAINE 20260925) : le palier 3 stocké utilise des ancres `ni-ni`/`pas-bord`/`pas-ligne`/`pas-colonne` et des chaînes `voisin-diagonale`/`comparaison`, que le générateur ACTUEL ne produit plus (palier 3 committé = ancres {coin, diagonale, diagonale-inverse} + relations relatives). La régénération avec le générateur actuel est donc indispensable pour le palier 3 (son stock viole les critères C) et souhaitable pour le 2 (redondances).
2. **Le blocage de la nuit du 27** (20–30 min sans résultat) est cohérent avec des grammaires « pures » : palier 2 tout-négatif (ancres négatives + relations négatives) et palier 3 tout-relatif (ancres {coin, diagonale…} + relations relatives lâches) ferment mal l'espace : le solveur n'aboutit jamais, la boucle d'essais tourne.
3. **Incohérence repérée** : `VOCABULAIRE_REQUIS[2] = {diagonale, diagonale-inverse, voisin-diagonale}` n'est **pas réalisable** avec la grammaire du palier 2 (ni `ANCRES_PAR_PALIER[2]` ni `RELATIONS_PAR_PALIER[2]` ne contiennent ces types) → la boucle « obligatoires » ne trouve rien, silencieusement. À aligner (requis ∩ réalisable).
4. **Modification locale non commitée** (`git diff tools/generer_deduction.py`) : ajoute `pas-a-droite-de`, `pas-a-gauche-de`, `pas-au-dessus-de`, `pas-en-dessous-de` aux relations du palier 3. Jugement du coordinateur : **à conserver** — elle mixe du négatif dans le relatif (anti-grammaire-pure) et élargit le vivier ; les critères C bloqueront de toute façon les phrases qui fixent seules une position. Ne pas l'annuler.

## Consignes de reprise (leçons des interruptions de 17:26)

- Travailler par petites étapes, chacune bornée ; **commit à chaque jalon vert**.
- Écrire le fichier rapport **dès le début** et le mettre à jour au fil de l'eau (jamais tout à la fin).
- Pas de lecture intégrale des gros fichiers : `grep`/`sed`/lectures ciblées avec offset/limit.
- Timeout shell sur chaque commande ; jamais de génération non surveillée.
