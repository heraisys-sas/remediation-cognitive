"""Détection de fatigabilité cognitive — source unique (issue #3).

Regroupe les seuils et la décision d'alerte partagés par :
- `engine.session.runner` (moteur de séance) ;
- `backend.app.domain.fatigue` (garde-fou clinique côté domaine).

Décision d'harmonisation : la comparaison du **taux d'erreur** est
largement (`>=`) afin de proposer l'arrêt dès que le taux **atteint** le
seuil (position protectrice : on alerte tôt). La comparaison du **temps de
réaction** reste stricte (`>`). L'alerte reste une **proposition**
(jamais une interruption forcée) : la fonction n'interrompt rien d'elle-même.
"""

from __future__ import annotations

# Seuils de fatigabilité (docs/10-clinique/protocoles.md).
SEUIL_RT_FATIGUE = 1.25  # RT moyen glissant > 1,25 x baseline -> proposition
SEUIL_TAUX_ERREUR = 0.40  # taux d'erreur glissant >= 0,40 -> proposition
FENETRE_FATIGUE = 5  # réponses récentes prises en compte
MIN_REPONSES_FATIGUE = 3  # anti-bruit : pas d'alerte avant ce nombre


def taux_erreur(reponses: list[bool]) -> float:
    """Taux d'erreur sur une fenêtre de réponses (True = correct).

    0.0 sur fenêtre vide.
    """
    if not reponses:
        return 0.0
    return 1.0 - sum(1 for correct in reponses if correct) / len(reponses)


def alerter_fatigue(
    rt_glissant: list[float],
    baseline_rt: float,
    taux_erreur_glissant: float = 0.0,
    seuil_rt: float = SEUIL_RT_FATIGUE,
    seuil_erreur: float = SEUIL_TAUX_ERREUR,
    nb_reponses: int | None = None,
    min_reponses: int = MIN_REPONSES_FATIGUE,
) -> bool:
    """True si une alerte de fatigue doit être **proposée** à l'utilisateur.

    Règle unique :
      - RT moyen glissant > seuil_rt * baseline_rt (strict), OU
      - taux d'erreur glissant >= seuil_erreur (atteinte = déclenchement).

    Garde anti-bruit : si `nb_reponses` est fourni et < `min_reponses`,
    aucune alerte n'est émise (évite les faux positifs en début de séance).
    """
    if nb_reponses is not None and nb_reponses < min_reponses:
        return False
    depassement_rt = False
    if rt_glissant:
        rt_moyen = sum(rt_glissant) / len(rt_glissant)
        depassement_rt = rt_moyen > baseline_rt * seuil_rt
    depassement_erreur = taux_erreur_glissant >= seuil_erreur
    return depassement_rt or depassement_erreur
