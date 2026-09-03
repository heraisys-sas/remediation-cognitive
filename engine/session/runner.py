"""Orchestration d'une séance.

Responsabilités :
- sélection des items (règle adaptative + FSRS) ;
- respect du dosage (limite sessions/jour, durée 5–10 min) ;
- surveillance de la fatigabilité (voir backend/app/domain/fatigue.py) ;
- proposition d'arrêt (jamais forcée).
"""
