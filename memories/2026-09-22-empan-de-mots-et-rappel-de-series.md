# 2026-09-22 — Empan de mots, rappel de séries et correctifs d'usage (sprint 4)

## Demandes reçues

1. Le champ de réponse devait être vidé quand on passe à la question suivante (bug signalé).
2. « Il me semble qu'il y a une pause de 2 secondes entre les éléments de l'empan de chiffres — corrige cela. »
3. « As-tu prévu une complexification progressive ? », « et l'empan de mots ? »
4. « Des tentatives plus tard, et à la fin d'un test demander quelle était la première série ou toutes les séries dont on se souvient — qu'en penses-tu ? »
5. Regrouper Python et Anglais dans une section « Extra » en bas de l'écran d'accueil.

## Constats factuels

- **Champ de saisie** : régression de mon fait — en réécrivant `afficherQuestion` (sprint 3), j'avais supprimé le bloc de remise à zéro. Corrigé, puis vérifié **dans le navigateur** (le champ est vide après « Suivant »). Un contrôle automatisé a été ajouté (`tools/verifier_interface.py`) pour qu'une telle suppression casse la vérification.
- **« Pause de 2 secondes »** : il n'y avait pas de pause de 2 s — un élément était affiché 800 ms, suivi d'un blanc de 250 ms. En revanche l'interface annonçait « 2 éléments · environ 2 s », formulation ambiguë qui pouvait se lire comme un temps de pause. Corrigé : rythme affiché explicitement (« un toutes les 0,92 s ») et blanc ramené à 120 ms (séparation visuelle seulement). Le validateur borne désormais le rythme (400–2000 ms par élément).
- **Complexification progressive** : vérifiée sur les données — empan de chiffres endroit 3 → 4 → 5 → 6, envers 3 → 4 → 5 → 6, paires 2 → 3 → 4, n-back N = 2 → 3 → 4, empan de mots 3 → 4 → 5 puis 3–4 envers.

## Livré

- **Empan de mots** : paliers 9 à 12 du thème mémoire (72 items), ordre significatif, saisie tolérante (accents/casse/ponctuation), pool concret sans doublon.
- **Thème « Rappel de séries »** : 4 paliers, 32 items — une série de 4 mots ; deux puis trois séries avec rappel **de l'ensemble** (interférence entre séries) ; **rappel différé** de 20 s sur toutes les séries, puis question sur la **première** série uniquement. Réussite au **seuil** (0,5–0,75) ; l'interface affiche retrouvés/manquants.
- **Interface** : section « Extra » (Python, Anglais) en bas de l'accueil ; compte à rebours visible et passable pour le rappel différé ; bandeau de série pendant l'affichage ; bilan de rappel sans verdict binaire.
- **Contrôles** : validateur enrichi (rythme, empan de mots, rappel libre : séries/portée/seuil/délai, unicité des mots) — il a attrapé un pool contenant « panier » deux fois ; `verifier_reponses` étendu (691 items, 0 anomalie) ; 110 tests.

## Décisions (ADR-005)

- Un item de rappel libre déclare `reponse.seuil` : la réussite est partielle par nature, et l'API renvoie la liste attendue pour que l'interface montre ce qui manquait.
- Le rythme de présentation est une invariante de contenu (400–2000 ms par élément) : plus de pause d'attente déguisée en empan.
- Un résultat de rappel partiel **reste un repère de séance** : jamais un score de mémoire comparable entre personnes.

## Mon avis sur le rappel de séries (réponse à la question posée)

Le paradigme est pertinent et cohérent avec la littérature : ce qui est difficile dans le rappel de plusieurs séries, c'est l'**interférence** entre listes et l'absence d'indice contextuel — c'est précisément ce qui est en jeu quand « l'information est là mais ne revient pas ». Le rappel différé ajoute une composante utile (résistance au délai). Trois précautions : (1) ne pas transformer le nombre de mots retrouvés en score, encore moins en norme ; (2) garder l'attente **courte et visible**, passable — sinon on mesure de la tolérance à la frustration ; (3) la « reprise plus tard » est mieux portée par le moteur (la même série redevient due dans une séance ultérieure) que par une répétition dans la même séance, où l'effet de récence fausse tout.

## Reste à faire

- Relecture orthophoniste des 72 items d'empan de mots et des 32 items de rappel libre.
- Vidage des courbes de rappel : aucun stockage de « taux de rappel » n'a été ajouté — si un jour un suivi est affiché, il devra rester descriptif et personnel.
