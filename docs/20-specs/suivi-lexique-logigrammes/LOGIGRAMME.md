# Logigramme — contrat et reprise

2026-10-22. Propriété exclusive domaine `logigramme.py`, générateur, nouveaux JSON logigrammes, test dédié, ce document. Aucun fichier partagé modifié.

Contrat avant implémentation : thème `logigrammes`, type `logigramme`. `contenu.categories` contient objets `{id,label,valeurs}` ; première catégorie ordonnée fixe les lignes. `contraintes` contient `{type:association|exclusion|avant,gauche:{categorie,valeur},droite:{categorie,valeur},texte}` ; avant signifie strictement plus tôt sur les lignes horaires. Toutes règles de bijection sont dans la consigne. `reponse.associations` = `{horaire:{categorie:valeur}}` (et `reponse.valeur` JSON sérialisé), toutes lignes et catégories non horaires exactement. `corriger_logigramme(item,reponse)` retourne bool ; absence, surplus, doublon ou mauvaise association refusés. JSON réponse fourni par UI sérialisé autorisé.

UI attendue : tableau associations réversible, indices toujours accessibles, aide de méthode qui ne révèle rien, pas de préremplissage. Tableau = compensation externe assumée, aucun transfert général promis. Correction/résultats/journalisation existants réutilisés par intégration.

Preuve : propagation par supports binaires et contrainte globale all-different par catégorie ; arrêt seulement si chaque domaine est singleton. Vérification indépendante nombre de solutions plafonné à deux. Aucun branchement pour la preuve de résolution. Corpus original adulte : 4 situations par palier, 3 entités/3 catégories, 4 entités/3 catégories, 4 entités/4 catégories.

Checkpoint initial : AGENTS.md et REPRISE.md lus ; conventions items déduction inspectées. Prochaine commande : création domaine/générateur/tests puis pytest ciblé. Aucun blocage.

Prompt reprise : lire ce fichier, ne toucher que fichiers exclusifs, générer corpus et prouver propagation + unicité, envoyer contrat intégration.

## Checkpoint implémenté — 22 octobre 2026

Fichiers : `backend/app/domain/logigramme.py` (correcteur exact, propagation, compteur indépendant), `tools/generer_logigrammes.py`, 3 nouveaux fichiers `content/entrainement/logigrammes/paliers/palier-01.json` à `palier-03.json`, `backend/tests/test_logigrammes.py` et ce document. Aucun commit ; fichiers partagés laissés à l’agent intégration.

Corpus : 12 items originaux, atelier partagé / archives / association / préparation exposition. Première version trop répétitive remplacée AVANT service : contraintes croisées tirées et minimisées de façon déterministe. Chaque palier présente plusieurs signatures topologiques indépendantes des noms. Comparaisons uniquement entre catégories différentes, jamais une chaîne totale de personnes donnée dans l'énoncé. Tous les indices finaux sont utiles : en retirer un empêche la propagation complète. Toutes grilles comportent association, exclusion et comparaison utiles.

Contrat final : `contenu.categories` première catégorie `horaire` fixe les lignes ; autres IDs `personne`, `dossier`, et P3 `support`. `contenu.contraintes` = indices logiques affichés en permanence ; `contenu.indices` = aides de méthode graduées `{niveau,texte}`. `reponse.associations` = grille complète, `reponse.valeur` = JSON, `reponse.preuve_deductive` = preuve privée. Cette preuve ne doit jamais rejoindre le contenu public de séance. `corriger_logigramme(item,reponse)` accepte dict ou JSON, et refuse omissions, suppléments, doublons et associations fausses. Domaines références `(categorie,valeur)` = ensemble d’horaires possibles ; chaque trace indique avant/après et règle. Les permutations de supports ne portent que sur une catégorie all-different ; aucune hypothèse globale pour résoudre. Compteur indépendant parcourt les permutations globales, plafond deux.

Validation : `python3 tools/generer_logigrammes.py` -> 3×4 items avec assertions propagation et unicité ; `python3 -m pytest -q backend/tests/test_logigrammes.py` -> **40 passed**, 2 avertissements dépendances Starlette. Tests : corpus reproductible, 12 unicités, 12 preuves identiques au corpus, trace monotone, tailles paliers, 12 corrections complètes, omissions/surplus/mauvais liens/doublons, ambiguïté non résolue, contradiction refusée, diversité structurelle, chaque indice utile. Test hors périmètre à laisser au parent. Aucun blocage propre au domaine.

Reprise : ne pas régénérer du contenu déjà servi sous les mêmes IDs ; pour cette branche avant première intégration seulement, corpus révisé en place. Agent intégration informé du contrat. Prochain travail : intégration catalogue/schéma/API/UI, vérification réponse privée retirée, essai fonctionnel (responsable parent/intégration), puis revue générale et commit explicite contenu.
