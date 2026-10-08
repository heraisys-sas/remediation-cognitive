# ADR-038 — Spécifier les prototypes cognitifs séparément de la remédiation

## Contexte

L’utilisateur a demandé la formalisation des idées de correction différée, figures et couleurs, ajoutées à la feuille de route au commit acf74b5. La TODO mélangeait modes, métriques et paramètres sans contrat d’exécution. Il autorise son remplacement par une spécification meilleure.

## Décision

La source de travail devient [la spécification des prototypes](../../20-specs/prototypes-epreuves-cognitives.md). La feuille de route conserve uniquement un lien et le statut de développement.

Les prototypes restent locaux et séparés de la remédiation. Familiarisation et mesure personnelle sont des modes des prototypes, sans diagnostic ou standardisation présumée. Le bilan standardisé historique et l’IRT ne sont pas réactivés.

Les paramètres dérogatoires sont persistants mais masqués en mode normal, sans bandeau. Les départs sont volontaires et les épreuves interrompables. Les comptes vocaux ambigus nécessitent vérification ; l’incertitude de reconnaissance n’est pas une erreur de réponse. Un essai interrompu n’est pas assimilé à un essai complet.

## Conséquences

Développement par lots indépendants avec données versionnées et stockage séparé. Aucun changement d’API ou moteur réalisé par cette décision documentaire. Le contrat d’implémentation devra être documenté avec ses tests lors de sa réalisation. Les durées et tailles demandées sont des paramètres de prototype, pas des normes.

Une spécification future peut remplacer celle-ci ; supprimer alors les liens et documents devenus concurrents, avec conservation de l’historique Git.
