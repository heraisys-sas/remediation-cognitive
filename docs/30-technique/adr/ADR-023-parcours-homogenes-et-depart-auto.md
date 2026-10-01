# ADR-023 — Progressions homogènes et départ automatique ajusté

**Statut** : accepté (2026-10-01).

## Contexte

Plusieurs cartes faisaient avancer un palier commun à des tâches différentes : empans de chiffres, associations et empans de mots ; accès lexical et mémoire de la source ; six méthodes sans ordre de difficulté commun. Une réussite dans une famille pouvait donc ouvrir une autre famille sans en démontrer la maîtrise. À l'inverse, faire recommencer systématiquement un adulte de niveau antérieur élevé par trois chiffres, un QCM lexical ou une seule série de quatre mots risque de rendre les premières séances peu crédibles.

## Décision

Les cartes restent regroupées par intention, mais proposent des **parcours indépendants**. Chaque parcours a ses propres cartes FSRS, son palier, son historique de maîtrise et sa baseline de temps. Le quota de séances reste commun au thème : changer de parcours ne multiplie pas le nombre de séances autorisées.

| Carte | Parcours indépendants |
|---|---|
| Retenir et manipuler | chiffres endroit ; chiffres envers ; mots ; associations mot–nombre ; position dans une séquence |
| Mémoriser des séries | immédiat ; différé ; première série seulement, séparément pour les mots lus et entendus |
| Méthodes | les six familles existantes, dont PQRST guidé directement accessible |
| Garder le cap | reprendre ; adapter ; vérifier |
| Retrouver des mots et leur contexte | accès lexical ; mémoire de la source ; stratégie SFA ; stratégie PCA |

Les stratégies SFA et PCA deviennent des choix autonomes : elles ne sont plus des niveaux obligatoires après la mémoire de la source.

Pour un parcours **sans historique**, le mode automatique commence à un niveau qui évite une entrée manifestement faible tout en conservant le niveau 1 dans le sélecteur d'essai :

- chiffres endroit : palier 3, soit cinq chiffres ;
- mots : palier 2, soit quatre mots ;
- associations : palier 2, soit trois paires ;
- séries immédiates, lues ou entendues : palier 2, soit deux séries de trois mots ;
- accès lexical : palier 2, rappel libre avec indices facultatifs, sans imposer d'abord le QCM.

Les parcours qui introduisent une manipulation nouvelle commencent au palier 1 : ordre inverse, position dans une séquence, rappel différé et sélection de la première série. Les familles à un seul niveau restent également au palier 1. Le niveau initial est écrit dès le premier démarrage automatique afin qu'une séance interrompue ne fasse pas retomber le parcours au niveau 1.

## Compatibilité

Les anciens dossiers (`memoire`, `methodes`, `evocation`, etc.) sont conservés. Les nouveaux états utilisent une clé distincte, par exemple `memoire--mots`. Aucune maîtrise d'une ancienne progression composite n'est convertie ou interprétée comme la maîtrise d'un parcours plus précis. Les identifiants et le contenu des exercices ne changent pas.

Le programme de huit semaines demande lui aussi le parcours avant de démarrer. L'API garde le fonctionnement historique quand `parcours` est absent, pour les anciens clients et les outils de contrôle.

## Limites

Ces départs sont des choix de conception pour le public visé, pas des normes. Le sélecteur permet de revenir immédiatement à un niveau inférieur. Une calibration adaptative à partir de quelques essais demanderait un signal plus fin que la réussite binaire actuelle ; elle reste hors de ce lot.
