"""Orchestration des séances d'entraînement (couche service du sprint 1).

Sépare la logique métier du mapping HTTP (router.py) :
- démarrer une séance : garde-fou de dosage (3 séances/jour), sélection
  des items (dus FSRS puis nouveaux, max 12), création du
  ``SessionRunner`` (moteur engine/ réutilisé tel quel) ;
- enregistrer une réponse : correction serveur (la réponse attendue ne
  fuit jamais avant soumission), feedback immédiat guidé ;
- terminer la séance : application de FSRS + critère de maîtrise
  (90 % × 3 séances consécutives → palier +1), puis persistance JSON.

Les séances en cours vivent en mémoire (registre) ; seuls les états
cartes / maîtrise / compteur sont persistés, à la fin de la séance.
La fatigue (``SessionRunner.doit_proposer_arret``) n'est qu'une
proposition renvoyée en fin de séance — JAMAIS une interruption.
"""

from __future__ import annotations

import statistics
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from engine.mastery.criteria import palier_maitrise_historique
from engine.session.runner import SessionRunner
from engine.srs.fsrs import CarteFSRS, planifier

from ...domain import messages
from ...domain.contenu import ChargeurContenu
from ...domain.correction import corriger
from ...domain.dosage import (
    DUREE_MAX_SEANCE_S,
    LIMITE_SESSIONS_JOUR,
    MAX_ITEMS_PAR_SEANCE,
)
from ...domain.selection import selectionner_items
from ...storage.store import StockageJSON

# Notes FSRS v1 : réussite → Good (3), échec → Again (1).
NOTE_REUSSITE = 3
NOTE_ECHEC = 1

# Critère de maîtrise (docs/10-clinique/protocoles.md, paramétrable).
SEUIL_MAITRISE = 0.9
SESSIONS_CONSECUTIVES_MAITRISE = 3


def _horloge_utc() -> datetime:
    """Horloge par défaut (injectable pour les tests)."""
    return datetime.now(timezone.utc)


# -- exceptions métier (le router les mappe vers les codes du contrat) ---------


class ThemeInconnu(Exception):
    """Thème absent du registre de l'API."""


class LimiteSessionsAtteinte(Exception):
    """Garde-fou de dosage : quota journalier de séances déjà consommé."""

    def __init__(self, restantes: int = 0) -> None:
        super().__init__(restantes)
        self.restantes = restantes


class SessionInconnue(Exception):
    """Identifiant de séance inconnu (ou thème ne correspondant pas)."""


class SessionDejaTerminee(Exception):
    """La séance a déjà été clôturée (409 du contrat)."""


class ItemHorsSeance(Exception):
    """Item absent de la séance en cours (404 du contrat)."""


class ReponseInvalide(Exception):
    """Réponse ou temps invalide (422)."""


# -- adaptations locales -------------------------------------------------------


class ItemMoteur:
    """Adapte un item de contenu au contrat du moteur (attribut ``item_id``).

    engine.session.runner attend des items exposant ``item_id`` ; le
    contenu versionné utilise la clé ``id``. L'adaptation reste côté
    backend : engine/ n'est pas modifié.
    """

    def __init__(self, item: dict) -> None:
        self.item = item
        self.item_id = item["id"]


@dataclass
class SessionEnCours:
    """État serveur d'une séance démarrée (en mémoire jusqu'à la fin)."""

    session_id: str
    theme: str
    palier: int
    runner: SessionRunner
    items_par_id: dict[str, dict]
    # Départ de la séance (garde-fou de durée, injectable via l'horloge).
    depart: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # Première réponse par item — fait foi pour FSRS ; les essais
    # supplémentaires (reprises errorless) restent comptés par le moteur.
    reponses: dict[str, bool] = field(default_factory=dict)
    # Temps (ms) des premières réponses correctes — baseline RT adaptative.
    temps_reference: list[float] = field(default_factory=list)
    # Indices consultés par item (0 = sans aide) — mesure de l'aide nécessaire.
    indices_utilises: dict[str, int] = field(default_factory=dict)
    # Essais clos en affichant la réponse : aucune erreur commise par
    # l'utilisateur, mais pas de récupération réussie non plus.
    assistees: set[str] = field(default_factory=set)
    terminee: bool = False


