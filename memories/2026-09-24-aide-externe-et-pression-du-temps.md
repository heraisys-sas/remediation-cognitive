# 2026-09-24 — Aide externe et pression du temps (paliers 7 et 8)

## Demande

Après ma recommandation : « la mémoire prospective (choisir l'aide externe adaptée) et la vitesse de traitement en situation écologique ».

## Livré

- **Palier 7 — Aide externe adaptée** (`aide-externe`, 8 items) : pour chaque situation à ne pas oublier, choisir l'aide la plus efficace. La règle enseignée : une aide est utile quand elle est **au bon endroit, au bon moment, et visible juste avant l'action**. Les deux leurres de chaque item sont toujours les mêmes erreurs réelles : « compter sur sa mémoire » et « écrire dans un carnet qu'on ne relit pas ».
- **Palier 8 — Gestion de la pression du temps** (`gestion-du-temps`, 8 items) : décider vite de l'essentiel, simplifier, préparer à l'avance, dire en une phrase qu'on est pressé, s'arrêter quand la fatigue monte avant de conduire.

## Décision assumée : pas d'exercice chronométré

Pour la vitesse de traitement, je n'ai **pas** implémenté d'épreuve chronométrée. Trois raisons : ces épreuves sont fatigantes pour un public post-commotionnel, elles installent une pression qui nuit à la mémoire de travail, et leur transfert aux activités quotidiennes est faible. Ce qui aide en situation, c'est de **gérer la demande** (simplifier, prioriser, anticiper) — l'objet du palier 8, dans l'esprit du *Time Pressure Management*. C'est aussi cohérent avec le garde-fou « on ne chronomètre pas le rappel » posé au sprint 2. Si l'impression de lenteur persiste chez l'utilisateur, c'est un signal à porter devant le professionnel, pas à travailler au chronomètre.

## Contrôles

**851 items / 0 erreur** ; **135 tests** ; garde-fous cliniques sans violation.

## Reste à faire

- Passage visuel des écrans ; relecture orthophoniste.
- Piste : un « carnet de stratégies » consultable (résumé des aides vues), qui donnerait une trace écrite des méthodes — à discuter avec la spécialiste.

## 2026-09-26 — dosage de la déduction : six grilles, même durée

Demande : 6 exercices au lieu de 12 par séance, et 15 minutes au lieu de 10.

- Vérification faite dans `docs/10-clinique/` : le cadre dit **séance courte ≤ 10 min** et
  « 5-10 min » ; la fatigue reste une proposition. Étendre à 15 minutes serait une exception
  au cadre, qui doit être documentée explicitement — je ne l'ai donc pas prise seul.
- Décision appliquée : **on ajuste le nombre d'exercices, pas la durée** → 6 grilles pour la
  déduction, 10 minutes inchangées. Douze grilles de raisonnement ne tenaient de toute façon
  pas dans une séance (cause du mur de durée signalé juste avant).
- Mécanisme : `dosage.parametres_seance(theme)` (table `PARAMETRES_THEME`) → le dosage devient
  une propriété du thème, pas une constante globale. Toute future adaptation passe par là,
  avec sa justification dans les protocoles.
