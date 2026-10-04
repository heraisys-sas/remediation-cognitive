"""Détection de fatigabilité cognitive (garde-fou clinique).

Délègue à `engine.fatigue` (source unique des seuils et de la décision).
Ce module n'existe que pour préserver la couche `domain` et son contrat
d'interface ; il n'y a **plus de duplication** de logique.
"""

from __future__ import annotations

from engine.fatigue import alerter_fatigue  # noqa: F401  (ré-export)

__all__ = ["alerter_fatigue"]
