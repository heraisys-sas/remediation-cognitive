"""Dosage des séances (garde-fou clinique).

Règles issues de docs/10-clinique/protocoles.md :
- séance courte 5–10 min ;
- limite de sessions/jour paramétrable (dérogation explicite possible pour
  les thèmes d'entraînement — ADR-021) ;
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
#: et « 5-10 min » (protocoles.md). Ce qu'on ajuste par thème, c'est le **nombre
#: d'exercices** : une grille de déduction demande une chaîne de raisonnement complète
#: (mémoire de travail + fonctions exécutives) et dure bien plus longtemps qu'un item
#: de calcul mental — douze grilles ne tiendraient pas dans une séance.
PARAMETRES_THEME: dict[str, dict[str, int | bool]] = {
    "deduction": {"max_items": 6},
    "garder-cap": {"max_items": 4},
}
PARAMETRES_SEANCE_DEFAUT: dict[str, int | bool] = {
    "max_items": MAX_ITEMS_PAR_SEANCE,
    "duree_max_s": DUREE_MAX_SEANCE_S,
    "duree_proposee": True,
}


def parametres_seance(theme: str) -> dict[str, int | bool]:
    """Nombre d'exercices, durée maximale et nature de cette durée, pour ce thème."""
    return {**PARAMETRES_SEANCE_DEFAUT, **PARAMETRES_THEME.get(theme, {})}


def duree_proposee(theme: str) -> bool:
    """La durée maximale est-elle une **proposition** pour ce thème ?

    Oui, partout (ADR-010) : au-delà de la durée, la séance **propose** l'arrêt — elle ne
    se ferme pas d'elle-même, la personne décide de continuer ou non. Le garde-fou de
    sur-sollicitation reste : la limite de séances par jour, et le nombre d'exercices
    par séance. Le paramètre subsiste pour qu'un thème puisse un jour demander une limite
    ferme (le code de clôture existe toujours).
    """
    return bool(parametres_seance(theme)["duree_proposee"])

#: Nombre maximal de reprises par séance : un exercice manqué revient **une fois**, en fin
#: de séance, avec la réponse fournie avant le nouvel essai (errorless learning : ré-encoder
#: une erreur la renforce). Plafonné pour ne pas doubler la durée de la séance — au-delà, les
#: exercices manqués reviennent à la séance suivante, par la répétition espacée.
MAX_REPRISES_PAR_SEANCE = 4

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


def derogation_limite_sessions(categorie: str, demandee: bool) -> bool:
    """La dérogation explicite au plafond de séances du jour s'applique-t-elle ?

    La personne peut lever le plafond depuis l'accueil (« Dépasser la limite de
    séances du jour » — ADR-021). Portée volontairement limitée aux thèmes
    d'**entraînement** : l'évaluation reste plafonnée à une séance par jour —
    répéter une mesure la fausse. Le compteur du jour continue de compter les
    séances jouées sous dérogation : le dosage reste juste.
    """
    return demandee and categorie == "entrainement"
