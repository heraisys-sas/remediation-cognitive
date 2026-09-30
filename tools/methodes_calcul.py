"""Stratégies propres au problème, sans calculer ni fournir les résultats."""
import re

QUANTITES = {
    "Un pot de peinture": "Cherche combien de surfaces couvertes par un pot sont nécessaires pour couvrir la surface totale. Vérifie l’unité : des pots.",
    "Un film": "Additionne la durée du film et celle de la pause. Vérifie que ton total est plus long que le film seul.",
    "Trois rendez-vous": "Convertis une heure trente en minutes, puis multiplie cette durée par le nombre de rendez-vous. Vérifie l’unité : des minutes.",
    "Un paquet contient 10": "Retire du nombre initial les serviettes qui restent. Vérifie que prises et restantes reconstituent le paquet.",
    "20 tablettes": "Partage le total en groupes égaux : cherche combien chaque sachet reçoit. Vérifie en multipliant par le nombre de sachets.",
    "Quinze cartons": "Cherche combien de groupes de cinq cartons tu peux former. Vérifie que les piles reconstituent le total.",
    "Une boîte de 30": "Calcule la quantité utilisée pendant tous les jours indiqués, puis retire-la du stock initial. Garde le résultat intermédiaire en tête. Vérifie que le reste est inférieur au stock de départ.",
    "Deux litres": "Additionne les litres entiers, puis rassemble les deux demi-litres. Vérifie que tu réponds en litres.",
}


def methode_calcul(enonce: str, palier: int) -> str:
    if palier == 7:
        return "Effectue la première opération, garde son résultat en tête, puis applique la seconde. Vérifie le sens du dernier changement : un ajout augmente, un retrait diminue."
    if palier == 11:
        return "Compare les écarts entre plusieurs nombres pour repérer le pas régulier. Applique ce pas pour poursuivre la suite ou retrouver le nombre qui ne le respecte pas. Vérifie la règle sur toute la ligne."
    if palier == 12:
        facteur = re.search(r'(\d+)\s*×\s*\?|\?\s*×\s*(\d+)', enonce)
        n = next(g for g in facteur.groups() if g is not None)
        return f"Cherche combien de fois {n} permet d’atteindre le total : avance dans sa table en comptant les groupes. Vérifie en multipliant ton nombre de groupes par {n}."
    if palier == 8:
        if 'articles' in enonce:
            return ("Calcule séparément le total des euros et celui des centimes, puis rassemble-les. Vérifie que le total couvre tous les articles." if ',' in enonce else
                    "Multiplie le prix d’un article par le nombre d’articles. Tu peux additionner le même prix autant de fois. Vérifie que tu réponds en euros.")
        return "Pars du prix et complète jusqu’à la somme payée, en passant si utile par une dizaine. Additionne mentalement ces compléments. Vérifie que prix et monnaie rendue reconstituent la somme payée."
    if palier == 9:
        for debut, texte in QUANTITES.items():
            if enonce.startswith(debut):
                return texte
        if 'personnes' in enonce:
            return "Compare le nombre de personnes prévu et le nouveau nombre. Applique le même multiplicateur à la quantité. Vérifie que tu conserves l’unité de la recette."
        if 'minutes' in enonce or 'séance' in enonce or 'trajet' in enonce:
            return "Multiplie la durée d’une activité par le nombre d’activités. Vérifie que le total est exprimé en minutes."
        if enonce.startswith(('Un paquet contient 12', 'Quatre séries')):
            return "Multiplie la quantité d’un groupe par le nombre de groupes. Vérifie que tu comptes les éléments et non les groupes."
        raise ValueError(f'Quantité sans méthode adaptée : {enonce}')
    if 'manque-t-il' in enonce:
        return ("Pars du nombre indiqué et cherche ce qu’il faut ajouter pour atteindre dix. Vérifie en réunissant le nombre de départ et ton complément." if palier == 1 else
                "Complète d’abord jusqu’à la dizaine suivante si nécessaire, puis jusqu’à cent. Rassemble mentalement les deux compléments. Vérifie que départ et complément font cent.")
    match = re.search(r'(\d+) ([+−×]) (\d+)', enonce)
    if not match:
        raise ValueError(f'Calcul sans méthode : {enonce}')
    a, op, b = int(match[1]), match[2], int(match[3])
    if op == '+':
        if a + b <= 10 and a != b and abs(a-b) != 1:
            return 'Pars du plus grand nombre et avance du nombre d’unités indiqué par le plus petit. Vérifie en revenant en arrière du même nombre d’unités.'
        if a == b:
            return "Reconnais un double : le même nombre est ajouté deux fois. Utilise le double connu, ou décompose le nombre en parts faciles à doubler. Vérifie que le total est pair."
        if abs(a-b) == 1:
            return "Prends le double du plus petit nombre, puis ajoute une unité. Vérifie que le résultat est juste au-dessus de ce double."
        return "Complète le premier nombre jusqu’à dix avec une partie du second, puis ajoute ce qu’il reste. Vérifie que le résultat est plus grand que chacun des deux nombres."
    if op == '−':
        if a > 10 and a-b < 10:
            return "Retire d’abord ce qui permet d’arriver à dix, puis retire ce qu’il reste à enlever. Vérifie en ajoutant le retrait à ton résultat pour retrouver le départ."
        return "Décompose le nombre à retirer en parts faciles, puis enlève-les successivement. Vérifie en ajoutant le retrait à ton résultat pour retrouver le départ."
    facteur = next((n for n in (2,5,9,4,8,6,3,7) if n in (a,b)), None)
    strategies = {
        2: "Prends le double de l’autre nombre.",
        3: "Prends le double de l’autre nombre, puis ajoute encore ce nombre.",
        4: "Double l’autre nombre, puis double encore ce résultat.",
        5: "Multiplie l’autre nombre par dix, puis prends la moitié.",
        6: "Multiplie l’autre nombre par cinq, puis ajoute encore ce nombre.",
        7: "Décompose sept en cinq et deux : rassemble cinq fois et deux fois l’autre nombre.",
        8: "Multiplie l’autre nombre par quatre, puis double ce résultat.",
        9: "Multiplie l’autre nombre par dix, puis retire une fois ce nombre.",
    }
    return strategies[facteur] + " Vérifie en comparant avec un produit voisin que tu connais."
