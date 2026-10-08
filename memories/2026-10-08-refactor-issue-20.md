# Refactorisation — issue #20

Registre technique des thèmes centralisé, correction et validation modularisées,
I/O des générateurs commune, contrôleur vanilla séparé des comportements d'exercices.
État de séance réinitialisable, génération d'annulation préservée ; service déchargé
des détails de correction et de la finalisation pure de progression. Ruff léger ajouté.

Aucun fichier de contenu actif modifié. 15 copies/scripts historiques supprimés sous
`.cluster`, rapports et mesures gardés, historique récupérable au commit `160367c`.
Voir ADR-037 pour les limites et l'ajout API des propriétés d'interface.

Pièges vérifiés : l'extracteur JS doit ignorer les objets par défaut des signatures ;
le contrôle de POST seul pouvait manquer une erreur après réception de la séance.
Les tests lisent désormais les scripts effectivement servis et contrôlent l'installation
réelle de la séance. Ne pas réinitialiser le compteur de génération des minuteries.
