# Rejouer un palier — 2026-10-08

Ajout dans les réglages dérogatoires sous le bypass de limite. Case masquée/désactivée hors mode ; préférence orthogone.rejouerPalier conservée, effet neutralisé hors mode. Le démarrage demande rejouer_palier uniquement lorsque mode et case sont actifs.

API additive bool false (ADR-036), service réutilise inclure_non_dus dans sélection. Correction du chemin à étapes qui retournait trop tôt pour accepter ce complément ; ordre normal identique sans bypass. Quota, parcours, palier, limite de séances et persistance historique habituels conservés. Aucun changement moteur/contenu.

Validation : 49 tests backend, dont 3 nouveaux tests rejeu ; JS syntaxe et verifier_interface ; Chrome persistence/rechargement et corps réseau mode on/off. Travail local, aucun push/commit ; modifications antérieures préservées.

Placement corrigé à la demande : case de rejeu au-dessus de la limite, chacune sur une ligne distincte (display flex sur les labels du groupe ; inline-flex les plaçait côte à côte sur grand écran). Cache CSS actualisé.

Diagnostic du blocage réel : les dix cartes mémoire-source ne sont pas dues (sélection normale vide, sélection dérogatoire dix items). Serveur PID11797 lancé sans reload avant la modification, OpenAPI ne contenait pas rejouer_palier et ignorait donc le champ. Redémarré le serveur du bon checkout avec uvicorn --reload ; vérifié OpenAPI rejouer_palier et JS servi qui le transmet. Aucune carte ni historique supprimé, aucune séance utilisateur créée pour le contrôle.
