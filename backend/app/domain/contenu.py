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
from copy import deepcopy
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
    "memoire": ("memoire/paliers", "palier-*.json"),
    "rappel-series": ("rappel-series/paliers", "palier-*.json"),
    "series-entendues": ("series-entendues/paliers", "palier-*.json"),
    "actualiser-consigne": ("actualiser-consigne/paliers", "palier-*.json"),
    "comparer-documents": ("comparer-documents/paliers", "palier-*.json"),
    "reperer-essentiel": ("reperer-essentiel/paliers", "palier-*.json"),

    "quotidien": ("quotidien/paliers", "palier-*.json"),
    "deduction": ("deduction/paliers", "palier-*.json"),
    "methodes": ("methodes/paliers", "palier-*.json"),
    "garder-cap": ("garder-cap/paliers", "palier-*.json"),
    "evocation": ("evocation/paliers", "palier-*.json"),
}

# Parcours homogènes exposés à l'intérieur d'une même carte. Chaque parcours
# possède son propre état de maîtrise ; ``sources`` remappe les anciens paliers
# composites vers une progression locale 1..N, sans réécrire le contenu livré.
_PARCOURS_PAR_THEME: dict[str, list[dict]] = {
    "memoire": [
        {"id": "chiffres-endroit", "nom": "Chiffres dans l’ordre",
         "description": "Empans de 3 à 6 chiffres ; départ automatique à 5 chiffres",
         "sources": [1, 2, 3, 4], "types": ["empan"], "enonce_contient": "dans l'ordre",
         "palier_depart": 3},
        {"id": "chiffres-envers", "nom": "Chiffres en ordre inverse",
         "description": "Manipuler mentalement 3 à 6 chiffres, sans passer par les empans endroit",
         "sources": [4, 5, 6, 7], "types": ["empan"], "enonce_contient": "à l'envers",
         "palier_depart": 1},
        {"id": "mots", "nom": "Mots — ordre et ordre inverse",
         "description": "Empans de mots concrets ; départ automatique à 4 mots",
         "sources": [9, 10, 11, 12], "types": ["empan-mots"], "palier_depart": 2},
        {"id": "associations", "nom": "Associations mot–nombre",
         "description": "Mémoriser puis retrouver une association ; départ automatique à 3 paires",
         "sources": [3, 6, 8], "types": ["paires-associatives"], "palier_depart": 2},
        {"id": "position", "nom": "Position dans une séquence",
         "description": "Retrouver l’élément situé 2, 3 puis 4 positions avant la fin",
         "sources": [5, 7, 8], "types": ["n-back"]},
    ],
    "rappel-series": [
        {"id": "immediat", "nom": "Rappel immédiat",
         "description": "Une à trois séries ; départ automatique à deux séries de trois mots",
         "sources": [1, 2, 3], "palier_depart": 2},
        {"id": "differe", "nom": "Rappel différé",
         "description": "Toutes les séries après une attente de 20 secondes", "sources": [4],
         "portee": "toutes-series"},
        {"id": "premiere-serie", "nom": "Sélectionner la première série",
         "description": "Après le délai, rappeler seulement la première série", "sources": [4],
         "portee": "premiere-serie"},
    ],
    "series-entendues": [
        {"id": "immediat", "nom": "Rappel immédiat",
         "description": "Une à trois séries entendues ; départ automatique à deux séries",
         "sources": [1, 2, 3], "palier_depart": 2},
        {"id": "differe", "nom": "Rappel différé",
         "description": "Toutes les séries entendues après 20 secondes", "sources": [4],
         "portee": "toutes-series"},
        {"id": "premiere-serie", "nom": "Sélectionner la première série",
         "description": "Après le délai, rappeler seulement la première série entendue", "sources": [4],
         "portee": "premiere-serie"},
    ],
    "methodes": [
        {"id": "pqrst-guide", "nom": "PQRST guidé pas à pas", "sources": [6]},
        {"id": "pqrst-rappel", "nom": "PQRST — répondre de mémoire", "sources": [1]},
        {"id": "choisir-plan", "nom": "Choisir un plan", "sources": [2]},
        {"id": "auto-instruction", "nom": "Se guider avant d’agir", "sources": [3]},
        {"id": "verifier-plan", "nom": "Vérifier un plan", "sources": [4]},
        {"id": "chercher-information", "nom": "Chercher dans un document", "sources": [5]},
    ],
    "garder-cap": [
        {"id": "reprendre", "nom": "Reprendre après une interruption", "sources": [1]},
        {"id": "adapter", "nom": "Adapter un plan", "sources": [2]},
        {"id": "verifier", "nom": "Vérifier avant de terminer", "sources": [3]},
    ],
    "evocation": [
        {"id": "acces-lexical", "nom": "Retrouver le mot",
         "description": "Mots adultes, indices gradués ; réponse orale ou clavier, QCM de soutien au palier 1",
         "sources": [8, 9, 10, 11, 12, 13], "palier_depart": 2,
         "max_items_paliers": {1: 10, 2: 10, 3: 10, 4: 8, 5: 8, 6: 6},
         "libelles_paliers": {1: "QCM de soutien", 2: "Point de départ · objets familiers · voix ou clavier",
            3: "Mots précis · voix ou clavier", 4: "Notions en contexte · voix ou clavier",
            5: "Verbes utiles · voix ou clavier", 6: "Mots en situation · voix ou clavier"}},
        {"id": "memoire-source", "nom": "Retrouver le contexte",
         "description": "Distinguer l’information de l’endroit où elle a été apprise", "sources": [4],
         "types": ["rappel-source"]},
        {"id": "strategie-semantique", "nom": "Stratégie sémantique (SFA)", "sources": [6]},
        {"id": "strategie-phonologique", "nom": "Stratégie phonologique (PCA)", "sources": [7]},
    ],
}

