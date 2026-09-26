"""Dosage des séances (garde-fou clinique).

Règles issues de docs/10-clinique/protocoles.md :
- séance courte 5–10 min ;
- limite de sessions/jour paramétrable ;
- cap de difficulté configurable avec justification pédagogique explicite
  (anti sur-sollicitation post-commotionnelle).
"""


def verifier_droit_de_session(nb_sessions_du_jour: int, limite: int) -> bool:
    """True si l'utilisateur peut encore démarrer une séance aujourd'hui."""
    return nb_sessions_du_jour < limite


# Garde-fous chiffrés du sprint 1 (docs/30-technique/api-contract.md) —
# paramétrables ici uniquement, jamais côté client.
LIMITE_SESSIONS_JOUR = 3
MAX_ITEMS_PAR_SEANCE = 12
DUREE_MAX_SEANCE_S = 600

#: Paramètres de séance par thème, quand la **nature de l'exercice** le justifie.
#:
#: Le cadre clinique reste « séance courte, ≤ 10 min » (docs/10-clinique/cadre-usage.md)
#: et « 5-10 min » (protocoles.md) : on ajuste donc le **nombre d'exercices**, jamais
#: la durée — la durée maximale reste le garde-fou de sur-sollicitation.
#:
#: Déduction : chaque grille demande une chaîne de raisonnement complète (mémoire de
#: travail + fonctions exécutives, « charge soutenue ») et dure bien plus longtemps
#: qu'un item de calcul mental. Douze grilles ne tiennent pas dans une séance : on en
#: propose six, ce qui laisse la séance se terminer par son contenu et non par le
#: minuteur.
PARAMETRES_THEME: dict[str, dict[str, int]] = {
    "deduction": {"max_items": 6, "duree_max_s": 600},
}
PARAMETRES_SEANCE_DEFAUT: dict[str, int] = {
    "max_items": MAX_ITEMS_PAR_SEANCE,
    "duree_max_s": DUREE_MAX_SEANCE_S,
}


def parametres_seance(theme: str) -> dict[str, int]:
    """Nombre d'exercices et durée maximale d'une séance, pour ce thème."""
    return {**PARAMETRES_SEANCE_DEFAUT, **PARAMETRES_THEME.get(theme, {})}

#: Limite de séances par jour selon la CATÉGORIE du thème.
#: L'évaluation est volontairement limitée à une séance par jour : répéter une
#: mesure la fausse (effet d'apprentissage), alors que l'entraînement de
#: remédiation gagne à être régulier.
LIMITES_SESSIONS_JOUR: dict[str, int] = {
    "entrainement": 3,
    "evaluation": 1,
}


def appliquer_cap_difficulte(palier_demande: int, cap_actif: int) -> int:
    """Ne jamais dépasser le cap de difficulté actif."""
    return min(palier_demande, cap_actif)
