# Proposition — Palier « PQRST mis en œuvre »

**Statut** : **arbitrages rendus le 2026-09-27** — mise en œuvre prévue. Les décisions ci-dessous remplacent les questions ouvertes.

## Le constat

Le palier PQRST actuel (`mt-1-pqrst-*`) **teste le résultat** de la méthode sans la faire appliquer. Déroulé réel d'un item :

1. le texte s'affiche 25 s puis **disparaît** ;
2. une question de mémoire est posée (« À quelle heure est le rendez-vous ? ») ;
3. la personne choisit parmi trois propositions.

La méthode est **nommée** dans la consigne et rappelée dans le panneau « Méthode », mais jamais **mise en œuvre** : personne n'est amené à survoler, à se poser une question, ni à reformuler. L'exercice sollicite donc la mémoire, pas la stratégie — ce qui est cohérent avec la remarque d'usage, et avec le fait que PQRST *est* une méthode de mémorisation dont seul le résultat est vérifié ici.

## Ce que la méthode demande, et pourquoi chaque étape compte

| Étape | Ce que fait la personne | Appui scientifique |
|---|---|---|
| **P** — Parcours | survoler : titre, début, fin | donner un cadre avant de lire réduit la charge (Sweller, au socle du projet) |
| **Q** — Question | **écrire sa propre question** sur le texte | effet de génération ; oriente la lecture vers un but |
| **R** — Lecture | lire en cherchant la réponse à sa question | lecture guidée par un but : meilleur encodage |
| **S** — Reformulation | **redire le texte en une phrase, avec ses mots** | élaboration verbale : la stratégie d'encodage la plus efficace |
| **T** — Test | se tester de mémoire | pratique de récupération (Roediger & Karpicke, au socle du projet) |

Les deux étapes qui portent l'apprentissage (Q et S) sont **des productions**, pas des reconnaissances : c'est précisément ce qui manque aujourd'hui.

## Le palier proposé

**Un item = une séquence guidée complète**, sur un texte court (3 à 4 phrases, vie quotidienne), déroulée **dans le même item** — la séquence ne doit pas être interrompue par d'autres exercices.

### Déroulé d'une séquence

| Étape | Écran | Jugé ? |
|---|---|---|
| 1. **Parcours** (≈ 10 s) | le titre + la première phrase seulement → « De quoi parle ce texte ? » (3 propositions) | **oui** (choix) |
| 2. **Question** | « Écris la question que tu te poses sur ce texte. » → champ libre, puis affichage d'**une question possible** | **non** (production libre, modèle affiché) |
| 3. **Lecture** | le texte entier, au rythme de la personne, **sans chronomètre**, sa question restant affichée | — |
| 4. **Reformulation** | « Redis le texte en une phrase, avec tes mots. » → champ libre, jugé sur **4 idées-clés sur 5** (tolérance : accents, variantes, dictée), puis **résumé modèle** | **oui** |
| 5. **Test** | 2 questions de mémoire, comme aujourd'hui | **oui** |

### Ce qui est jugé, ce qui ne l'est pas

- **Jugé** : le parcours (choix), la reformulation (idées-clés), le test final (choix).
- **Non jugé** : la question personnelle — c'est une **production active**, pas une réponse juste ; un modèle est proposé ensuite, comme pour l'analyse de mot en évocation (les invites ne sont pas notées, seule la production compte).
- Tolérances habituelles appliquées (ADR-008) : accents, casse, variantes, dictée, « 15 heures » = « 15 h ».
- **Aucun chronomètre** sur la lecture : c'est la méthode qu'on entraîne, pas la vitesse (le minutage ne réapparaît que dans le palier « test » actuel).

### Dosage

Une séquence ≈ 2-3 minutes. **Quatre textes par palier** : une séance de ce palier dure donc ≈ 8-12 minutes, sans dépasser le cadre (séance courte, ≤ 10 min **proposée**, ADR-010). Aucun nouveau paramètre de séance nécessaire : le palier contient ce qu'une séance peut absorber.

### Placement dans la progression

**Un palier supplémentaire, placé après les paliers actuels** (donc après le PQRST « test » qui présente la méthode). Logique : on découvre la méthode, puis on l'applique. L'autre option — remplacer le palier 1 actuel — ferait disparaître la mesure du résultat ; elle est écartée par défaut.

### Identifiants

Nouveaux (`mt2-…`) : contenu entièrement neuf, il ne doit pas hériter des états de révision du PQRST actuel (règle de versionnage du contenu).

## Décisions retenues (2026-09-27)

1. **Seuil de la reformulation** : **4 idées-clés sur 5** — exigence soutenue, pas de validation à moitié. Le **résumé modèle** est montré dans tous les cas (réussi ou non).
2. **La question personnelle** : **champ libre**, avec une question modèle affichée ensuite. La production n'est pas notée : c'est l'acte de produire qui travaille.
3. **Nombre d'étapes** : **les 5** (PQRST complet), y compris pour les profils fragiles — la difficulté se règle par le contenu des textes, pas par la réduction de la méthode.
4. **Textes** : **4 phrases**, thèmes du quotidien (rendez-vous, colis, consignes d'appareil, courrier administratif).
5. **Récapitulatif** : en fin de séance, une **fiche méthode** de 5 lignes (les 5 étapes, formulées pour la vie réelle) que la personne garde hors écran.

## Coût et plan de mise en œuvre

| Travail | Contenu | Estimation |
|---|---|---|
| Contenu | générateur + 4 textes × 5 étapes, manifest, relecture | le plus gros poste, mais mécanique |
| Type d'item | `pqrst-mise-en-oeuvre` + jugement par étape (choix, production non jugée, idées-clés) | correction à écrire et tester |
| Interface | composant « séquence » montrant les cinq étapes et leur consigne au point d'usage | contenu dans l'app actuelle |
| Contrôles | validateur (structure des étapes, seuils, cohérence des modèles), tests de correction | à ajouter |

## Critères d'acceptation

- la personne **produit** au moins deux étapes par texte (sa question, sa reformulation) ;
- la séquence n'est jamais interrompue par un autre exercice ;
- rien n'est jugé qui ne doive l'être (production libre non notée, modèle affiché) ;
- la correction reste déterministe et testée ; les tolérances d'ADR-008 s'appliquent ;
- une séance de ce palier tient dans le cadre de durée, sans chronomètre sur la lecture ;
- la méthode reste **visible pendant l'exercice** dans les cinq étapes du composant guidé, sans panneau redondant.
