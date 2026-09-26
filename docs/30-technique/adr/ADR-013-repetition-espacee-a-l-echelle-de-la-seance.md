# ADR-013 — Répétition espacée : l'unité est la séance quotidienne, pas la minute

**Statut** : accepté (2026-09-26)

## Contexte

Signalement : « j'ai eu l'impression de retrouver plusieurs fois la même série dans *méthodes* et ailleurs ».

Vérification faite sur les données réelles : dans *méthodes*, **les 12 cartes du palier 1 étaient toutes dues en même temps**, chacune avec une échéance située **dix minutes après sa révision**. Or le palier 1 compte exactement 12 items et une séance en sert 12 : chaque séance de la journée resservait donc **tout le palier**, à l'identique.

Cause : le planificateur FSRS utilisait ses **pas d'apprentissage par défaut — 1 minute et 10 minutes**. Ces pas viennent des applications de révision continue (Anki), où l'on revoit une carte plusieurs fois dans l'heure. Ici, le logiciel se pratique en **séances quotidiennes** (1 à 3 par jour) : une échéance à dix minutes signifie « due tout de suite, toute la journée ».

## Décision

**1. Les pas d'apprentissage et de réapprentissage sont à l'échelle du jour** (`timedelta(days=1)`). Conséquences mesurées sur ce poste :

| Réponse | Échéance |
|---|---|
| Bon | 2 jours |
| Encore (échec) | le lendemain |
| Facile | 8 jours |

Rien n'est dû dans l'heure ni dans la même journée. La répétition espacée retrouve son rôle : elle **étale** dans le temps, elle n'entasse pas dans la journée.

**2. Le rythme est donné par le programme, pas par le minuteur.** C'est le programme de 8 semaines qui propose chaque thème environ deux fois par semaine ; les cartes redeviennent dues quand le thème revient. Le seuil de maîtrise reste clinique (90 % sur 3 séances au même palier).

**3. Une erreur revient une fois, en fin de séance, avec sa réponse.** C'est le complément d'errorless learning : un exercice manqué (et non assisté) est **réinséré en fin de séance**, avec la réponse fournie avant le nouvel essai. Bornes : **une reprise par exercice**, **quatre au maximum par séance** (la séance ne double pas ; au-delà, la répétition espacée ramène les autres le lendemain). Un essai déjà assisté — où les indices ont donné la réponse — n'est pas repris. La reprise ne modifie ni la note FSRS ni le taux de réussite : c'est la **première** réponse qui fait foi.

**3 bis. Le signalement est dans le fil de l'exercice, pas sur l'accueil.** Deux moments, au moment où l'information sert :

- **après une erreur** : le retour annonce « Cet exercice reviendra une fois en fin de séance, avec la réponse » ;
- **à la reprise** : une note affiche la réponse (« la réponse est « … » — il s'agit de la réancrer, pas de la deviner »), et le total de la séance s'ajuste.

Pourquoi pas un avis sur l'écran d'accueil : une consigne générale (« certains exercices reviennent deux fois ») serait abstraite et n'aiderait à rien ; l'information utile est **celle qui accompagne l'erreur** — c'est là qu'elle évite l'inquiétude (« pourquoi je revois ça ? ») et qu'elle garde son sens pédagogique.

**4. Une séance qui ne propose rien ne coûte rien** : si aucun item n'est dû et qu'il n'y a rien de nouveau, la séance est vide — elle **ne consomme pas** le quota des trois séances quotidiennes, et une séance sans réponse n'est pas historisée (elle ne peut donc pas faire reculer un palier).

## Base clinique (vérifiée le 2026-09-26)

La décision a été confrontée aux sources disponibles. La recherche en ligne est pauvre sur ce point précis ; les appuis solides sont :

- **Ebbinghaus (courbe d'oubli) et la répétition espacée** — déjà au socle du projet (`docs/10-clinique/bibliographie.md`) : une information se retient mieux revue à **intervalles croissants** que répétée en bloc. Revoir le même palier dix minutes plus tard est de la **pratique massée**, c'est-à-dire l'inverse de ce que la répétition espacée prescrit.
- **Spaced Retrieval (SR)** — rappel d'une information à des **intervalles de plus en plus longs**, technique développée en gériatrie et **étendue à l'aphasie et au traumatisme crânien** (« Spaced Retrieval Using Static and Dynamic Images », *ASHA*, 2019) : la littérature orthophonique place bien la répétition dans le temps, pas dans la minute.
- **Errorless learning (Baddeley & Wilson, au socle du projet ; Evans et al., *Neuropsychological Rehabilitation* 10(1), 2000)** — pour un déficit mnésique, ré-encoder une erreur la renforce : il faut **guider jusqu'à la réussite**. Ces méthodes ont leur « plus grand avantage là où la personne ne peut pas corriger elle-même ses erreurs » (Ptak et al., revue sur les troubles de la mémoire épisodique).

**Conséquence clinique retenue** : l'échelle du jour est la bonne pour l'**espacement**. Mais la littérature d'errorless learning demande, elle, qu'une **erreur ne reste pas sans reprise rapprochée** — d'où un point restant, ci-dessous.

## Conséquences

- (+) Une séance ne ressert plus la même série : le contenu vu aujourd'hui revient quand il doit revenir, pas dix minutes plus tard.
- (+) Le rythme du logiciel et le rythme de la mémoire s'accordent : les intervalles se comptent en jours, comme les séances.
- (+) Les données existantes se réparent d'elles-mêmes : les cartes portent encore leurs anciennes échéances (toutes passées) ; elles seront servies une dernière fois, puis reprogrammées à l'échelle du jour.
- (−) Après une séance, une deuxième séance du même thème dans la même journée peut n'avoir **rien à proposer** : l'interface l'annonce calmement (« Rien à réviser pour l'instant — ta prochaine séance arrive au bon moment »). C'est le comportement voulu, mais il doit rester expliqué à l'écran.
- (+) Une erreur ne reste pas sans reprise : elle revient dans la même séance, réponse fournie, ce que demande l'errorless learning — sans retomber dans la répétition en boucle, puisqu'elle revient **une seule fois** et qu'elle est **plafonnée**.
- (−) La **fréquence** des séances (5-10 min, jusqu'à 3 par jour) n'a pas été instruite par ces recherches : elle reste le cadre propre du projet (`docs/10-clinique/protocoles.md`), pas une donnée de la littérature retrouvée ici.
