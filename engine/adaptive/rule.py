"""Règle adaptative v1 : ajustement ±1 palier selon le taux de réussite glissant.

Interface prête pour une migration IRT (Phase 4 de la feuille de route,
quand les données utilisateur le permettront).
"""


def ajuster_palier(
    palier_actuel: int,
    taux_reussite_glissant: float,
    seuil_bas: float = 0.6,
    seuil_haut: float = 0.9,
) -> int:
    """Ajuste le palier : +1 si fluide, -1 si en difficulté, stable sinon."""
    if taux_reussite_glissant >= seuil_haut:
        return palier_actuel + 1
    if taux_reussite_glissant < seuil_bas:
        return max(1, palier_actuel - 1)
    return palier_actuel
