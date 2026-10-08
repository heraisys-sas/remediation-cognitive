from __future__ import annotations

import re
import math




from .common import (
    est_entier,
)

MOTIF_ID_CALCUL = re.compile(r"^(?:cm[23]-\d+-\d+|cm4-\d+-[0-9a-f]{12})$")

MOTIF_CALCUL_ARITHMETIQUE = re.compile(r"Combien font (\d+) ([+−×]) (\d+)((?: [+−] \d+)?) ?\?")

MOTIF_COMPLEMENT = re.compile(r"Combien manque-t-il à (\d+) pour faire (\d+) \?")

MOTIF_TOTAL_ARTICLES = re.compile(r"(\d+) articles à ([\d,]+) € — combien en tout \?")

MOTIF_RENDU = re.compile(r"Un article à (\d+) €, payé avec (\d+) € — combien te rend-on \?")

MOTIF_SUITE_CONTINUE = re.compile(r"(?:Continue la suite|Compte à rebours) : ([\d, ]+), \s*\?")

MOTIF_SUITE_ERREUR = re.compile(r"([\d, ]+) — quel nombre est faux \?")

MOTIF_FAIT_INVERSE_GAUCHE = re.compile(r"(\d+) = (\d+) × \?")

MOTIF_FAIT_INVERSE_DROITE = re.compile(r"(\d+) = \? × (\d+)")

MOTIF_CHAINE = re.compile(r"^\d+(?: [+−] \d+)+$")

def _reponse_calculee(enonce: str) -> int | None:
    """Recalcule la réponse d'un énoncé de calcul mental — ou None si non calculable.

    Contrôle **indépendant du générateur** : on relit la question telle qu'elle sera
    lue, et on refait le calcul. Une erreur de contenu (mauvais résultat associé à une
    question) est ainsi détectée mécaniquement. Les énoncés de la vie quotidienne
    (quantités, durées) ne sont pas calculables automatiquement : on n'invente rien,
    ils sont contrôlés en forme seulement.
    """
    try:
        from tools.verifier_calcul_adulte import recalculer
    except ModuleNotFoundError:
        from verifier_calcul_adulte import recalculer
    adulte = recalculer(enonce)
    if adulte is not None:
        return float(adulte)
    correspondance = MOTIF_CALCUL_ARITHMETIQUE.fullmatch(enonce.strip())
    if correspondance:
        a, operateur, b, suite = (
            int(correspondance.group(1)), correspondance.group(2),
            int(correspondance.group(3)), correspondance.group(4),
        )
        resultat = a + b if operateur == "+" else a - b if operateur == "−" else a * b
        if suite:
            reste = suite.strip()
            operateur2, nombre2 = reste[0], reste[1:].strip()
            resultat = resultat + int(nombre2) if operateur2 == "+" else resultat - int(nombre2)
        return resultat

    correspondance = MOTIF_COMPLEMENT.fullmatch(enonce.strip())
    if correspondance:
        return int(correspondance.group(2)) - int(correspondance.group(1))

    correspondance = MOTIF_TOTAL_ARTICLES.fullmatch(enonce.strip())
    if correspondance:
        prix = float(correspondance.group(2).replace(",", "."))
        return int(round(int(correspondance.group(1)) * prix))

    correspondance = MOTIF_RENDU.fullmatch(enonce.strip())
    if correspondance:
        return int(correspondance.group(2)) - int(correspondance.group(1))

    # Série de calcul : évaluation de gauche à droite, comme la personne la fait.
    if MOTIF_CHAINE.match(enonce.strip()):
        jetons = enonce.split()
        total = int(jetons[0])
        for rang in range(1, len(jetons) - 1, 2):
            operateur, valeur = jetons[rang], int(jetons[rang + 1])
            total = total + valeur if operateur == "+" else total - valeur
        return total

    # Suite à continuer : le pas se lit sur les deux premiers nombres.
    correspondance = MOTIF_SUITE_CONTINUE.fullmatch(enonce.strip())
    if correspondance:
        nombres = [int(n) for n in correspondance.group(1).split(",")]
        pas = nombres[1] - nombres[0]
        return nombres[-1] + pas

    # Repérer l'erreur : le pas se lit sur les deux premiers nombres.
    correspondance = MOTIF_SUITE_ERREUR.fullmatch(enonce.strip())
    if correspondance:
        nombres = [int(n) for n in correspondance.group(1).split(",")]
        pas = nombres[1] - nombres[0]
        attendus = [nombres[0] + pas * rang for rang in range(len(nombres))]
        fautifs = [reel for reel, attendu in zip(nombres, attendus) if reel != attendu]
        return fautifs[0] if len(fautifs) == 1 else None

    # Fait cherché par l'autre bout : « 42 = 6 × ? ».
    correspondance = MOTIF_FAIT_INVERSE_GAUCHE.fullmatch(enonce.strip())
    if correspondance:
        produit, facteur = int(correspondance.group(1)), int(correspondance.group(2))
        return produit // facteur if facteur and produit % facteur == 0 else None
    correspondance = MOTIF_FAIT_INVERSE_DROITE.fullmatch(enonce.strip())
    if correspondance:
        produit, facteur = int(correspondance.group(1)), int(correspondance.group(2))
        return produit // facteur if facteur and produit % facteur == 0 else None
    return None

def erreurs_coherence_calcul(item: dict, prefixe: str,
                             manifest_par_theme: dict[str, dict[int, dict]]) -> list[str]:
    """Vérifie un item de calcul mental d'après son **énoncé**, pas d'après son rang.

    Contrôles : le palier existe dans le manifest ; la réponse est un entier positif ;
    et — quand l'énoncé est calculable — la réponse recalculée correspond. C'est ce
    dernier contrôle qui attrape une question associée au mauvais résultat.
    """
    theme = item.get("theme")
    if theme not in manifest_par_theme:
        return []
    palier = item.get("palier")
    if not est_entier(palier) or palier not in manifest_par_theme[theme]:
        return [prefixe + f"palier {palier!r} absent du manifest du thème {theme!r}"]

    identifiant = item.get("id", "")
    if not MOTIF_ID_CALCUL.fullmatch(identifiant):
        return [prefixe + f"id non conforme au motif cm2/cm3 ou cm4-<palier>-<empreinte> : {identifiant!r}"]

    enonce = str((item.get("contenu") or {}).get("enonce") or "")
    reponse = (item.get("reponse") or {}).get("valeur")
    if isinstance(reponse, bool) or not isinstance(reponse, (int, float)) or not math.isfinite(reponse) or reponse < 0:
        return [prefixe + f"réponse numérique finie positive attendue, reçue {reponse!r}"]
    attendue = _reponse_calculee(enonce)
    if attendue is not None and attendue != reponse:
        return [prefixe + f"« {enonce} » vaut {attendue}, pas {reponse}"]
    return []

def couverture_calcul(items: list) -> tuple[int, int]:
    """Nombre d'items de calcul mental recalculables, et total.

    Mesure de **couverture** : si un motif de contrôle se casse (un point d'interrogation
    non échappé, par exemple), une famille entière cesse d'être vérifiée sans que rien ne
    le signale. Un contrôle qui ne contrôle rien est plus dangereux que pas de contrôle :
    la couverture du thème est donc mesurée et seuilée.
    """
    calcul = [item for item in items if isinstance(item, dict)
              and item.get("theme") == "calcul-mental"]
    verifiables = sum(1 for item in calcul
                      if _reponse_calculee(str((item.get("contenu") or {}).get("enonce") or "")) is not None)
    return verifiables, len(calcul)
