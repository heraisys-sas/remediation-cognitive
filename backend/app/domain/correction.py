"""Correction côté serveur des réponses du module entraînement.

Garde-fou central : la réponse attendue d'un item ne quitte JAMAIS le
serveur avant la soumission de l'utilisateur. La comparaison se fait ici
(``corriger``), puis le résultat (correcte + réponse attendue révélée
après coup pour le feedback guidé) est renvoyé par l'API.

Règles par thème (docs/30-technique/api-contract.md) :
- ``calcul-mental`` : comparaison numérique — accepte ``56`` ou ``"56"`` ;
- ``anglais``       : texte insensible à la casse, espaces trimmés ;
- ``python``        : chaîne exacte trimmée — production comme
  ``prediction-sortie``.
"""

from __future__ import annotations

from numbers import Real

# Tolérance de comparaison flottante (représentations décimales exactes).
TOLERANCE_NUMERIQUE = 1e-9


def _normaliser_texte(valeur) -> str:
    """Normalise une valeur en texte comparable : trim + espaces réduits."""
    if valeur is None:
        return ""
    return " ".join(str(valeur).split())


def _corriger_numerique(reponse, attendue) -> bool:
    """Compare numériquement : accepte un nombre ou une chaîne numérique.

    La virgule décimale française est tolérée dans les chaînes
    (``"56,5"`` vaut 56.5). Tout ce qui n'est pas interprétable
    numériquement est faux.
    """
    if attendue is None or isinstance(reponse, bool):
        return False
    if isinstance(reponse, Real):
        valeur = float(reponse)
    else:
        try:
            valeur = float(str(reponse).strip().replace(",", "."))
        except ValueError:
            return False
    try:
        cible = float(attendue)
    except (TypeError, ValueError):
        return False
    return abs(valeur - cible) <= TOLERANCE_NUMERIQUE


def corriger(theme: str, item: dict, reponse) -> bool:
    """Retourne True si la réponse soumise correspond à la réponse attendue.

    - ``theme`` : identifiant API du thème (calcul-mental, anglais, python) ;
    - ``item`` : item complet côté serveur (avec ``reponse.valeur``) ;
    - ``reponse`` : réponse utilisateur (str ou nombre, corps du contrat).

    Fonction interne serveur : ne jamais l'exposer avant soumission.
    """
    attendue = (item.get("reponse") or {}).get("valeur")
    if theme == "calcul-mental":
        return _corriger_numerique(reponse, attendue)
    if theme == "anglais":
        return (
            _normaliser_texte(reponse).lower()
            == _normaliser_texte(attendue).lower()
        )
    # python — production et prediction-sortie : chaîne exacte trimmée
    # (cas sensitive ; la valeur attendue peut être str ou nombre).
    reponse_texte = "" if reponse is None else str(reponse)
    attendue_texte = "" if attendue is None else str(attendue)
    return reponse_texte.strip() == attendue_texte.strip()
