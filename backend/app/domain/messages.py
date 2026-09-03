"""Séparation stricte des vocabulaires (garde-fou du cahier des charges).

- module bilan : vocabulaire clinique, disclaimers professionnels requis ;
- module rééducation : vocabulaire sobre, familial ;
- module entraînement : vocabulaire neutre, ludique modéré.

Aucune chaîne visible par l'utilisateur ne doit être construite hors de ce module.
"""

VOCABULAIRES = {
    "bilan": {
        "titre_session": "Bilan de suivi",
        "disclaimer": (
            "Ce bilan ne constitue pas un diagnostic. "
            "Partagez l'export avec votre professionnel de santé référent."
        ),
    },
    "reeducation": {
        "titre_session": "Séance de rééducation",
    },
    "entrainement": {
        "titre_session": "Session d'entraînement",
    },
}


def texte(cle_module: str, cle_message: str) -> str:
    """Retourne un texte du vocabulaire du module — erreur si le module inconnu."""
    return VOCABULAIRES[cle_module][cle_message]
