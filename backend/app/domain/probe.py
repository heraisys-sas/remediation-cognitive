"""Sonde d'état des capacités du poste (P1-B4).

Responsabilité unique : rapporter, pour l'interface et le diagnostic, ce
que ce poste sait faire et par quel moyen — sans logique métier.

Les capacités effectives vivent ailleurs :
- similarité -> `domain.similarity` ;
- synthèse   -> `domain.tts` ;
- voix       -> côté client (navigateur ou OS de la tablette).
"""

from __future__ import annotations

import platform

from .similarity import SEUIL_SIMILARITE, fournisseur_similarite
from .tts import synthese_disponible


def capacites() -> dict:
    """Ce que ce poste sait faire, et par quel moyen — pour l'interface et le diagnostic."""
    return {
        "similarite": {
            "disponible": True,
            "fournisseur": fournisseur_similarite(),
            "seuil": SEUIL_SIMILARITE,
        },
        "synthese": {"disponible": synthese_disponible(), "moyen": "voix du système"},
        "voix": {
            "disponible": None,
            "moyen": "client (navigateur ou OS de la tablette)",
        },
        "plateforme": platform.system(),
        "principe": "local — aucune donnée ne quitte le poste",
    }
