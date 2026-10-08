#!/usr/bin/env python3
"""Point d’entrée compatible du contrôle de contenu."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.validation.common import (
    RACINE_DEPOT, DOSSIER_CONTENU, FICHIER_SCHEMA, MOTIF_REF_PALIER, TYPES_A_CHOIX, TYPES_A_INDICES, MODES_AFFICHAGE, TYPES_INDICE, _normaliser_texte, charger_regles, est_entier, est_date_iso, THEMES_CONNUS, TYPES_JOUR,
)
from tools.validation.calculation import (
    MOTIF_ID_CALCUL, MOTIF_CALCUL_ARITHMETIQUE, MOTIF_COMPLEMENT, MOTIF_TOTAL_ARTICLES, MOTIF_RENDU, MOTIF_SUITE_CONTINUE, MOTIF_SUITE_ERREUR, MOTIF_FAIT_INVERSE_GAUCHE, MOTIF_FAIT_INVERSE_DROITE, MOTIF_CHAINE, _reponse_calculee, erreurs_coherence_calcul, couverture_calcul,
)
from tools.validation.items import (
    erreurs_item, erreurs_contenu, erreurs_meta, erreurs_regularite,
)
from tools.validation.deduction import (
    TYPES_INDICE_GRILLE, _cellule_grille, _predicat_grille, _sens_riche_contredit, _sens_contredit, _erreurs_grille_deduction,
)
from tools.validation.recall import (
    erreurs_sequence_pqrst, erreurs_rappel_libre,
)
from tools.validation.manifests import (
    erreurs_manifest,
)
from tools.validation.programme import (
    erreurs_programme, erreurs_missions,
)
from tools.validation.runner import (
    main,
)

if __name__ == "__main__":
    raise SystemExit(main())

__all__ = ['Path', 'RACINE_DEPOT', 'DOSSIER_CONTENU', 'FICHIER_SCHEMA', 'MOTIF_REF_PALIER', 'TYPES_A_CHOIX', 'TYPES_A_INDICES', 'MODES_AFFICHAGE', 'TYPES_INDICE', '_normaliser_texte', 'charger_regles', 'est_entier', 'est_date_iso', 'THEMES_CONNUS', 'TYPES_JOUR', 'MOTIF_ID_CALCUL', 'MOTIF_CALCUL_ARITHMETIQUE', 'MOTIF_COMPLEMENT', 'MOTIF_TOTAL_ARTICLES', 'MOTIF_RENDU', 'MOTIF_SUITE_CONTINUE', 'MOTIF_SUITE_ERREUR', 'MOTIF_FAIT_INVERSE_GAUCHE', 'MOTIF_FAIT_INVERSE_DROITE', 'MOTIF_CHAINE', '_reponse_calculee', 'erreurs_coherence_calcul', 'couverture_calcul', 'erreurs_item', 'erreurs_contenu', 'erreurs_meta', 'erreurs_regularite', 'TYPES_INDICE_GRILLE', '_cellule_grille', '_predicat_grille', '_sens_riche_contredit', '_sens_contredit', '_erreurs_grille_deduction', 'erreurs_sequence_pqrst', 'erreurs_rappel_libre', 'erreurs_manifest', 'erreurs_programme', 'erreurs_missions', 'main']
