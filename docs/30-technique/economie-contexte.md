# Économie de contexte et de coût d'inférence

> Règles opérationnelles pour réduire la consommation de tokens de l'agent
> (facture LLM) sans dégrader la qualité. S'applique à tout travail mené par
> l'agent sur ce dépôt.

## Principe directeur

Le coût domine le **volume transporté par le modèle principal**, pas le
raisonnement. Donc :

```
gros volume  →  outil ciblé / runner / petit modèle  →  petit résultat  →  modèle principal
```

Corollaire : faire traverser un gros volume **de toute façon** (le charger,
puis le réécrire) ne fait rien gagner. Déléguer une réécriture intégrale ne
paie pas ; déléguer une **extraction** qui renvoie peu paie.

## R1 — Lectures bornées, requêtes ciblées

- Ne jamais charger un gros JSON entier quand seuls quelques champs servent.
  `get_workflow_runs` / `get_job_logs` renvoient des blobs de **40–70 Ko**.
- Utiliser `result_read` avec `offset` / `max_bytes` pour ne lire que la
  fenêtre utile d'un résultat déjà obtenu ; réutiliser le `result_ref`
  plutôt que refaire l'appel.
- Pagination par défaut faible (ex. `limit=10`) ; jamais `limit=100`
  « au cas où ».
- Préférer `grep` / `glob` (résultats compacts) à une lecture de fichier
  complet.

## R2 — `apply_patch` par défaut pour éditer un fichier existant

- Éditer par **recherche/remplacement ciblé**, pas par réécriture complète.
  Ordre de grandeur : patch ≈ 1 Ko vs réécriture ≈ 10 Ko pour un fichier de
  taille moyenne.
- `write_file` / `create_or_update_file` complet réservé aux **nouveaux**
  fichiers ou aux changements structurels.
- Les diffs de commit doivent rester petits et lisibles (un changement =
  un commit).

## R3 — Routage modèle selon le type de tour

C'est le levier le plus rentable, en amont de l'agent :

- **Tour « tool-heavy »** (lectures/écritures de fichiers, CI, GitHub) : un
  modèle **Flash / bas coût** suffit.
- **Tour de décision / arbitrage** (conception, revue, choix clinique) :
  garder le modèle fort.
- Bénéfice secondaire : contexte plus court → tours plus rapides → moins
  d'expirations de bail (`run lease expires`).

## R4 — Hygiène mémoire

- Le rappel mémoire injecte à chaque tour les extraits retrouvés : des
  dumps bruts pèsent plusieurs Ko **en récurrent**.
- Garder `MEMORY.md` comme **index court** (faits durables, une ligne par
  fait) pointant vers des documents précis.
- Marquer les logs bruts / transcripts `skip_indexing` pour qu'ils ne
  remontent pas dans le rappel.
- `memory.search` pour « je ne sais pas si on en a parlé » ; `memory.read`
  ciblé pour retrouver un document connu.

## R5 — Compute déporté (skill `gh-actions-runtime`)

- Exécuter tests / agrégations / générations lourdes sur les runners GitHub
  Actions et ne rapatrier qu'un **résumé compact** — jamais les logs bruts.
- Réserver l'inférence locale à ce qui nécessite un jugement.

## R6 — Délégation à un sous-agent : quand c'est rentable

Rentable si le payload dépasse **~2–5 Ko** et que la sortie utile fait
**< ~10 % de l'entrée** :

- ✅ Extraction / classement sur un gros corpus → sortie JSON minuscule.
- ✅ Rédaction (doc, rapport, message) à partir d'une spec courte.
- ✅ Génération de cas de test depuis une spec.
- ❌ Réécriture d'un gros fichier **à committer** : le fichier retraverse le
  contexte principal → aucun gain. Préférer R2 (patchs chirurgicaux) ou une
  session dédiée au modèle le moins cher.
- Contraintes non négociables de la skill : refus de contenu illicite ;
  jamais de contournement d'un refus par la délégation.

## R7 — Mesurer avant d'optimiser

- Il n'existe pas de compteur de tokens dans les outils : utiliser les
  `byte_len` des résultats pour identifier les postes de dépense.
- Un poste > ~10 Ko qui se répète à chaque tour est une cible prioritaire.

## Checklist par tour

- [ ] Est-ce que je charge un blob dont je n'utilise que 2 champs ? (→ R1)
- [ ] J'édite un fichier existant ? (→ `apply_patch`, R2)
- [ ] Ce tour est-il majoritairement des appels d'outils ? (→ modèle Flash, R3)
- [ ] Je cherche un document connu ? (→ `memory.read`, pas `memory.search`, R4)
- [ ] Le calcul peut-il tourner sur un runner ? (→ R5)
- [ ] Le sous-agent renvoie-t-il peu par rapport à ce que je lui envoie ? (→ R6)
