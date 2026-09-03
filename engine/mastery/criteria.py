"""Critère de maîtrise : pas de passage au palier suivant sans fluidité.

Défaut : 90 % de réussite sur 3 sessions consécutives (paramétrable).
"""


def palier_maitrise(
    taux_par_session: list[float],
    seuil: float = 0.9,
    sessions_consecutives: int = 3,
) -> bool:
    """True si les N dernières sessions consécutives atteignent le seuil."""
    if len(taux_par_session) < sessions_consecutives:
        return False
    return all(t >= seuil for t in taux_par_session[-sessions_consecutives:])
