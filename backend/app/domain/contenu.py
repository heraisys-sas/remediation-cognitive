"""Accès au contenu d'entraînement versionné sous content/ (données, pas code).

Le backend lit content/ tel quel : tout item est déjà conforme à
``content/schema-item.json``. Les chemins sont résolus depuis
l'emplacement de ce fichier, indépendamment du CWD.

Le registre ci-dessous mappe les identifiants de thème de l'API vers
les sources du dépôt ; les libellés visibles (nom/description) viennent
du vocabulaire centralisé (``domain.messages``), pas d'ici.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import messages

RACINE_PROJET = Path(__file__).resolve().parents[3]
"""Racine du dépôt remediation-cognitive (résolution indépendante du CWD)."""

_BASE_ENTRAINEMENT = Path("content/entrainement")

# Thème API → (sous-dossier de content/entrainement, motif de fichiers).
_SOURCES_PAR_THEME: dict[str, tuple[str, str]] = {
    "calcul-mental": ("calcul-mental/paliers", "palier-*.json"),
    "anglais": ("anglais", "verbes-irreguliers.json"),
    "python": ("python/commandes", "builtins.json"),
}


class ChargeurContenu:
    """Charge et met en cache les items d'entraînement par thème.

    Le contenu est versionné et figé pendant l'exécution : une lecture
    unique par thème suffit (cache mémoire de l'instance).
    """

    def __init__(self) -> None:
        self._cache_items: dict[str, list[dict]] = {}

    # -- thèmes ------------------------------------------------------------

    def themes(self) -> list[dict]:
        """Métadonnées des thèmes exposés par l'API (contrat GET /themes)."""
        libelles = messages.VOCABULAIRES["entrainement"]["themes"]
        return [
            {"id": theme_id, **libelles[theme_id]}
            for theme_id in _SOURCES_PAR_THEME
            if theme_id in libelles
        ]

    def theme_existe(self, theme: str) -> bool:
        """True si le thème fait partie du registre de l'API."""
        return theme in _SOURCES_PAR_THEME

    # -- items -------------------------------------------------------------

    def items(self, theme: str) -> list[dict]:
        """Items complets du thème (avec ``reponse`` — usage serveur uniquement)."""
        if theme not in self._cache_items:
            self._cache_items[theme] = self._charger(theme)
        return self._cache_items[theme]

    def item(self, theme: str, item_id: str) -> dict | None:
        """Item complet par identifiant, ou None s'il est inconnu du thème."""
        for item in self.items(theme):
            if item["id"] == item_id:
                return item
        return None

    def paliers(self, theme: str) -> list[int]:
        """Paliers disponibles pour le thème, triés (1, 2, …)."""
        return sorted({int(item["palier"]) for item in self.items(theme)})

    # -- interne -----------------------------------------------------------

    def _charger(self, theme: str) -> list[dict]:
        """Lit les fichiers de contenu du thème (ordre de glob trié = stable)."""
        if theme not in _SOURCES_PAR_THEME:
            return []
        sous_dossier, motif = _SOURCES_PAR_THEME[theme]
        dossier = RACINE_PROJET / _BASE_ENTRAINEMENT / sous_dossier
        items: list[dict] = []
        for fichier in sorted(dossier.glob(motif)):
            donnees = json.loads(fichier.read_text(encoding="utf-8"))
            if isinstance(donnees, list):
                items.extend(donnees)
        return items
