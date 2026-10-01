"""Persistance JSON de l'entraînement — données non médicales (ADR-002).

Fichiers sous ``backend/data/entrainement/<theme>/`` (hors dépôt : le
.gitignore du projet exclut ``data/``) :
- ``cartes-fsrs.json``      : état FSRS par item (``CarteFSRS.to_dict`` /
  ``from_dict`` de engine.srs.fsrs, utilisé tel quel) ;
- ``maitrise.json``         : palier courant + historique chronologique
  des couples (palier, taux de réussite) — critère 90 % × 3 séances ;
- ``compteur-seances.json`` : compteur de séances de la fenêtre courante —
  jour, ou semaine (lundi) pour l'évaluation — remis à zéro au changement
  de fenêtre.

Les répertoires sont créés à la volée à l'écriture ; les lectures sur
fichiers absents retournent des valeurs par défaut (thème vierge :
palier 1, aucun historique, aucune carte, 0 séance).

Les séances en cours restent en mémoire (registre backend) et ne sont
persistées qu'à la fin — seuls les états ci-dessus sont écrits.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

from engine.srs.fsrs import CarteFSRS

RACINE_PROJET = Path(__file__).resolve().parents[3]
"""Racine du dépôt remediation-cognitive (résolution indépendante du CWD)."""

_MOTIF_THEME = re.compile(r"^[a-z0-9-]+$")


class StockageJSON:
    """Accès fichiers JSON par thème ; racine injectable (tests).

    Périmètre strictement « entraînement » : aucune donnée de bilan ne
    transite ici (séparation ADR-002).
    """

    def __init__(self, racine: Path | None = None) -> None:
        self.racine = (
            Path(racine)
            if racine is not None
            else RACINE_PROJET / "backend" / "data" / "entrainement"
        )

    # -- primitives ----------------------------------------------------------

    def _dossier_theme(self, theme: str) -> Path:
        """Dossier du thème, avec garde contre toute injection de chemin."""
        if not _MOTIF_THEME.match(theme or ""):
            raise ValueError(f"theme invalide : {theme!r}")
        return self.racine / theme

    def _lire_json(self, chemin: Path) -> dict | None:
        """Lit un fichier JSON ; None s'il n'existe pas encore."""
        try:
            return json.loads(chemin.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None

    def _ecrire_json(self, chemin: Path, contenu: dict) -> None:
        """Écriture atomique (temporaire + rename) ; crée le répertoire à la volée."""
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire = chemin.with_suffix(chemin.suffix + ".tmp")
        temporaire.write_text(
            json.dumps(contenu, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        os.replace(temporaire, chemin)

    # -- cartes FSRS ---------------------------------------------------------

    def lire_cartes(self, theme: str) -> dict[str, CarteFSRS]:
        """Cartes FSRS persistées du thème (dictionnaire vide si thème vierge)."""
        donnees = self._lire_json(self._dossier_theme(theme) / "cartes-fsrs.json") or {}
        cartes: dict[str, CarteFSRS] = {}
        for item_id, etat in (donnees.get("cartes") or {}).items():
            cartes[item_id] = CarteFSRS.from_dict(etat)
        return cartes

    def ecrire_cartes(self, theme: str, cartes: dict[str, CarteFSRS]) -> None:
        """Persiste le deck complet du thème (sérialisation engine, non modifiée)."""
        contenu = {
            "cartes": {
                item_id: carte.to_dict()
                for item_id, carte in sorted(cartes.items())
            }
        }
        self._ecrire_json(self._dossier_theme(theme) / "cartes-fsrs.json", contenu)

    # -- maîtrise par palier ---------------------------------------------------

    def lire_maitrise(self, theme: str) -> dict:
        """État de maîtrise : palier courant + historique [(palier, taux), …]."""
        donnees = self._lire_json(self._dossier_theme(theme) / "maitrise.json") or {}
        palier_courant = int(donnees.get("palier_courant") or 1)
        historique = [
            (int(palier), float(taux))
            for palier, taux in (donnees.get("historique") or [])
        ]
        etat = {"palier_courant": palier_courant, "historique": historique}
        if "historique_etapes" in donnees:
            etat["historique_etapes"] = [(int(p), float(t)) for p, t in donnees["historique_etapes"]]
        return etat

    def maitrise_existe(self, theme: str) -> bool:
        """True si une progression a déjà été persistée pour ce thème/parcours."""
        return (self._dossier_theme(theme) / "maitrise.json").is_file()

    def ecrire_maitrise(
        self, theme: str, palier_courant: int, historique: list[tuple[int, float]],
        historique_etapes: list[tuple[int, float]] | None = None,
    ) -> None:
        """Persiste le palier courant et l'historique chronologique."""
        contenu = {
            "palier_courant": int(palier_courant),
            "historique": [[palier, taux] for palier, taux in historique],
        }
        if historique_etapes is not None:
            contenu["historique_etapes"] = [[p, t] for p, t in historique_etapes]
        self._ecrire_json(self._dossier_theme(theme) / "maitrise.json", contenu)

    # -- compteur de séances (fenêtre courante) ---------------------------------

    def lire_compteur(self, theme: str, debut: date) -> int:
        """Séances démarrées dans la fenêtre ouverte à ``debut`` (0 sinon)."""
        donnees = (
            self._lire_json(self._dossier_theme(theme) / "compteur-seances.json")
            or {}
        )
        if donnees.get("date") != debut.isoformat():
            return 0
        return int(donnees.get("nb_sessions") or 0)

    def ecrire_compteur(self, theme: str, debut: date, nb_sessions: int) -> None:
        """Persiste le compteur de la fenêtre (le début stocké pilote la remise à zéro)."""
        contenu = {
            "date": debut.isoformat(),
            "nb_sessions": int(nb_sessions),
        }
        self._ecrire_json(
            self._dossier_theme(theme) / "compteur-seances.json", contenu
        )

    # -- baseline RT (temps de référence) ---------------------------------------

    def lire_temps_reference(self, theme: str) -> list[float]:
        """Derniers temps de réaction corrects (ms), vide si thème vierge."""
        donnees = (
            self._lire_json(self._dossier_theme(theme) / "temps-reference.json")
            or {}
        )
        return [float(t) for t in (donnees.get("temps") or [])]

    def ecrire_temps_reference(self, theme: str, temps: list[float]) -> None:
        """Persiste les ≤ 100 derniers temps corrects (médiane → baseline RT)."""
        contenu = {"temps": [float(t) for t in temps[-100:]]}
        self._ecrire_json(
            self._dossier_theme(theme) / "temps-reference.json", contenu
        )
