# 1er octobre 2026 — parcours et attention

Demande utilisateur : fusionner l’état actuel dans main, puis coder les propositions approuvées. Fusion rapide ab17659 → 8a75404 publiée dans main après 253 tests réussis, 1 ignoré. Développement sur exercices-attention-series.

ADR-022 : catégories honnêtes, deux parcours de séries, trois nouvelles tâches fonctionnelles. 32 items rs-* remplacés par rs2-* (rythme 2 + 2), 32 listes auditives rse1-*, 36 situations nouvelles. Anciens calculs Concentration accessibles sous Calcul mental sans modifier leurs IDs ni historiques. Aucun profilage diagnostique, reprise effectivement interrompue reportée.

Essai navigateur isolé 8766 avec données temporaires : actualisation masque bien les messages ; documents consultables, réponse et fin de séance vérifiées. Le retour fonctionnel était créé mais restait caché : corrigé et couvert par test. Web Speech dans le navigateur intégré n’appelait pas onend : remplacé pour les stimuli par fichiers Thomas AAC préparés, 48 mots/329297 octets ; passage réel au rappel vérifié sans erreur console. Voix des consignes inchangée.

Les simulations et leurs seuils ne sont pas validés cliniquement. La lecture humaine du contenu et l’écoute des fichiers restent utiles. Ne pas mélanger les progressions auditives/visuelles. Le serveur et l’autre checkout de l’utilisateur n’ont pas été modifiés.

Validation finale : 266 tests réussis, 1 ignoré ; 1020 items / 0 erreur ; cohérence interface, syntaxe JS, 839 phrases de déduction ; régénération identique des cinq parcours nouveaux/modifiés.
