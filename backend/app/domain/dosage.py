"""Dosage des séances (garde-fou clinique).

Règles issues de docs/10-clinique/protocoles.md :
- séance courte 5–10 min ;
- limite de sessions/jour paramétrable ;
- cap de difficulté configurable avec justification pédagogique explicite
  (anti sur-sollicitation post-commotionnelle).
"""


def verifier_droit_de_session(nb_sessions_du_jour: int, limite: int) -> bool:
    """True si l'utilisateur peut encore démarrer une séance aujourd'hui."""
    return nb_sessions_du_jour < limite


def appliquer_cap_difficulte(palier_demande: int, cap_actif: int) -> int:
    """Ne jamais dépasser le cap de difficulté actif."""
    return min(palier_demande, cap_actif)
