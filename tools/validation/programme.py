from __future__ import annotations

from pathlib import Path




from .common import (
    RACINE_DEPOT, THEMES_CONNUS, TYPES_JOUR, est_entier,
)

def erreurs_programme(
    donnees: object, chemin: Path, paliers_par_theme: dict[str, int]
) -> list[str]:
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(donnees, dict) or not isinstance(donnees.get("semaines"), list):
        return [prefixe + "programme attendu : objet avec une liste 'semaines'"]

    erreurs: list[str] = []
    semaines = donnees["semaines"]
    if not est_entier(donnees.get("duree_semaines")) or donnees["duree_semaines"] != len(semaines):
        erreurs.append(prefixe + "duree_semaines doit correspondre au nombre de semaines listées")

    for position, semaine in enumerate(semaines, start=1):
        if not isinstance(semaine, dict):
            erreurs.append(prefixe + f"semaine {position} : objet attendu")
            continue
        if semaine.get("semaine") != position:
            erreurs.append(prefixe + f"semaine {position} : champ semaine = {semaine.get('semaine')!r}")
        duree = semaine.get("duree_min")
        if not est_entier(duree) or not 1 <= duree <= 15:
            erreurs.append(prefixe + f"semaine {position} : duree_min doit être un entier 1..15")

        plafonds = semaine.get("plafond_palier")
        if not isinstance(plafonds, dict) or not plafonds:
            erreurs.append(prefixe + f"semaine {position} : plafond_palier manquant")
        else:
            for theme, plafond in plafonds.items():
                if theme not in THEMES_CONNUS:
                    erreurs.append(prefixe + f"semaine {position} : thème inconnu {theme!r}")
                    continue
                if not est_entier(plafond) or plafond < 1:
                    erreurs.append(prefixe + f"semaine {position} : plafond {theme} doit être ≥ 1")
                elif theme in paliers_par_theme and plafond > paliers_par_theme[theme]:
                    erreurs.append(
                        prefixe
                        + f"semaine {position} : plafond {theme} ({plafond}) dépasse les "
                        + f"{paliers_par_theme[theme]} paliers disponibles"
                    )

        jours = semaine.get("jours")
        if not isinstance(jours, list) or len(jours) != 7:
            erreurs.append(prefixe + f"semaine {position} : 7 jours attendus")
            continue
        for jour in jours:
            if not isinstance(jour, dict):
                erreurs.append(prefixe + f"semaine {position} : jour attendu comme objet")
                continue
            type_jour = jour.get("type")
            if type_jour not in TYPES_JOUR:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')!r} : type {type_jour!r}")
            themes = jour.get("themes")
            if not isinstance(themes, list) or not all(isinstance(t, str) for t in themes):
                erreurs.append(prefixe + f"semaine {position} : themes doit être un tableau")
                continue
            for theme in themes:
                if theme != "au-choix" and theme not in THEMES_CONNUS:
                    erreurs.append(prefixe + f"semaine {position} : thème inconnu {theme!r}")
            if type_jour == "repos" and themes:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : un jour de repos ne propose pas de thème")
            if type_jour == "seance" and len(themes) != 1:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : une séance propose un seul thème")
            duree_jour = jour.get("duree_min")
            if not est_entier(duree_jour) or not 0 <= duree_jour <= 15:
                erreurs.append(prefixe + f"semaine {position} jour {jour.get('jour')} : duree_min 0..15 attendu")
    return erreurs

def erreurs_missions(donnees: object, chemin: Path) -> list[str]:
    prefixe = f"{chemin.relative_to(RACINE_DEPOT)}: "
    if not isinstance(donnees, dict) or not isinstance(donnees.get("missions"), list):
        return [prefixe + "fichier de missions attendu : objet avec une liste 'missions'"]
    erreurs: list[str] = []
    ids_vus: set[str] = set()
    for position, mission in enumerate(donnees["missions"], start=1):
        if not isinstance(mission, dict):
            erreurs.append(prefixe + f"mission {position} : objet attendu")
            continue
        identifiant = mission.get("id")
        if not isinstance(identifiant, str) or not identifiant:
            erreurs.append(prefixe + f"mission {position} : id manquant")
        elif identifiant in ids_vus:
            erreurs.append(prefixe + f"mission {position} : id dupliqué {identifiant!r}")
        else:
            ids_vus.add(identifiant)
        if not isinstance(mission.get("titre"), str) or not mission["titre"].strip():
            erreurs.append(prefixe + f"mission {position} : titre manquant")
        if not est_entier(mission.get("niveau")) or mission["niveau"] < 1:
            erreurs.append(prefixe + f"mission {position} : niveau doit être un entier ≥ 1")
        etapes = mission.get("etapes")
        if not isinstance(etapes, list) or not etapes or not all(isinstance(e, str) and e.strip() for e in etapes):
            erreurs.append(prefixe + f"mission {position} : etapes doit être une liste non vide de chaînes")
        for champ in ("pourquoi", "repere"):
            if not isinstance(mission.get(champ), str) or not mission[champ].strip():
                erreurs.append(prefixe + f"mission {position} : {champ} manquant")
        if "duree_estimee_min" in mission and (
            not est_entier(mission["duree_estimee_min"]) or mission["duree_estimee_min"] < 1
        ):
            erreurs.append(prefixe + f"mission {position} : duree_estimee_min doit être un entier ≥ 1")
    return erreurs
