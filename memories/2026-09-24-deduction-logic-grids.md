# 2026-09-24 — Déduction : méthode des logic grids (recherche + correctifs)

## La demande

« Renseigne-toi sur cet exercice et cette méthode pour bien l'implémenter. »

## Ce que dit la documentation

Deux principes reviennent dans les guides de construction de puzzles de logique :

1. **Chaque combinaison est unique** (« each combination should be unique ») — c'est la règle que l'utilisateur avait identifiée, et c'est elle qui rend les phrases non ambiguës.
2. **Aucune référence n'est répétée inutilement** dans un indice — pas d'indice décoratif, chaque phrase doit apporter une contrainte.

Et la taxonomie classique des indices : *true/false* (direct), *multi-elimination*, *neither/nor*, *either/or*, *greater/lesser*.

## Ce que ça a changé dans le code

- **Taxonomie complète implémentée** : `case` (direct), `ligne`/`colonne`, `voisin-gauche/droite/dessus/dessous` (voisinage), `comparaison` (à gauche de, même ligne), `autre-ligne`/`autre-colonne` (pas la même ligne/colonne), `pas-coin`, `pas-bord`, `ni-ni` (élimination), `si-alors` (**conditionnel**). Tous à deux informations.
- **Plus aucun indice décoratif** : mon générateur complétait jusqu'ici avec des « règles » répétées pour atteindre 6 indices — exactement le défaut que la documentation proscrit. Les indices sont maintenant **nécessaires** (4 à 9 selon la grille), et la règle générale est passée dans la **consigne**.
- **Méthode de résolution enseignée explicitement** : noter les certitudes → barrer les impossibilités → recouper les indices reliant deux figures. C'est la stratégie des logigrammes, et elle est écrite dans la consigne (cohérent avec le fil « méthodes » du logiciel).

## Bug attrapé au passage (et pourquoi il compte)

Les indices `voisin-gauche` et `voisin-droite` étaient **inversés** : la construction les créait avec une sémantique et le test les évaluait avec la sémantique opposée. Pire : le solveur acceptait un ensemble d'indices dès qu'il ne restait **qu'une seule** solution possible, **sans vérifier que c'était la bonne** — un indice faux pour la solution visée pouvait donc être retenu, et le puzzle stocké devenir incohérent.

Corrigé deux fois : la sémantique des voisinages est cohérente, et le solveur vérifie désormais que la solution survivante **est bien celle visée**. C'est le genre de garde-fou qui évite un puzzle insoluble livré à l'utilisateur.

## Reste à faire

- Passage visuel (grille, indices conditionnels, bouton « Un indice »).
- Relecture orthophoniste.
- Piste : une **grille de possibilités** (marquer les cases encore possibles) comme aide de résolution, à l'image du tableau qu'on utilise sur papier.


## 2026-09-25 — déductibilité garantie + stock 3 mois

Suite au retour « pas assez de phrases pour reconstruire la grille » :

- la **déductibilité** (résoluble par propagation, sans hypothèse) remplace la simple unicité comme critère de livraison. Solveur : `tools/deduction_commun.py` (domaines par case + règles + AC sur les indices binaires). Génération constructive : on ajoute des indices jusqu'à ce que le solveur termine ; le validateur refuse un puzzle non déductible ; un test rejoue le solveur sur tout le thème.
- stock étendu 16 → **80 grilles** (20/palier), **solutions toutes distinctes** (60/72 de l'univers 3×3, 20/6912 en 4×4). Le générateur prend `--par-palier` et échoue proprement si l'univers est épuisé.
- le solveur est *sound* mais incomplet : un `False` invite à ajouter des indices (prudent), un `True` prouve la déductibilité. C'est la marge de sécurité voulue.
- leçon : l'**unicité** ne suffit pas pour l'entraînement — un puzzle unique peut exiger des hypothèses (essayage) et devenir infaisable en rééducation. Toujours valider par un solveur qui raisonne comme la personne.

## 2026-09-25 (suite) — « aucune déduction n'est provoquée » : refonte des phrases

Retour utilisateur en trois points, tous fondés :

1. **Les règles n'étaient pas énoncées.** La consigne ne disait que « chaque figure colorée
   apparaît une seule fois », alors que le solveur et les grilles reposent sur les règles
   latines (chaque figure et chaque couleur une fois par ligne et par colonne). Avec les six
   placements directs de la première grille, les trois dernières cases restaient **ambiguës** :
   impossible de reconstruire. Leçon : les règles utilisées par le solveur doivent être
   exactement celles énoncées à la personne.
2. **Les phrases de palier 1 étaient des placements directs** — recopiage, zéro déduction.
   Corrigé : plus aucun placement direct (sauf 3 ancres en 4×4) ; chaque phrase porte
   **deux informations** qui se croisent (champ `et` : ligne + pas-colonne, colonne + pas-coin…)
   ou relie deux figures (relational, dont les nouvelles formes faibles `a-droite-de`,
   `au-dessus-de` qui obligent à combiner).
3. **L'outil manquait** : le logigramme papier se résout avec une grille d'élimination.
   Ajouté dans l'interface : tableau de déduction cliquable (✗ / ✓) sous la grille —
   mémoire de travail externalisée, comme en orthophonie.

Autres décisions techniques :

- sélection des phrases **par puissance** (fraction de l'espace éliminée) puis quota de
  phrases composées par palier — sans le quota, les phrases relationnelles (plus fortes)
  écrasaient toutes les composées ;
- le solveur est le juge : 80/80 grilles déductibles après refonte ;
- palier 4 : la grille 4×4 ne se referme pas par déduction pure sans point de départ →
  3 ancres maximum, phrases 13-18 ; paliers 1-3 : zéro ancre ;
- le validateur verrouille la pédagogie (aucun placement direct au palier 1, minimum de
  phrases composées) en plus de la déductibilité.

## 2026-09-25 (soir) — la règle latine était une invention : refonte en chaînes

Retour décisif de l'utilisateur : « ça n'est pas une règle générale ; les phrases d'indices
doivent contenir tous les éléments de la résolution du problème ».

- J'avais introduit les règles latines (figure et couleur une fois par ligne et par colonne)
  pour qu'un petit nombre de phrases suffise. C'était un raccourci de conception : la grille
  n'était alors pas reconstructible à partir des seules phrases. **Une règle non énoncée
  n'existe pas.**
- Nouveau socle : **une seule règle**, évidente — chaque figure colorée posée une fois, une
  figure par case. Le solveur n'utilise que ça (propagation de domaines + consistance d'arc
  sur les relations, plus « case déterminée » et « figure à une seule case possible »).
- **Phrases en chaîne** : un repère, puis des relations d'une figure à la suivante
  (« …, qui est juste au-dessus de … »). Trois informations et plus par phrase, donc peu de
  phrases : 4 au palier 1, 8 aux paliers 2-3, 15 en 4×4. Les phrases sont le seul support.
- Le tri par « force » ne suffisait pas : la sélection est maintenant **gloutonne pilotée par
  le solveur** (chaque étape prend la phrase qui minimise le nombre de cases encore ouvertes).
  C'est ce qui donne l'ensemble le plus court qui détermine la grille.
- Conséquence heureuse : l'univers des placements passe à 9! (et 16! en 4×4) — le stock long
  terme n'est plus contraint par les 72 grilles latines.
- Paliers différenciés par la **nature** des relations et des repères (voisinage → relations
  variées → repères négatifs + relations lâches → 4×4), sinon les paliers 2 et 3 se ressemblaient.
- Leçon générale à garder : ne jamais introduire une règle implicite pour simplifier la
  génération. Si la résolution dépend d'autre chose que de l'énoncé, l'exercice est faux.

## 2026-09-25 (nuit) — phrase tronquée : script périmé en cache

Symptôme signalé : « Le triangle vert est dans la colonne du centre et . ».

- Signature typique : **ancien script + nouveau contenu**. Le navigateur gardait `app.js`
  en cache ; l'ancien formateur (qui attendait `et` sous forme d'objet) recevait une liste
  et produisait un prédicat vide. Diagnostic confirmé en reproduisant la chaîne exacte.
