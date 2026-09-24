# 2026-09-24 — Retrait du thème « vie sociale », missions renommées

## La demande

« Enlève l'entraînement vie sociale, il est trop simple. Laisse les missions hors écran en renommant la section pour qu'elle soit plus explicite sur les raisons de ces missions. »

## Ce qui a été fait

- **Thème d'entraînement « vie sociale » supprimé** : 4 paliers, 40 items (vignettes d'émotion, réponses adaptées, lecture d'intention). Motif : trop simple à l'usage, et il faisait doublon avec les missions.
- **Missions conservées et explicitées** : la section devient **« Missions dans la vraie vie »**. L'intitulé et le texte d'introduction disent maintenant *pourquoi* elles existent — ce n'est pas l'exercice à l'écran qui rétablit le lien, c'est l'action réelle. Un README dédié (`content/missions/README.md`) développe les raisons : érosion des automatismes sociaux, anticipation négative, exposition progressive et répétée comme facteur actif.
- **Réorganisation** : les missions quittent `content/entrainement/social/` pour `content/missions/` ; le périmètre annexe `/api/social` devient `/api/missions` (le nom « social » n'avait plus de sens une fois le thème retiré).

## Points de vigilance rencontrés

- **Le programme de 8 semaines proposait encore « social »** dans sa rotation : après le retrait, il aurait envoyé l'utilisateur vers un thème inexistant. Corrigé, et j'en ai profité pour intégrer les thèmes actuels (quotidien, méthodes, déduction) et corriger les plafonds de paliers (l'évocation est passée à 7 paliers).
- **Les ADR ne se réécrivent pas** : ADR-004 documentait le périmètre `/api/social`. Je l'ai laissé tel quel et **annoté d'un suivi** daté, plutôt que de falsifier la décision historique.
- Le fichier de test `test_evocation_social_api.py` a été renommé (`test_evocation_missions_api.py`) et purgé de ses tests du thème retiré.

## Contrôles

**811 items / 0 erreur** ; **133 tests** ; garde-fous cliniques sans violation ; programme régénéré sans le thème retiré.

## Reste à faire

- Passage visuel de la section renommée.
- Relecture orthophoniste (dont le README des missions et son argumentaire).
