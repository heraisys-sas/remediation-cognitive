# ADR-007 — Déduction : la résolution tient dans les phrases

**Statut** : accepté (2026-09-26)

*Suivi (2026-09-26)* : le point 6 « dix minutes **proposées** » n'est plus propre à la déduction — la durée maximale est une proposition pour **tous** les thèmes (ADR-010). Le dosage de six grilles reste, lui, spécifique au thème.

## Contexte

Trois versions successives du logigramme ont été refusées pour la même raison de fond : la grille ne se reconstruisait pas à partir de ce qui était **écrit**.

1. **Des placements directs** (« le triangle vert est en haut à gauche ») : on recopie, il n'y a aucune déduction à faire.
2. **Une règle inventée** : pour qu'un petit nombre de phrases suffise, une règle latine a été ajoutée (chaque figure et chaque couleur une fois par ligne et par colonne) et présentée comme une règle du jeu. Or la personne ne pouvait pas terminer la grille avec ce qui lui était dit. **Une règle non énoncée n'existe pas.**
3. **Un sens inversé** : les quatre relations de voisinage (au-dessus / en dessous, à gauche / à droite) étaient inversées entre le nom de l'indice et sa signification — les phrases disaient le contraire de la solution. Le générateur et le solveur partageant la même fonction, l'erreur était invisible de l'intérieur.

## Décision

**1. Une seule règle, et elle est énoncée.** Chaque figure colorée se pose une fois, une case ne contient qu'une figure. Aucune autre règle n'est supposée : si une phrase n'est pas écrite, elle ne sert pas. La consigne porte cette règle, pas un rappel de convention cachée.

**2. Les phrases contiennent la résolution.** Une phrase est une **chaîne** : un repère, puis des relations d'une figure à la suivante (« …, qui est juste au-dessus du … »). Elle porte plusieurs informations, ce qui raccourcit l'exercice — surtout au début. Vocabulaire disponible : repères (`ligne`, `colonne`, `coin`), diagonales (descendante, montante) et leurs négations, voisinage droit **et** diagonal, « à l'opposé de » (symétrie par rapport au centre), comparaisons, négations.

**3. Aucune phrase redondante.** Toute phrase retirable sans perdre la solution est supprimée automatiquement. Le vocabulaire explicitement demandé est protégé de ce nettoyage, sinon le générateur le sacrifie aux chaînes les plus longues.

**3 bis. L'ordre des phrases est tiré au sort** (et vérifié : aucune position figée, aucun type de phrase systématiquement en tête). Les phrases du vocabulaire obligatoire étaient placées en premier : toutes les grilles d'un palier commençaient donc par le même type de phrase — une régularité visible qui met sur la piste sans rien dire de la solution.

**4. Le solveur est le juge.** Une grille n'est livrée que si **toutes** ses cases sont déterminées par propagation, sans hypothèse, avec la seule règle énoncée. Vérifié à trois endroits : à la génération, au dépôt (le validateur refuse), et par un test rejoué sur tout le contenu du dépôt.

**5. Deux contrôles indépendants du solveur** — parce qu'un contrôle qui partage le code du générateur ne peut pas voir une convention fausse :

- le **sens** de chaque phrase est relu selon le français (« juste au-dessus » = une ligne en moins), indépendamment du solveur ;
- l'**interface** doit écrire chaque type de relation comme il s'annonce : `voisin-dessus` ne peut pas produire « en dessous ».

**6. Dosage propre au thème.** Six grilles par séance (une grille dure plusieurs minutes) et dix minutes **proposées** : la séance invite à s'arrêter, elle ne se ferme pas d'elle-même. S'arrêter au milieu d'un raisonnement serait brutal.

## Conséquences

- (+) La résolution ne dépend que de ce qui est lu : plus de règle cachée, plus de phrase qui dit le contraire de la solution — les deux échecs constatés sont désormais impossibles sans qu'un contrôle proteste.
- (+) Le vocabulaire est vérifié des deux côtés (sens et rendu), et le dosage est cohérent avec la nature de l'exercice.
- (+) L'univers des placements est immense (9! en 3×3) : le stock long terme n'est plus limité par le contenu possible.
- (−) Les phrases sont **plus nombreuses** qu'avec des placements directs (4 au palier 1, jusqu'à 17 en 4×4) : c'est le prix d'une déduction réelle.
- (−) Toute nouvelle forme d'indice demande **trois** écritures : le prédicat, le rendu français, et sa relecture de sens. Un type ajouté sans les trois fait échouer les contrôles.
- (−) La génération est plus lente (quelques dizaines de secondes pour tout le thème) : elle est hors ligne, sans effet à l'exécution.
