from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path




from backend.app.domain.catalog import THEMES

RACINE_DEPOT = Path(__file__).resolve().parents[2]

DOSSIER_CONTENU = RACINE_DEPOT / "content"

FICHIER_SCHEMA = DOSSIER_CONTENU / "schema-item.json"

MOTIF_REF_PALIER = re.compile(r"^[a-z]+-palier-\d+$")

TYPES_A_CHOIX = {
    "reconnaissance",
    "rappel-source",
    "etape-suivante",
    "par-ou-commencer",
    "si-alors",
    "meilleure-solution",
    "pqrst",
    "but-etapes",
    "auto-instruction",
    "plan-a-verifier",
    "reperer-info",
    "aide-externe",
    "gestion-du-temps",
}

TYPES_A_INDICES = {"rappel-indice"}

MODES_AFFICHAGE = {"sequence", "liste", "series", "texte"}

TYPES_INDICE = {"semantique", "phonologique", "orthographique", "contextuel"}

def _normaliser_texte(valeur: str) -> str:
    import unicodedata

    decompose = unicodedata.normalize("NFD", valeur.casefold())
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    return "".join(sans_accents.split())

def charger_regles() -> dict:
    with FICHIER_SCHEMA.open(encoding="utf-8") as flux:
        schema = json.load(flux)
    proprietes = schema.get("properties", {})
    meta = proprietes.get("meta", {}).get("properties", {})
    relecture = meta.get("relecture_ortho", {}).get("properties", {})
    return {
        "champs_requis": set(schema.get("required", [])),
        "champs_connus": set(proprietes.keys()),
        "enum_module": set(proprietes.get("module", {}).get("enum", [])),
        "enum_type": set(proprietes.get("type", {}).get("enum", [])),
        "enum_fonctions": set(
            proprietes.get("fonctions_ciblees", {}).get("items", {}).get("enum", [])
        ),
        "motif_id": re.compile(proprietes.get("id", {}).get("pattern", r"^[a-z0-9-]+$")),
        "champs_meta": set(meta.keys()),
        "champs_relecture": set(relecture.keys()),
        "enum_statut_relecture": set(relecture.get("statut", {}).get("enum", [])),
    }

def est_entier(valeur: object) -> bool:
    return isinstance(valeur, int) and not isinstance(valeur, bool)

def est_date_iso(valeur: object) -> bool:
    if not isinstance(valeur, str):
        return False
    try:
        date.fromisoformat(valeur)
    except ValueError:
        return False
    return True

THEMES_CONNUS = frozenset(THEMES)

TYPES_JOUR = {"seance", "legere", "repos"}