- Correctif de fond : servir l'interface avec `Cache-Control: no-store` (sous-classe de
  `StaticFiles`) + deux tests sur les en-têtes. Ne jamais supposer que la page ouverte
  exécute le code publié.
- Bug réel trouvé au passage : mon nouveau formateur de chaînes **perdait les négations**
  (« Le carré rouge dans un coin » au lieu de « n'est pas dans un coin »). Corrigé en
  assemblant complément + négation + verbe en un seul endroit.
- Nouveau garde-fou : `tools/verifier_phrases.js` exécute le **vrai** code de rendu sur
  tout le contenu et refuse une phrase vide, sans verbe ou contenant « undefined ».
  Il a validé les 700 phrases après correction.
- Leçon : après un changement de format de contenu, le rendu doit être vérifié par un
  contrôle automatique exécutant le code réel — pas relu à l'œil.

## 2026-09-25 (soir) — relations de voisinage inversées

Signalement : « la solution inverse le haut et le bas par rapport aux phrases ».

- Les quatre types de voisinage étaient **inversés** : « voisin-dessus » était vrai quand la
  cible était au-dessus du sujet, alors que la phrase dit « le sujet est au-dessus de la
  cible ». Les paliers 1, 2 et 4 étaient donc insolubles (le palier 3, sans voisinage, passait).
- Cause de fond : le solveur et le générateur **partageaient la même fonction de prédicat**,
  donc toute erreur de convention était invisible ; seul le sens des phrases françaises
  pouvait la révéler — et rien ne le vérifiait.
- Ajout de `_sens_contredit` dans le validateur : **contrôle indépendant**, écrit d'après le
  sens français (« juste au-dessus » = une ligne en moins). Il a signalé les 540 phrases
  fautives du contenu précédent, puis 0 après régénération.
- Ajout côté interface : le vérificateur de phrases refuse qu'un type s'écrive autre chose
  que ce qu'il annonce (test négatif réalisé : 298 anomalies détectées en inversant le rendu).
- Leçon : quand deux composants partagent une convention, la vérifier par une **seconde
  lecture indépendante** (ici le français), jamais par le même code.

## 2026-09-25 (soir) — vocabulaire enrichi et chasse aux redondances

Demande : utiliser diagonales, coins, « à l'opposé de » ; éviter les indications redondantes.

- Ajout de types : `coin` (positif), `diagonale` / `diagonale-inverse` (+ négations),
  `voisin-diagonale`, `oppose` (symétrie par le centre). Le vocabulaire se décline par palier.
- Constat : la gloutonne pilotée par le solveur **sacrifiait le vocabulaire rare** au profit de
  chaînes plus longues (`oppose` présent 60 fois dans le vivier, jamais retenu). D'où
  `VOCABULAIRE_REQUIS` : une phrase au moins de chaque forme demandée, protégée du nettoyage.
- **Minimalisation** : après la sélection, toute phrase retirable sans perdre la déductibilité
  est supprimée — aucune indication redondante. Contrôle indépendant : retirer une phrase
  quelconque casse la déductibilité.
- Le test des relations énumérait les types à la main : il a raté les deux nouveaux. Corrigé en
  important `TYPES_BINAIRES` (source unique) plutôt qu'en recopiant la liste.
