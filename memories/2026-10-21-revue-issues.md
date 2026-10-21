# Actualité des issues — 21 octobre 2026

Vérification GitHub des trois issues ouvertes, des PR et du code origin/dev
44acda5 (SHA distant vérifié). Les développements cognitifs du checkout
deduction-corrections restent locaux ; ne pas les présenter comme livrés.

- #6 : toujours pertinente et prioritaire. Le seuil commun 0,78 subsiste.
  Reproduction réelle du repli lexical : « Paul appelle Marie pour confirmer le
  rendez-vous » / « Marie appelle Paul pour confirmer le rendez-vous » donnent
  0,8667 et le correcteur accepte l’inversion. Cas synthétique, pas une réponse
  utilisateur ni une mesure Apple. Les tests existants vérifient notamment les
  contrats par mocks, pas une calibration réelle complète. Garder corpus,
  séparation réglage/contrôle et mesure par fournisseur ; ne pas promettre
  qu’un changement de seuil suffira à traiter l’ordre des rôles.
- #7 : pertinente, à préciser selon la décision utilisateur. Pas de comptes,
  profils ni authentification dans Orthogone ; contrôle d’accès éventuellement
  délégué à une passerelle/microservices. Une instance et un stockage partagés
  ne sont pas isolés par une authentification externe seule. Corriger la phrase
  de l’issue : aucune API de bilan n’est exposée ; les résultats et notes restent
  potentiellement personnels. Documentation et avertissement de démarrage
  préparés sur fix/deploiement-local, test ciblé réussi ; pas encore livrés.
- #25 : pertinente comme suivi d’intégration, pas comme développement à refaire.
  PR #27 ouverte, tests et interface-mobile verts. Recette automatisée mobile
  distincte d’un test sur appareil physique et avec lecteur d’écran. Choix
  éditorial actuel : difficultés ressenties, sans diagnostic ni gravité.
- #8 : close par décision utilisateur. PR #26 de retrait du graphe encore ouverte,
  ancien échec CI associé à la facturation ; ne pas rouvrir export ou graphe.

Le transfert de progression est mis de côté. Les cinq séances par semaine sont
une hypothèse de dimensionnement, pas une autorisation d’imposer un nouveau
plafond global. Aucun changement distant d’issue, fusion, compte ni service
Cloudflare à l’occasion de cette revue.
