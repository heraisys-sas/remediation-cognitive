"""Couche de capacités du poste — façade (P1-B4).

Depuis P1-B4, la logique est répartie en modules à responsabilité unique :
- `domain.similarity` : similarité de textes (fournisseurs Apple/lexical) ;
- `domain.tts` : synthèse vocale sécurisée (issue #2) ;
- `domain.probe` : état des capacités, pour l'interface et le diagnostic.

Ce module reste la **porte d'entrée historique** : il ré-exporte l'API
publique pour ne casser aucun import existant. Préférer les imports directs
dans le code nouveau.

Le logiciel reste **local** : aucune capacité ne sort de la machine.
"""

from __future__ import annotations

from .probe import capacites
from .similarity import (
    SEUIL_SIMILARITE,
    fournisseur_similarite,
    proche,
    similarite,
)
from .tts import synthese

__all__ = [
    "SEUIL_SIMILARITE",
    "capacites",
    "fournisseur_similarite",
    "proche",
    "similarite",
    "synthese",
]
