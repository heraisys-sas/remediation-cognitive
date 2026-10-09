# ADR-042 — Distinguer entraînement et autoévaluation dans les spécifications cognitives

9 octobre 2026 — décision documentaire issue des précisions de l’utilisateur ; aucune modification du moteur, de l’API ou des données.

## Contexte

Le référentiel cognitif, la revue des exercices existants et la recherche de candidats précisent désormais ce que chaque tâche fait réellement pratiquer ou observer. L’utilisateur conserve Déduction, Calcul mental et Retrouver le mot, retient quatre mémoires immédiates et demande les nouvelles spécifications. Il précise que les formats d’observation peuvent être implémentés dans « Exercices ciblés », rubrique d’autoévaluation. Les nouveaux candidats recherchés ne sont pas tous sélectionnés.

ADR-038 et sa spécification restent utiles pour les contrats de couleurs, de corrections entrelacées et de figures. Leur ancien emplacement « Prototypes », leur séparation absolue de la pratique et leur ordre de lots ne doivent pas devenir des contraintes contradictoires avec la décision récente.

## Décision

Le [cadre des exercices cognitifs](../../20-specs/cadre-exercices-cognitifs.md) devient la source commune des usages, du confort, des statuts et de la comparabilité. Il est complété par les [corrections existantes](../../20-specs/corrections-exercices-existants.md), les [quatre mémoires retenues](../../20-specs/memoires-immediates.md) et les [candidats à arbitrer](../../20-specs/candidats-cognitifs.md).

L’entraînement décrit une compétence ou une stratégie effectivement pratiquée. L’autoévaluation décrit sa performance dans une configuration stable, sans diagnostic ni standardisation présumée. Un double usage impose protocoles et résultats séparés. L’absence de preuve clinique d’une adaptation n’interdit pas de pratiquer une compétence ; elle interdit d’en présenter l’efficacité comme établie.

Les corrections de fidélité et les quatre principes de mémoire sont documentés sans déclarer leur implémentation. Les autres candidats restent des propositions, même lorsqu’une priorité de discussion leur est attribuée. Les paramètres nouveaux sont des défauts de conception à arbitrer, pas un dosage clinique. Aucune suppression d’exercice ou d’historique, aucune réactivation du bilan standardisé ou de l’IRT historique.

Le [tableau d’articulation du cadre](../../20-specs/cadre-exercices-cognitifs.md#9-articulation-avec-les-spécifications-antérieures) indique précisément quelles sections des prototypes restent opérationnelles. Ce document antérieur est conservé tant qu’il porte des contrats non remplacés. Le cadre et les nouvelles fiches prévalent pour le classement et les exigences explicitement révisées. La proposition PQRST conserve ses décisions de contenu ; son séquençage et son interprétation relèvent désormais d’EX-REV-001.

## Conséquences

Les spécifications sont relisibles par l’orthophoniste, le chercheur, la conception et le développement sans confondre sources, décisions et logiciel courant. Les comparaisons restent descriptives et conditionnelles ; aucun score global de capacités, percentile ou observance n’est ajouté. Les résultats d’usage ne sont pas une validation clinique.

Chaque implémentation future devra préciser son contrat de persistance/API et ses vérifications, en conservant la traçabilité des anciens protocoles. Les données minimales proposées ne sont pas déclarées déjà enregistrées. Les anciennes formulations de projet excluant toute tâche évaluative ne s’appliquent pas comme veto à l’autoévaluation récemment autorisée par l’utilisateur.
