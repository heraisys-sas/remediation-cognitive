# ADR-045 — Quatre pratiques guidées de mémoire immédiate

9 octobre 2026 — décision de mise en œuvre V1.

## Contexte

L’utilisateur a retenu Retenir un code, Refaire le chemin, Qu’est-ce qui a changé ? et Quel objet était où ?. Leurs paramètres indépendants et résultats descriptifs ne correspondent pas aux séances adaptatives historiques. Les données et contenus déjà servis doivent rester inchangés.

## Décision

API locale `/api/memoires-immediates`, séparée de FSRS et du moteur adaptatif. Pratique guidée seule en V1 : quatre essais, lancement volontaire, aide après verrouillage de la première réponse ; pas de mode d’observation supplémentaire. Stimuli originaux générés par graine UUID et version `memoires-immediates-v1` ; géométries et palette fixes versionnées. Un bloc de changement contient deux identiques et deux différents dans un ordre mélangé ; toutes positions et paires sont tirables. Réserve des objets tirée indépendamment du modèle. Les essais interrompus sont sans correction et remplacés par un nouveau stimulus lié, au même rang.

La correction est calculée sur le serveur. Réponses premières et assistées sont conservées séparément ; durées et modalités déclarées par le navigateur ne deviennent pas des mesures validées. Aucun score global, empan normé, adaptation automatique ni taux d’observance. Trois blocs ouverts par jour par défaut ; dérogation explicite `sans_limite_sessions`, booléen strict. La fermeture est explicite, y compris après le quatrième essai.

Chaque bloc est un fichier UUID dans `backend/data/memoires-immediates`, hors dépôt. Écriture temporaire, synchronisation et remplacement atomique ; validation avant écriture ; accès sérialisés dans le processus. Les retry réseau identiques d’une réponse retrouvent la correction et le successeur existants ; une autre réponse ne peut écraser la première. Le modèle nécessaire à l’encodage est transmis au navigateur : son masquage DOM/accessibilité est une responsabilité de l’interface, aucune protection contre une inspection technique n’est revendiquée.

## Conséquences

Les trois exercices protégés, leurs historiques et le moteur restent intacts. Les résultats de ces pratiques ne sont pas comparés avec les anciens essais. Pas de synchronisation multi-processus ou distante en V1. Les valeurs par défaut sont des propositions de conception ; relecture clinique et essai d’usage restent nécessaires. Les exemples facultatifs s’exécutent hors résultats du bloc déjà ouvert et ne créent ni essai enregistré ni bloc supplémentaire. Le quota porte sur les blocs commencés. Une aide interrompue est tracée sans score, puis le prochain essai initial est proposé.
