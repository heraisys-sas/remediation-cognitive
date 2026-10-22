# Commandes audio compactes — 23 octobre 2026

Branche feat/calcul-commandes-audio, checkout /Users/olivierhz/orthogone/calcul-commandes-audio, base origin/dev 0ed9207. Demande : icônes Écouter/Dicter, micro à droite du champ ; harmonisation autorisée dans autres exercices. Skill ui-ux-pro-max appliquée.

Interface seule : haut-parleur CSS/SVG, wrapper relatif du champ et micro 44 px ; textes accessibles conservés et statut visible (préparation, parole, transcription, erreurs), réinitialisé entre questions. États automatiques d’Évocation préservés. Versions ressources incrémentées ; aucune modification du moteur vocal ni des contenus/données. Tests Playwright simulent les capacités/micro, ne valident pas la reconnaissance sur matériel.

Reprise : vérifier status/PR/CI de cette branche. Tests navigateur 4/4 Chromium bureau/mobile, WebKit mobile/320 px. Suite Python finale : 531 réussis, 1 ignoré ; rapport dans /private/tmp/audio-tests-final.txt ; commande PATH='/Applications/AutoClaw.app/Contents/Resources/node/darwin-arm64':$PATH python3 -m pytest -q. Validateur interface OK. Node existant AutoClaw utilisé seulement comme exécutable, aucun agent AutoClaw lancé. node_modules de test lié temporairement puis supprimé avant commit.
