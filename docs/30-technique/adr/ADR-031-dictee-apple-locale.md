# ADR-031 — Dictée locale par SpeechAnalyzer

## Contexte
Le navigateur ne propose pas toujours la reconnaissance française hors ligne.
L'application doit rester locale, sans repli réseau, avec du texte modifiable.

## Décision
Un adaptateur Swift utilise SpeechTranscriber/SpeechAnalyzer (macOS 26+) sur un
WAV borné capté dans le navigateur. Deux routes `/api/capacites/dictee` exposent
l'état local et la transcription. Les ressources Apple doivent être déjà
installées ; aucune installation automatique. Aucun contexte de réponse attendue
n'est injecté. L'analyse sémantique métier reste postérieure à la transcription.

## Conséquences
Compilation locale requise, disponibilité explicite sur les postes compatibles.
Les autres postes conservent la saisie clavier ou une reconnaissance navigateur
uniquement si celle-ci garantit le traitement sur appareil. Les enregistrements
restent temporaires ; le serveur ne capte jamais lui-même le microphone.
