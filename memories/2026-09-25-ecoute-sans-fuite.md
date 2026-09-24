# 2026-09-25 — « Écouter » : fuite d'indice corrigée, ergonomie de la mémorisation

## Le bug

« Écouter la consigne » donnait la réponse **avant** l'affichage du texte à retenir (signalé sur « au quotidien »). Cause : le bouton lisait `consigne + enonce` — et `enonce` **est la question**, connue du client dès le départ. Pendant la phase de mémorisation, la question était donc prononcée à voix haute.

Le formulaire, lui, était bien masqué pendant la mémorisation : le défaut ne venait que de l'audio.

## Le correctif

Le bouton lit **ce qui est affiché**, suivi d'un état `etat.enonceCourant` :

- **phase de mémorisation** → la consigne seule ;
- **phase de question** → la consigne **et** la question ;
- jamais la question avant son affichage — donc jamais d'indice soufflé.

## Ergonomie (la demande de fond)

- Le **stimulus se lit automatiquement** au clic sur « Afficher » : texte (PQRST), liste de paires, fiche à retenir — « on écoute ce qu'on lit ».
- Les **séquences** (empans, double tâche) restent **visuelles** : leur rythme (0,8–1 s par élément) est trop précis pour être doublé par une voix dont la latence varie.
- Libellé simplifié : « 🔊 Écouter », avec une infobulle qui précise ce qu'il lit.

## Leçon

Un bouton qui lit « tout le contenu de l'item » casse la logique pédagogique de l'exercice : l'audio doit suivre **l'état d'avancement** de l'écran, exactement comme le texte. Toute capacité ajoutée doit être testée **contre les phases**, pas seulement contre le contenu.

## Contrôles

811 items / 0 erreur ; 140 tests.

## Suite (même jour) — ne pas répéter la consigne

Retour d'usage : la consigne de méthode répétée à chaque question est rébarbative.

- **Audio** : on ne lit plus que la **question** (la consigne reste lisible pendant la mémorisation, et accessible via le tableau de bord « Méthode — avant de répondre »).
- **Écrit** : la consigne de méthode n'est **affichée qu'une fois par type d'exercice dans la séance** (un ensemble `etat.consignesVues` suit les types déjà vus ; remis à zéro à chaque séance). Ensuite, une phrase courte du style « Mémorise le contenu affiché. » suffit.

Leçon : dans un entraînement répétitif, **la pédagogie doit décroître** — la première occurrence enseigne, les suivantes entraînent. Répéter une méthode à chaque item la transforme en bruit.

## Suite (même jour) — lecture automatique par défaut

- **Activée par défaut** : la consigne (mémorisation), le stimulus (à l'affichage) et la question se disent d'eux-mêmes.
- **Case « Lecture automatique »** à côté du bouton « Écouter », en haut de la zone d'exercice : la décocher coupe la lecture immédiatement, la recocher la rétablit ; le réglage est conservé dans `localStorage` (clé `remediation.lectureAuto`).
- Le bouton « Écouter » reste **indépendant** du réglage (lecture à la demande, pour relire).
- Le stimulus devient « ce qui est affiché » pendant son affichage : le bouton « Écouter » le relit donc à la demande, même si l'automatique est coupé.

Leçon : un défaut automatisé doit rester **réversible en un geste** et **persistant**, sinon l'utilisateur subit le réglage au lieu de le piloter.

## Suite (même jour) — dictée affichée au fur et à mesure

Demande : voir la réponse orale se former à l'écran.

- `capacites.js` demande maintenant les **résultats provisoires** (`interimResults = true`) et expose `onPartiel(texte)` (pendant la parole) en plus de `onResultat(texte)` (phrase définitive).
- `app.js` écrit la transcription **dans le champ de réponse** au fil de l'eau, en conservant ce qui était déjà saisi, et signale l'écoute par un liseré sur le champ.
- Effet : la personne voit ce qui a été compris **avant** de valider, et peut corriger au clavier.

Rappel consigné : selon le navigateur, la reconnaissance est **sur l'appareil** (Safari) ou **distante** (Chrome → serveurs Google). Pour de la voix sensible, préférer le mode « sur l'appareil ».
