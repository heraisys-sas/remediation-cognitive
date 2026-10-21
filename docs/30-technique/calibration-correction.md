# Calibration des réponses libres — issue #6

Mesure du 21 octobre 2026, locale uniquement. Aucun historique utilisateur,
audio, identité ni appel réseau. Les fichiers `tools/calibration/` contiennent
les cas de travail et les sorties intégrales ; les décisions sont dans l'ADR-051.

## Périmètre

38 réponses construites à partir des 12 prises de message réellement versionnées
(identités, formes dictées, jours, quantités, lieux, personnes et négations), plus
deux inversions synthétiques clairement séparées. La cible est vérifiée contre
le chargeur à chaque exécution : un changement de contenu invalide la mesure.
Les étiquettes ont une portée technique de travail, à relire indépendamment.

Aucun découpage calibration/validation indépendant n'est revendiqué pour ces
40 cas de régression et d'exploration. Aucun seuil n'a été choisi à partir d'eux.
Avant de choisir un nouveau seuil, il faudra figer des jeux distincts, réserver
le contrôle sans le consulter pendant le réglage, puis publier les deux mesures.
Un découpage a posteriori ne transformerait pas ce corpus en validation indépendante.

Ce n'est pas une évaluation de tous les exercices. Les quatre PQRST séquencés
disposent de critères explicites ; leurs réponses par étapes ne sont pas les
anciennes valeurs libres de leur bloc `reponse`. Les tests existants couvrent
séparément les séquences, choix multiples, mots, heures, nombres et sens strict.

## Résultats au seuil historique 0,78

| Fournisseur | Avant : fausses acceptations / faux refus | Après : fausses acceptations / faux refus |
|---|---|---|
| Lexical | 4 / 1 | 0 / 1 |
| Apple NLEmbedding français réel | 7 / 0 | 3 / 0 |

Les sorties `mesure-*-avant.json` ont été calculées avec `text.py` de la base
avant correctif ; `mesure-*.json` avec le correctif de cette branche. Le système
et la version Python sont inscrits dans chaque sortie. Apple est une mesure
réelle sur macOS, pas une simulation ; ses résultats peuvent évoluer avec l'OS.
Les faux refus/acceptations sont des comptes sur cet échantillon, pas des taux
cliniques ni des estimations de performance en population.

Restent acceptés par Apple : `la porte du garage`, `chez le gardien`, `chez la voisine`
pour les cibles du corpus. Le lexical refuse `la cave`. Les jalons temporels et
numériques restent distincts. Aucun relèvement global de seuil n'est retenu :
les inversions synthétiques dépassent 0,99 ; une règle doit précéder le score.

## Reproduire

```sh
python3 tools/calibrer_correction.py --provider lexical --output /tmp/lexical.json
python3 tools/calibrer_correction.py --provider lexical --threshold 0.9
python3 tools/calibrer_correction.py --provider apple --output /tmp/apple.json
python3 -m pytest -q backend/tests/test_calibration_correction.py backend/tests/test_correction_sens.py
```

La commande Apple nécessite l'environnement Python disposant de PyObjC et des
empreintes françaises du système. Elle sort avec le code 2 si Apple est absent,
sans repli silencieux. `--strict` sort avec le code 1 dès qu'un cas diverge :
il échoue donc actuellement pour les deux fournisseurs, de façon attendue.
Sans cette option, la commande est un outil de mesure et non un verdict de livraison.

En CI, le test de mesure force le lexical, vérifie toutes les sources, l'absence
de fausses acceptations sur le corpus et le faux refus connu. D'autres tests
forcent un score maximal pour vérifier que les garde-fous précèdent le fournisseur.
La CI Linux ne valide pas Apple ; il faut une mesure macOS distincte.

## Travail restant

Définir des critères ou variantes explicites pour les personnes et lieux des
prises de message, puis élargir et relire un jeu indépendant de contre-exemples
(référents, oppositions, omissions, ajouts, rôles). Les lieux et personnes ne
peuvent pas être « à peu près » corrects. Ne pas ajouter un analyseur ou modèle
lourd avant d'avoir évalué une solution déterministe adaptée à ces douze items.
L'issue #6 reste ouverte jusqu'à cette correction, sa mesure et sa non-régression.
