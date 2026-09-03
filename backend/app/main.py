"""Point d'entrée FastAPI (squelette).

Trois périmètres d'API strictement isolés (voir docs/30-technique/adr/ADR-002) :
- /api/entrainement : hors périmètre médical, diffusable librement ;
- /api/reeducation  : usage strictement familial ;
- /api/bilan        : données de santé — stockage chiffré séparé, périmètre HDS potentiel.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Bilan & rééducation cognitive (SPC)",
    version="0.1.0",
    description="Moteur adaptatif commun — entraînement (hors MDR), rééducation et bilan (usage familial).",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
