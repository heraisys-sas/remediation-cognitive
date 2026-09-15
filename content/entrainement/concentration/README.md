# Module Concentration (Entraînement — hors MDR)

**Principe** : une attention qui tient — calcul sériel à total courant, filtrage en double tâche, séries à règle. La **fatigue progressive est conçue dans le contenu** : la longueur des chaînes (3 → 7 opérations) et la densité des suites croissent par palier, et la détection de fatigue existante (RT médian + erreurs) fait le reste. Logique des tâches de calcul sériel (famille PASAT) et du filtrage (famille d2) assimilée — protocoles **non copiés** : support visuel, rythme libre, opérations variables.

## Familles

- **Calcul chaîné** : additions/soustractions bout à bout, évaluées de gauche à droite ; le total courant doit être maintenu en mémoire de travail, sans rien poser. Bornes : résultat intermédiaire ≥ 0 et ≤ 300, cap 7 opérations.
- **Cascade de soustractions** : départ − pas répété cinq fois (pas 3–9) — automatisation de la soustraction sous charge.
- **Double tâche de filtrage** : suite mêlant lettres et chiffres (1 s par élément, affichage temporisé), puis « somme des chiffres » ou « nombre de lettres » — attention divisée et sélective.
- **Séries à règle** : terme manquant d'une suite arithmétique, géométrique ou alternée — mémoire de travail et vitesse.

## Structure

- `paliers.json` — manifest des 9 paliers (id, description, prerequis, nb_items)
- `paliers/palier-01..09.json` — 18 items par palier, soit **162 items**

## Réponses attendues

- numériques pour toutes les familles (tolérance numérique du contrat : « 43,0 » vaut 43).

## Génération

Contenu produit par `tools/generer_memo_concentration.py` (déterministe, graine 20260904). Toute retouche manuelle d'un item doit mettre à jour `meta.relecture_ortho`.

## Moteur

Identique aux autres thèmes : paliers (90 % × 3 séances), FSRS, détection de fatigue, garde-fou de séance (600 s, affichage temporisé inclus).