def _item_sans_reponse(item: dict) -> dict:
    """Payload client d'un item : id/type/palier/contenu — JAMAIS ``reponse``."""
    return {
        "id": item["id"],
        "type": item["type"],
        "palier": item["palier"],
        "contenu": item["contenu"],
    }


class GestionnaireSessions:
    """Point d'entrée métier : démarrer / répondre / terminer une séance."""

    def __init__(
        self,
        stockage: StockageJSON | None = None,
        contenu: ChargeurContenu | None = None,
        horloge: Callable[[], datetime] | None = None,
    ) -> None:
        self.stockage = stockage or StockageJSON()
        self.contenu = contenu or ChargeurContenu()
        # Horloge injectable (tests) — horloge UTC réelle par défaut.
        self.horloge = horloge or _horloge_utc
        self._sessions: dict[str, SessionEnCours] = {}
        # Sérialise lecture → incrément → écriture du compteur journalier.
        self._verrou_dosage = threading.Lock()

    # -- démarrage -----------------------------------------------------------

    def demarrer(self, theme: str) -> dict:
        """Démarre une séance et retourne le payload 201 du contrat.

        Lève ``ThemeInconnu`` (404) ou ``LimiteSessionsAtteinte`` (429).
        Le compteur du jour est incrémenté dès le démarrage (une séance
        entamée compte dans le dosage, qu'elle aille à son terme ou non).
        """
        if not self.contenu.theme_existe(theme):
            raise ThemeInconnu(theme)
        with self._verrou_dosage:
            maintenant = self.horloge()
            aujourd_hui = maintenant.date()
            nb_sessions = self.stockage.lire_compteur(theme, aujourd_hui)
            if nb_sessions >= LIMITE_SESSIONS_JOUR:
                raise LimiteSessionsAtteinte(
                    restantes=max(0, LIMITE_SESSIONS_JOUR - nb_sessions)
                )
            etat_maitrise = self.stockage.lire_maitrise(theme)
            palier = self._palier_courant(theme, etat_maitrise["palier_courant"])
            cartes = self.stockage.lire_cartes(theme)
            selection = selectionner_items(
                self.contenu.items(theme),
                cartes,
                palier,
                maintenant,
                MAX_ITEMS_PAR_SEANCE,
            )
            runner = SessionRunner(
                items=[ItemMoteur(item) for item in selection],
                max_items=MAX_ITEMS_PAR_SEANCE,
                duree_max_s=DUREE_MAX_SEANCE_S,
                baseline_rt_ms=self._baseline_rt(theme),
                depart=maintenant,
            )
            # Le contrat livre tous les items d'un bloc au démarrage : ils
            # sont donc tous « servis » dès l'ouverture de la séance, et le
            # moteur peut ensuite enregistrer chaque réponse.
            while runner.prochain_item() is not None:
                pass
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = SessionEnCours(
                session_id=session_id,
                theme=theme,
                palier=palier,
                runner=runner,
                items_par_id={item["id"]: item for item in selection},
                depart=maintenant,
            )
            self.stockage.ecrire_compteur(theme, aujourd_hui, nb_sessions + 1)
        return {
            "session_id": session_id,
            "items": [_item_sans_reponse(item) for item in selection],
            "regles": {
                "max_items": MAX_ITEMS_PAR_SEANCE,
                "duree_max_s": DUREE_MAX_SEANCE_S,
            },
        }

    def _palier_courant(self, theme: str, palier_stocke: int) -> int:
        """Palier de travail : celui du stockage, borné au contenu disponible."""
        paliers = self.contenu.paliers(theme)
        if not paliers:
            return max(1, palier_stocke)
        return min(max(1, palier_stocke), paliers[-1])

    def _baseline_rt(self, theme: str) -> float:
        """Baseline RT adaptative : médiane des dernières réponses correctes.

        Revue exécution : une baseline figée à 1000 ms produit de faux
        positifs de fatigue chez les utilisateurs lents. On prend la
        médiane des ≤ 100 derniers temps corrects persistés ; 1000 ms
        tant que l'échantillon est trop petit (moins de 5 réponses).
        """
        temps = self.stockage.lire_temps_reference(theme)
        if len(temps) >= 5:
            return float(statistics.median(temps))
        return 1000.0

    # -- réponses ------------------------------------------------------------

    def repondre(
        self,
        theme: str,
        session_id: str,
        item_id: str,
        reponse,
        temps_ms,
        indice_utilise: int | None = None,
    ) -> dict:
        """Corrige côté serveur et retourne le payload 200 du contrat.

        ``indice_utilise`` (optionnel, 0 par défaut) : nombre d'indices
        consultés par l'utilisateur. La valeur ``nb_indices + 1`` signale que
        la réponse a été AFFICHÉE — l'essai est alors « assisté » : aucune
        erreur n'est commise (principe errorless) mais la récupération n'a pas
        eu lieu, donc la carte FSRS est notée en échec et le taux de réussite
        ne la compte pas comme réussite.

        Lève ``SessionInconnue`` (404), ``SessionDejaTerminee`` (409),
        ``ItemHorsSeance`` (404) ou ``ReponseInvalide`` (422).
        """
        session = self._session(theme, session_id)
        if session.terminee:
            raise SessionDejaTerminee()
        item = session.items_par_id.get(item_id)
        if item is None:
            raise ItemHorsSeance()
        if (self.horloge() - session.depart).total_seconds() >= session.runner.duree_max_s:
            # Garde-fou de dosage (revue conformité) : au-delà de la durée
            # max, la séance est clôturée automatiquement et les réponses
            # suivantes reçoivent 409. Ce n'est PAS une interruption par la
            # fatigue — celle-ci reste une simple proposition.
            self._cloturer(session, self.horloge())
            raise SessionDejaTerminee()
        nb_indices = len((item.get("contenu") or {}).get("indices") or [])
        if indice_utilise is None:
            indice_utilise = 0
        if (
            isinstance(indice_utilise, bool)
            or not isinstance(indice_utilise, int)
            or indice_utilise < 0
            or indice_utilise > nb_indices + 1
        ):
            raise ReponseInvalide("indice_utilise hors bornes")
        assistee = nb_indices > 0 and indice_utilise > nb_indices
        correcte = False if assistee else corriger(theme, item, reponse)
        try:
            session.runner.enregistrer_reponse(item_id, correcte, temps_ms)
        except ValueError as exc:
            raise ReponseInvalide(str(exc)) from exc
        premiere_reponse = item_id not in session.reponses
        session.reponses.setdefault(item_id, correcte)
        if premiere_reponse:
            session.indices_utilises[item_id] = indice_utilise
            if assistee:
                session.assistees.add(item_id)
            elif correcte and indice_utilise == 0:
                # Seules les premières réponses correctes SANS AIDE nourrissent
                # la baseline RT (les essais aidés ou dupliqués la fausseraient).
                session.temps_reference.append(float(temps_ms))
        if assistee:
            cle = "feedback_assiste"
        else:
            cle = "feedback_correcte" if correcte else "feedback_incorrecte"
        return {
            "correcte": correcte,
            "assistee": assistee,
            "attendue": item["reponse"]["valeur"],
            "feedback": messages.texte("entrainement", cle),
        }

    # -- fin de séance ---------------------------------------------------------

    def terminer(self, theme: str, session_id: str) -> dict:
        """Clôture la séance : FSRS + maîtrise + persistance, payload 200 du contrat.

        Lève ``SessionInconnue`` (404) ou ``SessionDejaTerminee`` (409).
        """
        session = self._session(theme, session_id)
        if session.terminee:
            raise SessionDejaTerminee()
        resume_moteur, nb_repondu, nb_correctes, taux = self._cloturer(
            session, self.horloge()
        )
        restantes = max(
            0,
            LIMITE_SESSIONS_JOUR
            - self.stockage.lire_compteur(theme, self.horloge().date()),
        )
        arret_propose = bool(resume_moteur["alerte_fatigue"])
        retour = {
            "resume": {
                "items": nb_repondu,
                "correctes": nb_correctes,
                "duree_s": int(round(resume_moteur["duree_s"])),
                "taux_reussite": taux,
            },
            "arret_propose": arret_propose,
            "motif_arret": "fatigue" if arret_propose else None,
            "sessions_restantes_aujourdhui": restantes,
        }
        # Champs propres aux exercices d'accès au mot : aide réellement
        # nécessaire et essais clos sans erreur (réponse affichée).
        if session.indices_utilises or session.assistees:
            retour["resume"]["assistees"] = len(session.assistees)
            retour["resume"]["sans_aide"] = sum(
                1
                for item_id, correcte in session.reponses.items()
                if correcte and session.indices_utilises.get(item_id, 0) == 0
            )
        return retour

    def _cloturer(
        self, session: SessionEnCours, maintenant: datetime
    ) -> tuple[dict, int, int, float]:
        """Finalise la séance : FSRS + maîtrise + baseline RT + persistance.

        Utilisée par la clôture explicite (``terminer``) ET par le
        garde-fou de durée (auto-clôture au-delà de ``duree_max_s``).
        Résumé du contrat : items RÉPONDUS (pas seulement servis) — une
        séance abandonnée en cours de route reste cohérente ; les essais
        dupliqués ne comptent pas (première réponse par item, fait foi).
        """
        resume_moteur = session.runner.terminer()
        self._appliquer_fsrs(session, maintenant)
        nb_repondu = len(session.reponses)
        nb_correctes = sum(1 for correcte in session.reponses.values() if correcte)
        taux = nb_correctes / nb_repondu if nb_repondu else 0.0
        self._appliquer_maitrise(session, nb_repondu, taux)
        # Baseline RT : on accumule les temps corrects de la séance.
        temps_accumules = self.stockage.lire_temps_reference(session.theme)
        temps_accumules.extend(session.temps_reference)
        self.stockage.ecrire_temps_reference(session.theme, temps_accumules[-100:])
        session.terminee = True
        return resume_moteur, nb_repondu, nb_correctes, taux

    # -- interne ---------------------------------------------------------------

    def _session(self, theme: str, session_id: str) -> SessionEnCours:
        """Retrouve une séance en mémoire ; thème et identifiant doivent coïncider."""
        session = self._sessions.get(session_id)
        if session is None or session.theme != theme:
            raise SessionInconnue(session_id)
        return session

    def _appliquer_fsrs(self, session: SessionEnCours, maintenant: datetime) -> None:
        """Met à jour les cartes FSRS des items répondus puis persiste le deck."""
        if not session.reponses:
            return
        cartes = self.stockage.lire_cartes(session.theme)
        for item_id, correcte in session.reponses.items():
            carte = cartes.get(item_id) or CarteFSRS(item_id)
            note = NOTE_REUSSITE if correcte else NOTE_ECHEC
            cartes[item_id] = planifier(carte, note, maintenant)[0]
        self.stockage.ecrire_cartes(session.theme, cartes)

    def _appliquer_maitrise(
        self, session: SessionEnCours, nb_repondu: int, taux: float
    ) -> None:
        """Historise le taux de la séance et applique le critère de maîtrise.

        Une séance sans item répondu n'est pas historisée (aucun signal).
        Critère : 90 % de réussite sur 3 séances consécutives au même
        palier → le palier courant avance d'un cran.
        """
        if nb_repondu <= 0:
            return
        etat = self.stockage.lire_maitrise(session.theme)
        historique = list(etat["historique"])
        historique.append((session.palier, float(taux)))
        palier = etat["palier_courant"]
        if palier_maitrise_historique(
            historique,
            palier=session.palier,
            seuil=SEUIL_MAITRISE,
            sessions_consecutives=SESSIONS_CONSECUTIVES_MAITRISE,
        ):
            palier = max(palier, session.palier + 1)
        self.stockage.ecrire_maitrise(session.theme, palier, historique)
