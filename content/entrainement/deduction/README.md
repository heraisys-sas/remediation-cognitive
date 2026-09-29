# Déduction — cinq paliers, 100 grilles

Chaque figure colorée est utilisée une fois et chaque case reçoit un pion. **Toute autre contrainte doit être écrite dans les indices de la grille en cours**. Aucune répartition des formes ou couleurs n'est une règle permanente.

## Progression

| Palier | Grille | Travail proposé |
|---|---|---|
| 1 | 3×3 | Repères et voisinages ; chaînes guidées, puis informations à relier soi-même |
| 2 | 3×3 | Exclusions de catégories et de positions ; retrait progressif des repères positifs |
| 3 | 3×3 | Répartition d'une catégorie, relations et entre-deux ; extrémités nommées puis partielles, enfin sans voisinages immédiats |
| 4 | 3×3 | Diversité explicite, exclusions, entre-deux partiel et relations croisées ; derniers exercices sans repères individuels de ligne/colonne |
| 5 | 4×4 | Synthèse de ces familles ; entre-deux diagonal à partir de l'étape 2, davantage de positions à départager |

20 grilles par palier : 7 d'introduction, 7 intermédiaires et 6 de synthèse (`contenu.etape_progression`). C'est une progression de **contraintes pédagogiques**, pas une échelle de difficulté cognitive étalonnée : une grille peut être subjectivement plus facile que la précédente.

Les nouveautés suivent cet ordre. Lorsqu'il existe aussi des révisions dues, la moitié des places de la séance est réservée aux nouveautés ; les révisions avancées passent avant les anciennes grilles faciles. La maîtrise exige trois séances réussies selon le critère existant, **chacune comprenant une réponse de l'étape finale**. Les seules étapes préparatoires ne valident pas le palier. Le choix manuel du palier reste disponible.

## Familles d'indices

- Repères, exclusions individuelles, voisinages, comparaisons, diagonales et opposition par symétrie centrale.
- **Exclusion collective** : aucune figure d'une couleur ou d'une forme dans une ligne/colonne.
- **Répartition** : exactement un pion d'une catégorie dans une région, ou dans chaque ligne/colonne.
- **Diversité** : exactement un pion de chaque forme ou couleur dans la région indiquée. C'est un indice local au puzzle.
- **Entre-deux** : un pion se trouve strictement entre deux autres sur une ligne, colonne ou diagonale à 45°. Les extrémités peuvent n'être désignées que par leur forme ou couleur. Elles sont deux pions distincts, choisis parmi ceux de la palette. La distance et le voisinage immédiat ne sont pas imposés.

Une phrase peut porter une ou deux informations utiles ; aucune longueur minimale artificielle. Les phrases collectives restent autonomes. Les longues chaînes de l'initiation se raccourcissent progressivement.

Sur une grille 3×3, « entre deux pions sur une diagonale » donnerait immédiatement le centre. Le générateur réserve donc cet indice au 4×4, pour conserver le recoupement exigé aux paliers avancés. Les autres indices diagonaux restent disponibles en 3×3.

## Garanties vérifiées

- Chaque réponse satisfait les indices ; contrôle séparé de leur sens et de leur formulation française.
- Chaque grille se résout par éliminations et propagation de contraintes, sans recherche par hypothèses.
- Un second algorithme, qui n'appelle pas le propagateur de génération, cherche jusqu'à deux solutions et confirme **l'unicité et l'identité avec la réponse enregistrée**.
- Aux paliers 2–5, aucune phrase seule ne fixe une position : énumération des placements pour les relations individuelles/entre-deux, symétrie des pions d'une catégorie pour les contraintes collectives autonomes.
- Retirer une information conservée empêche la résolution complète par le propagateur. Cette nécessité pour la preuve utilisée **ne signifie pas** que chaque information serait indispensable à l'unicité mathématique ; ce sont deux propriétés distinctes.
- Des tests comparent les contraintes collectives à un oracle indépendant sur 2 160 affectations, dont des configurations non latines, des contradictions et des références partielles.

Ces contrôles structurels ne démontrent ni une équivalence clinique avec un matériel papier ni une efficacité thérapeutique. La relecture orthophonique reste `a_revoir`.

## Utilisation et génération

Six grilles au maximum par séance ; à dix minutes, l'arrêt est proposé. Trois aides de secours sont disponibles sur demande. Le tableau de déduction permet de noter les possibilités sans placer prématurément un pion.

```sh
python3 tools/generer_deduction.py
python3 tools/validate_items.py
python3 tools/verifier_unicite_deduction.py
python3 tools/mesurer_difficulte.py
node tools/verifier_phrases.js
```

Génération déterministe, graines isolées par palier, solutions distinctes et identifiants dérivés du contenu. Cette refonte **remplace le corpus de 80 grilles par 100 grilles avec de nouveaux identifiants** : les anciennes cartes de répétition espacée ne sont pas réaffectées à de nouveaux exercices. Le palier courant enregistré est préservé ; l'ancien palier 4 propose maintenant le 3×3 avancé, le 4×4 se choisit au palier 5.
