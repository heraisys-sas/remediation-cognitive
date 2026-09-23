# 2026-09-23 — Renforcer le versant clinique (garde-fous, cadre, repères)

## Demande

« Améliore le clinique » — en réponse à mon propre constat de la veille : l'ingénierie est en avance sur la clinique, et la valeur restante est du côté de la validation et de l'usage, pas d'un énième thème.

## Ce que j'ai fait (et ce que je ne peux pas faire)

Trois choses sont en mon pouvoir ; la validation elle-même n'en est pas. Je l'ai dit explicitement.

1. **Garde-fous cliniques transformés en contrôle automatique** — `tools/verifier_clinique.py` : vocabulaire non médical sans terme clinique/normatif, thème sombre sans animation, aucun instrument protégé dans le contenu, relecture tracée et « valide » daté. Le principe : un garde-fou qui n'est pas vérifié par une machine se dégrade sans bruit.
2. **Cadre d'usage écrit** — `docs/10-clinique/cadre-usage.md` : limites du logiciel (hors dispositif médical), précautions par famille, signes d'alerte, statuts de relecture.
3. **Repères d'orientation dans l'application** — un bouton discret sur l'accueil menant à quatre situations génériques qui invitent à en parler à un professionnel (jamais un diagnostic).

## Choix de conception

- Le contrôle clinique scanne le **contenu des items**, pas la documentation : citer « PASAT » dans un README pour dire « on n'a pas copié » est légitime ; le retrouver dans un énoncé ne l'est pas.
- Le scan de vocabulaire exclut le module **bilan**, dont le disclaimer contient à juste titre le mot « diagnostic ».
- Les repères d'orientation sont volontairement **statiques et non cliniques** : « parlez-en », jamais « vous avez ».
- Les repères vivent dans le HTML statique (comme le reste de la copie d'interface), pas dans `messages.py` — cohérent avec la pratique existante.

## Vérifications

- `verifier_clinique.py` : aucune violation (vocabulaire OK, photophobie OK, matériel protégé absent, 691 items `a_revoir`).
- 4 tests verrouillent désormais les outils (validateur, réponses, interface, clinique) → **118 tests**.

## Reste à faire (ce que je ne peux pas faire seul)

- La **relecture orthophoniste** des 691 items : le contrôle garantit que les garde-fous tiennent, pas que le contenu est cliniquement juste.
- Un **premier usage réel** : c'est lui qui dira si le produit tient.
- Les paramètres moteur (90 % × 3, 600 s, 12 items, 3 séances/jour) restent des défauts raisonnables, pas des valeurs calibrées.
