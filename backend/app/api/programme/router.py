"""Routes du programme d'entraînement (contenu de cadrage, non médical).

- `GET /api/programme` — le programme complet (8 semaines) et le **plan du jour**,
  avec la date de début posée à la première consultation.

Le programme ne contraint rien : il propose un rythme, une rotation de thèmes et
un **plafond** de palier par semaine. L'avancement réel d'un palier reste décidé
par la maîtrise (90 % × 3 séances), dans le moteur — jamais par le calendrier.
"""

from __future__ import annotations

from fastapi import APIRouter, Request

from ...domain.programme import resume_programme

router = APIRouter(prefix="/api/programme", tags=["programme"])


@router.get("")
def lire_programme(request: Request) -> dict:
    """Programme complet + plan du jour (pose la date de début au premier appel)."""
    contenu = request.app.state.gestionnaire_entrainement.contenu
    programme = contenu.programme()
    stockage = request.app.state.stockage_programme
    horloge = request.app.state.horloge

    aujourd_hui = horloge().date()
    date_debut = stockage.definir_date_debut(aujourd_hui)

    return {
        "programme": programme,
        "date_debut": date_debut.isoformat(),
        "aujourd_hui": resume_programme(programme, date_debut, aujourd_hui),
        "regles": programme.get("regles", {}),
    }
