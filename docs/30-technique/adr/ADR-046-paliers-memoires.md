# ADR-046 — Paliers de pratique des mémoires immédiates

10 octobre 2026 — accepté dans le lot local. Remplace la limitation de difficulté fixe d’ADR-045 pour les nouveaux blocs demandant `progression: true`.

La charge puis le délai évoluent selon les configurations décrites dans [la spécification](../../20-specs/paliers-memoires-immediates.md). Les règles de passage sont des choix de produit, sans norme clinique ni catégorie HPI.

L’état dérive des journaux atomiques terminés, séparés par parcours/modalité/condition. Deux blocs admissibles à trois réponses exactes sur quatre augmentent le palier ; deux à une ou moins le diminuent. Chaque bloc garde ses paramètres. Les clôtures immuables sont traitées par date de fin ; la révision change après chaque transition. Un bloc ouvert sous une révision ancienne reste conservé mais ne modifie pas la nouvelle progression. Les retries de fin ne dupliquent pas la clôture.

Les aides, interruptions et blocs incomplets ne participent pas. Les paramètres numériques dérogatoires sont des configurations libres séparées. FSRS et les journaux historiques ne sont pas modifiés. Protocole des nouveaux stimuli v2 ; réponses des anciennes séances restent corrigées sur leur stimulus enregistré et résultats annoncés sous leur version stockée. Chaque essai nouvellement généré porte aussi sa version : une ancienne séance poursuivie après mise à jour peut contenir des essais v1 et v2 sans réétiquetage des anciens.

Tests de montée/descente, clôtures désordonnées, révisions anciennes, modalités séparées, tous les paliers et conditions ; recette six objets à 320 px. Validation technique uniquement.
