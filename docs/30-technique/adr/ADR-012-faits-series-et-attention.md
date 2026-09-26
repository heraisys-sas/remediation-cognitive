# ADR-012 — Contenus numériques : faits difficiles, séries et attention soutenue

**Statut** : accepté (2026-09-26) — **périmètre corrigé le jour même**

> **Périmètre** : la **dyscalculie est hors périmètre de ce POC** (elle a été incluse par erreur au premier jet de cette décision). Le palier de « sens du nombre » qui en découlait a été retiré le jour même, ainsi que ses contrôles. Ce qui reste — faits difficiles, séries, attention soutenue — vise la population du projet : adultes présentant des troubles cognitifs **acquis** (post-commotionnels).

*Suivi (2026-09-26)* : deux **séries complémentaires** ont été ajoutées, pour travailler ces difficultés autrement que par le calcul direct — *Suites et erreurs* (continuer une suite, repérer le nombre qui ne suit pas : attention soutenue et inhibition) et *Faits à l'envers* (« 42 = 6 × ? », le fait cherché par l'autre bout). Et une règle d'outillage : **un contrôle doit mesurer sa propre couverture**. Le contrôle par recalcul d'ADR-011 était devenu silencieusement inopérant pour plusieurs familles (un « ? » non échappé dans un motif) : le validateur mesure désormais la part d'items réellement recalculés (92 % du thème ; seule la famille « vie quotidienne » échappe au calcul automatique) et un test vérifie chaque forme d'énoncé.

## Contexte

ADR-011 a refondu le calcul mental autour des besoins d'un adulte (faits de base, stratégies, mémoire de travail, numératie du quotidien). Trois publics avaient été envisagés dans le même mouvement — le **premier s'est révélé hors périmètre** (voir la note ci-dessus) :

1. *(retiré)* **dyscalculie** — un trouble du **sens du nombre** : la difficulté ne porte pas d'abord sur les faits arithmétiques mais sur la représentation du nombre (grandeur, position, valeur de position, décomposition). Entraîner les tables ne soigne pas ce socle ;
2. **maintien de l'attention** — la difficulté est de **tenir** l'effort, pas de savoir calculer : ce qui se travaille, c'est la longueur de la série tenue de tête, avec une stratégie de vérification ;
3. **lacunes sur certaines multiplications** — une personne peut connaître 3 × 4 et ignorer 7 × 8. Une progression « une table par palier » la fait réciter ce qu'elle sait déjà au lieu de travailler ce qui manque.

## Décision

**2. Un palier de faits difficiles (lacunes ciblées)** — `calcul-mental`, palier 10 : × 6 à × 9, carrés compris, travaillés par **stratégie** et non par récitation. L'aide enseigne l'appui sur ce qui est su : « × 9 = × 10 − le nombre », « × 8 = double de × 4 ». La répétition espacée fait le reste : sur ces items, ce sont les faits effectivement manqués qui reviennent le plus.

**3. Les séries tiennent l'attention** — `concentration` : les chaînes vont de 3 à 7 opérations, avec l'aide « calcule de gauche à droite, étape par étape » et, pour les cascades, « retranche toujours le même nombre — garde le rythme ». Ce qui progresse, c'est la **longueur tenue**, jamais la vitesse.

**4. Le dépôt recalcule les totaux.** Le contrôle indépendant d'ADR-011 est étendu : les séries de calcul sont recalculées de gauche à droite à partir de l'énoncé, et refusées en cas de discordance.

## Conséquences

- (+) Les trois publics disposent d'une progression qui va à leur difficulté : socle du nombre, faits manquants, endurance de l'attention.
- (+) Aucune récitation inutile : ce qui est connu ne sera pas resservi indéfiniment, puisque la sélection se fait par faits manqués.
- (+) Un total de série faux ou un énoncé mal associé est arrêté au dépôt, pas en séance.
- (−) Le palier des faits difficiles liste des faits choisis à la main : il faudra l'enrichir si l'usage montre d'autres faits manqués récurrents.
- (−) La **dyscalculie** (trouble développemental du sens du nombre) n'est pas traitée : elle sortirait du périmètre du projet, qui vise des difficultés **acquises** chez l'adulte.
