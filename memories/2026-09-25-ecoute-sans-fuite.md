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