#: Fichier des missions d'interaction réelle (hors écran, périmètre « missions »).
_FICHIER_MISSIONS = Path("content/missions/missions.json")

#: Présentation : entraînements fonctionnels et exercices ciblés (aucun bilan).
_CATEGORIE_PAR_THEME: dict[str, str] = {
    "calcul-mental": "entrainement",
    "anglais": "entrainement",
    "python": "entrainement",
    "evocation": "entrainement",
    "quotidien": "entrainement",
    "deduction": "entrainement",
    "methodes": "entrainement",
    "garder-cap": "entrainement",
    "memoire": "cible",
    "rappel-series": "cible",
    "series-entendues": "cible",
    "actualiser-consigne": "entrainement",
    "comparer-documents": "entrainement",
    "reperer-essentiel": "entrainement",
}

# Niveau d'entrée automatique d'un thème sans parcours. Les niveaux inférieurs
# restent accessibles par le sélecteur d'essai ; ils servent de socle si la
# calibration montre une difficulté réelle.
_PALIER_DEPART_PAR_THEME: dict[str, int] = {
    "calcul-mental": 5,
}

#: Programme d'entraînement (cadrage du rythme et des paliers).
_FICHIER_PROGRAMME = Path("content/programmes/8-semaines.json")


class ChargeurContenu:
    """Charge et met en cache les items d'entraînement par thème.

    Le contenu est versionné et figé pendant l'exécution : une lecture
    unique par thème suffit (cache mémoire de l'instance).
    """

    def __init__(self) -> None:
        self._cache_items: dict[tuple[str, str | None], list[dict]] = {}
        self._cache_missions: list[dict] | None = None
        self._cache_programme: dict | None = None

    # -- programme d'entraînement ---------------------------------------------

    def programme(self) -> dict:
        """Programme de 8 semaines (contenu de cadrage ; dict vide si absent)."""
        if self._cache_programme is None:
            chemin = RACINE_PROJET / _FICHIER_PROGRAMME
            try:
                donnees = json.loads(chemin.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError):
                donnees = {}
            self._cache_programme = donnees if isinstance(donnees, dict) else {}
        return self._cache_programme

    # -- missions hors écran --------------------------------------------------

    def missions(self) -> list[dict]:
        """Missions d'interaction réelle (hors écran).

        Hors moteur de séance : une mission n'a pas de réponse attendue —
        l'application fournit la préparation et le suivi, pas une note.
        """
        if self._cache_missions is None:
            chemin = RACINE_PROJET / _FICHIER_MISSIONS
            try:
                donnees = json.loads(chemin.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError):
                donnees = {}
            missions = donnees.get("missions") if isinstance(donnees, dict) else None
            self._cache_missions = missions if isinstance(missions, list) else []
        return self._cache_missions

    # -- thèmes ------------------------------------------------------------

    def themes(self) -> list[dict]:
        """Métadonnées des thèmes exposés par l'API (contrat GET /themes).

        Chaque thème porte sa ``categorie`` : « entrainement » (remédiation) ou
        « cible » (exercices ciblés) — l’interface sépare les deux sections.
        """
        libelles = messages.VOCABULAIRES["entrainement"]["themes"]
        return [
            {
                "id": theme_id,
                "categorie": self.categorie(theme_id),
                # Paliers disponibles : sert au sélecteur d'essai de l'interface
                # (« Palier : auto » suit la progression ; un palier forcé ne sert
                # que pour les essais, il ne fait jamais reculer la maîtrise).
                "paliers": self.paliers(theme_id),
                "palier_depart": self.palier_depart(theme_id, None),
                "parcours": self.parcours(theme_id),
                **libelles[theme_id],
            }
            for theme_id in _SOURCES_PAR_THEME
            if theme_id in libelles
        ]

    def categorie(self, theme: str) -> str:
        """Catégorie du thème (« entrainement » par défaut)."""
        return _CATEGORIE_PAR_THEME.get(theme, "entrainement")

    def theme_existe(self, theme: str) -> bool:
        """True si le thème fait partie du registre de l'API."""
        return theme in _SOURCES_PAR_THEME

    def parcours(self, theme: str) -> list[dict]:
        """Parcours indépendants du thème, avec leurs paliers locaux."""
        return [
            {cle: valeur for cle, valeur in definition.items()
             if cle not in {"sources", "types", "types_par_source", "portee", "enonce_contient"}}
            | {"paliers": list(range(1, len(definition["sources"]) + 1))}
            for definition in _PARCOURS_PAR_THEME.get(theme, [])
        ]

    def parcours_existe(self, theme: str, parcours: str | None) -> bool:
        """Le parcours est facultatif ; s'il est fourni il doit être déclaré."""
        return parcours is None or any(
            definition["id"] == parcours for definition in _PARCOURS_PAR_THEME.get(theme, [])
        )

    def max_items_parcours(self, theme: str, parcours: str | None, palier: int) -> int | None:
        definition = next((p for p in _PARCOURS_PAR_THEME.get(theme, []) if p["id"] == parcours), {})
        return definition.get("max_items_paliers", {}).get(palier)

    def palier_depart(self, theme: str, parcours: str | None) -> int:
        """Palier initial d'une progression neuve ; 1 sans saut justifié."""
        definition = next((p for p in _PARCOURS_PAR_THEME.get(theme, [])
                           if p["id"] == parcours), None)
        if definition is not None:
            return int(definition.get("palier_depart", 1))
        return int(_PALIER_DEPART_PAR_THEME.get(theme, 1))

    # -- items -------------------------------------------------------------

    def items(self, theme: str, parcours: str | None = None) -> list[dict]:
        """Items complets du thème (avec ``reponse`` — usage serveur uniquement)."""
        cle = (theme, parcours)
        if cle not in self._cache_items:
            items = self._charger(theme)
            if parcours is not None:
                definition = next((p for p in _PARCOURS_PAR_THEME.get(theme, [])
                                   if p["id"] == parcours), None)
                if definition is None:
                    return []
                rangs = {source: rang for rang, source in enumerate(definition["sources"], 1)}
                types = set(definition.get("types") or [])
                portee = definition.get("portee")
                enonce_contient = definition.get("enonce_contient")
                filtres = []
                for item in items:
                    if item.get("palier") not in rangs:
                        continue
                    if types and item.get("type") not in types:
                        continue
                    types_source = definition.get("types_par_source", {}).get(item["palier"])
                    if types_source and item.get("type") not in types_source:
                        continue
                    if portee and (item.get("contenu") or {}).get("portee") != portee:
                        continue
                    if enonce_contient and enonce_contient not in str(
                        (item.get("contenu") or {}).get("enonce") or ""
                    ):
                        continue
                    copie = deepcopy(item)
                    copie["palier"] = rangs[item["palier"]]
                    filtres.append(copie)
                items = filtres
            self._cache_items[cle] = items
        return self._cache_items[cle]

    def item(self, theme: str, item_id: str, parcours: str | None = None) -> dict | None:
        """Item complet par identifiant, ou None s'il est inconnu du thème."""
        for item in self.items(theme, parcours):
            if item["id"] == item_id:
                return item
        return None

    def paliers(self, theme: str, parcours: str | None = None) -> list[int]:
        """Paliers disponibles pour le thème, triés (1, 2, …)."""
        return sorted({int(item["palier"]) for item in self.items(theme, parcours)})

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
