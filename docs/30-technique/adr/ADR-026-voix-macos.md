# ADR-026 — Voix macOS de qualité non exposées par le navigateur

Date : 2026-10-05

## Contexte

Audrey (Premium) est installée mais absente de la liste Web Speech dans Chrome.

## Décision

GET `/api/capacites/voix` annonce les voix fr_FR Premium/Enhanced installées
(retour `voix: [{id, nom}]`, liste vide hors macOS). POST
`/api/capacites/synthese` accepte un champ facultatif `voix` : s'il est fourni,
il est validé contre cette liste puis transmis à `say` par tableau d'arguments.
Sans ce champ, le fonctionnement historique reste identique. L'audio WAV est
retourné en base64. Le texte vocal conserve les transformations des opérateurs.

## Conséquences

Aucun téléchargement ni service distant. Les changements d'étape invalident les
réponses audio en attente. Une génération nécessite un court délai et ne dispose
pas de cache persistant. L'installation de voix relève de macOS. La liste du
navigateur exclut les voix fantaisie ; le choix explicite reste prioritaire.
