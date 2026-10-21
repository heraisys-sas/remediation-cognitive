# Déploiement local et frontière d’infrastructure

Orthogone fonctionne actuellement sans authentification applicative, pour une
seule personne par instance. Démarrage recommandé :

```sh
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8766
```

`::1` convient également pour une écoute locale IPv6. Éviter `0.0.0.0` et `::`
sur un poste accessible par d’autres machines. L’application avertit au démarrage
de cette contrainte, quelle que soit la commande de lancement. Cet avertissement
ne détecte pas l’adresse réelle d’écoute, ne bloque pas Uvicorn et ne constitue
pas un contrôle d’accès. Le lancement direct par Uvicorn reste possible.

## Données effectivement conservées

Les résultats d’entraînement, états de progression et répétition espacée sont
persistés côté serveur dans `backend/data/entrainement`. Les blocs de mémoires
immédiates ont leur répertoire séparé. Le carnet des missions peut contenir des
notes personnelles ; il est séparé des séances. Le programme conserve son état
local dans un autre répertoire. Les réglages du navigateur ne remplacent pas ces
stockages. Ne pas versionner les données réelles ; sauvegarder les répertoires
hors du dépôt avec des droits d’accès restreints et vérifier la restauration.

Aucune API de bilan n’est exposée par ce service : aucune donnée de bilan ne doit
y transiter. Voir [ADR-002](adr/ADR-002-separation-stockages.md) pour la séparation
des périmètres. Cette distinction ne rend pas les notes et résultats anonymes
ni insensibles lorsqu’ils peuvent être rattachés à une personne.

## Exposition déléguée à l’infrastructure

La gestion des utilisateurs n’est pas ajoutée à Orthogone. Une passerelle ou des
microservices peuvent porter TLS, authentification, autorisation, limitation des
requêtes et journalisation sans corps de réponses ni secrets. Ce sont des
responsabilités de déploiement, pas des fonctionnalités déjà livrées ici.

- Le backend ne doit être accessible que par la passerelle : réseau privé,
  socket ou filtrage réseau ; aucun chemin public ne doit contourner celle-ci.
- Protéger toutes les routes, y compris `/ui`, `/api`, `/docs` et `/openapi.json`.
  Une sonde de santé peut être réservée au réseau d’exploitation.
- Conserver une instance et un stockage isolés par personne. Une authentification
  devant une instance partagée n’isole pas ses historiques : Orthogone n’utilise
  pas une identité de requête pour sélectionner ses données.
- Restreindre les origines, contrôler les requêtes qui modifient des données et
  traiter la protection CSRF si la passerelle utilise des cookies. CORS seul
  n’est pas une protection d’accès.
- Vérifier avant exposition : accès anonyme refusé, accès direct impossible,
  isolation effective entre instances, restauration des sauvegardes et absence
  de données personnelles dans les journaux.

Les services locaux Apple (voix et similarité) s’exécutent sur l’hôte serveur :
les déplacer dans une infrastructure distante change leur disponibilité et le
chemin des données ; ce déplacement n’est pas implicite.

Le transfert de progression, Cloudflare KV et l’envoi de synthèses par courriel
restent hors de cette livraison. Aucun service distant supplémentaire ni compte
utilisateur n’est créé.
