"""Séparation stricte des vocabulaires (garde-fou du cahier des charges).

- module bilan : vocabulaire clinique, disclaimers professionnels requis ;
- module rééducation : vocabulaire sobre, familial ;
- module entraînement : vocabulaire neutre, ludique modéré.

Aucune chaîne visible par l'utilisateur ne doit être construite hors de ce module.
"""

VOCABULAIRES = {
    "bilan": {
        "titre_session": "Bilan de suivi",
        "disclaimer": (
            "Ce bilan ne constitue pas un diagnostic. "
            "Partagez l'export avec votre professionnel de santé référent."
        ),
    },
    "reeducation": {
        "titre_session": "Séance de rééducation",
    },
    "entrainement": {
        "titre_session": "Session d'entraînement",
        # Libellés des thèmes exposés par l'API (contrat GET /themes).
        "themes": {
            "calcul-mental": {
                "nom": "Calcul mental",
                "description": "Tables et calcul rapide, paliers progressifs",
            },
            "anglais": {
                "nom": "Anglais — verbes irréguliers",
                "description": "Rappel actif : écris le verbe demandé, sans proposition de choix",
            },
            "python": {
                "nom": "Python",
                "description": "Commandes du langage et prédiction de sortie de snippets",
            },
            "memoire": {
                "nom": "Mémoire",
                "description": "Empans de chiffres et de mots, séquences et associations — mémorisation progressive",
            },
            "rappel-series": {
                "nom": "Rappel de séries",
                "description": "Plusieurs séries de mots, puis rappel libre de tout ce dont on se souvient",
            },
            "quotidien": {
                "nom": "Au quotidien",
                "description": "Mémoire de travail, planification et anticipation dans des situations de la vie",
            },
            "deduction": {
                "nom": "Déduction",
                "description": "Grilles logiques 3×3 : figures et couleurs à placer en recoupant les indices",
            },
            "methodes": {
                "nom": "Méthodes",
                "description": "PQRST, but et étapes, auto-instruction : des méthodes pour s'organiser et retenir",
            },
            "concentration": {
                "nom": "Concentration",
                "description": "Calculs chaînés, double tâche et séries — une attention qui tient",
            },
            "evocation": {
                "nom": "Retrouver le mot",
                "description": "Définitions, indices progressifs, mémoire du contexte — retrouver ce qu'on sait déjà",
            },
        },
        # Feedback immédiat guidé (correction serveur).
        "feedback_correcte": "Bien joué, réponse correcte !",
        "feedback_incorrecte": "Pas tout à fait — la réponse attendue s'affiche, on y reviendra.",
        "feedback_assiste": "Voici la réponse — on la reverra bientôt, sans indice cette fois.",
        # Messages d'erreur (clés : erreur_<code machine du contrat>).
        "erreur_theme_inconnu": "Thème inconnu.",
        "erreur_session_inconnue": "Séance introuvable (elle n'existe plus en mémoire).",
        "erreur_session_terminee": "Cette séance est déjà terminée.",
        "erreur_item_hors_seance": "Cet item ne fait pas partie de la séance en cours.",
        "erreur_reponse_invalide": "Réponse ou temps invalide.",
    },
    "missions": {
        "titre_session": "Missions dans la vraie vie",
        "mission_inconnue": "Mission inconnue.",
        "journal_entree_invalide": "Note invalide (texte manquant ou trop long).",
    },
}


def texte(cle_module: str, cle_message: str) -> str:
    """Retourne un texte du vocabulaire du module — erreur si le module inconnu."""
    return VOCABULAIRES[cle_module][cle_message]
