# ADR-005 — Rappel libre de séries, empan de mots et rythme d'affichage

**Statut** : accepté (2026-09-22)

## Contexte

Trois manques ont été identifiés à l'usage :

1. **Rappel libre** : après avoir mémorisé plusieurs petites séries, la question cliniquement intéressante n'est pas « restitue la liste » mais « qu'est-ce qui te revient ? » — un paradigme de récupération sans indice, dont le résultat est **partiel** par nature.
2. **Rappel différé** : une attente entre l'apprentissage et la question change complètement la difficulté (l'information n'est plus appuyée sur le contexte immédiat).
3. **Empan de mots** : le thème mémoire n'offrait que du matériel numérique ; le rappel verbal (mots) est une autre composante de la mémoire de travail.

S'y ajoutaient deux défauts constatés en usage réel : le champ de saisie n'était pas vidé entre deux questions (corrigé), et le rythme de présentation était ambigu — l'interface annonçait « 3 éléments · environ 3 s », ce qui pouvait se lire comme un temps de pause (corrigé).

## Décision

**1. Type `empan-mots`** — séquence de mots présentés un à un, rappel **dans l'ordre** (ou envers). La comparaison est ordonnée mais tolérante à la saisie (accents, casse, ponctuation). Aucun mot ne se répète dans une séquence.

**2. Type `rappel-libre`** — plusieurs séries de mots puis rappel libre :

- `contenu.affichage` : `{ "mode": "series", "series": [[mot, …], …], "duree_par_item_ms": int, "pause_serie_ms": int }` ;
- `contenu.delai_s` : attente (0 à 180 s) entre l'affichage et la question — **rappel différé** ; l'attente est visible et peut être passée ;
- `contenu.portee` : `toutes-series` (rappel de tout) ou `premiere-serie` (rappel de la première série seulement) ;
- `reponse.valeur` : **liste** des mots cibles ; `reponse.seuil` : proportion de mots à retrouver (0,25 à 1).

**3. Correction dédiée** : rappel libre réussi si la part de mots retrouvés atteint le seuil — ordre indifférent, accents et casse ignorés, pluriel simple toléré, mots en trop sans pénalité. L'API renvoie la liste attendue, ce qui permet à l'interface d'afficher **retrouvés / manquants** plutôt qu'un verdict binaire.

**4. Invariants validés automatiquement** (`tools/validate_items.py`) :

- rythme d'affichage **400–2000 ms par élément** (au-delà, ce n'est plus une présentation d'empan mais une pause) ;
- aucun mot dupliqué dans une séquence ni entre les séries d'un même item (le comptage serait ambigu) ;
- cibles déclarées = mots réellement affichés (selon la portée) ;
- seuil borné, délai borné, modes d'affichage connus.

## Conséquences

- (+) Les paradigmes de **rappel libre** et de **rappel différé** sont représentables sans toucher au moteur : un item reste un item, la difficulté vient du contenu.
- (+) La réussite partielle est **explicite** (seuil déclaré) au lieu d'un faux tout-ou-rien, et l'interface montre ce qui manquait — la valeur pédagogique est dans ce retour, pas dans le verdict.
- (+) Le rythme de présentation devient une invariante du contenu : impossible de « glisser » une pause d'attente dans un empan par inadvertance.
- (−) Un item de rappel libre occupe plus de temps (affichage de plusieurs séries + attente éventuelle) : le plafond de 12 items et le garde-fou de 600 s par séance restent la protection de dosage.
- (−) Un résultat partiel **n'est pas une mesure de mémoire** : aucun score normé ne doit être construit à partir de ces seuils (garde-fou clinique inchangé).
