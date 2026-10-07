# Dictée Apple sur le Mac serveur

Prérequis : macOS 26+, Xcode/Swift, matériel pris en charge par SpeechTranscriber,
ressources françaises déjà installées. Le navigateur capte seulement le micro ;
il transmet un WAV PCM16 mono au serveur **du même Mac**. Le texte revient dans
le champ éditable avant la correction habituelle. Aucune réponse attendue n'est
fournie à la reconnaissance.

```sh
sh tools/installer_dictee_apple.sh
.local/bin/dictee-apple --status
```

L'adaptateur est compilé dans `.local/bin/` (ignoré par Git). Aucun modèle tiers,
aucun appel cloud et aucun téléchargement automatique. Si le français n'est pas
installé, l'état renvoie `francais_non_installe` ; il faut préparer les ressources
Apple du système avant de retester. Ne pas remplacer silencieusement par un
service distant. Un terminal sandboxé peut ne pas voir les ressources pourtant
installées ; le serveur lancé normalement doit être utilisé pour le diagnostic.

API : `GET /api/capacites/dictee` renvoie la disponibilité ; `POST` sur la même
route reçoit `{ "audio_base64": "..." }` et renvoie
`{ "disponible": true, "texte": "...", "fournisseur": "apple_speech_local" }`.
WAV non compressé, 16 bits, mono, 8–48 kHz, 60 secondes et 3 Mo maximum.
Audio invalide : HTTP 422 ; moteur indisponible : HTTP 503. Le fichier temporaire
est supprimé au retour ou à l'erreur. Aucun audio n'est conservé dans les données.
Le processus est arrêté après 60 secondes au plus. Relancer le serveur après
installation du code backend, puis recharger la page.

Vérification réelle du 7 octobre 2026 : français installé, phrase synthétique
Audrey « Jeudi soir, nous attendons devant la gare. » transcrite exactement,
hors ponctuation finale. Aucun micro utilisateur capté. Cela vérifie le circuit,
pas la précision clinique ni la qualité sur la voix réelle de l'utilisateur.

## Affichage pendant la parole

La capture propose un aperçu toutes les 600 ms lorsqu’aucune transcription n’est en cours. Chaque appel reprend l’audio cumulé : le nouveau texte remplace l’aperçu précédent et peut réviser un mot selon le contexte. Il s’agit de requêtes cumulatives bornées, pas du streaming natif Apple. Une seule requête en vol, arrêt après 55 s et appel final si de nouveaux échantillons restent à traiter. Délai moteur : 20 s ; délai réseau local : 25 s. Une sortie vide devient une erreur explicite. Mesures sur audios synthétiques courts : 118–232 ms, pas une garantie de latence au micro ni sur 55 s.
