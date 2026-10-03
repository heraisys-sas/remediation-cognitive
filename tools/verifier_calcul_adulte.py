"""Recalcul indépendant depuis le seul énoncé affiché (pas depuis ses métadonnées)."""
import ast
import operator
import re
from decimal import Decimal


def recalculer(texte):
    n = [Decimal(x.replace(',', '.')) for x in re.findall(r'\d+(?:,\d+)?', texte)]
    if texte.startswith('Combien font ') and '%' not in texte:
        expression = texte.removeprefix('Combien font ').removesuffix(' ?')
        expression = expression.replace('−', '-').replace('×', '*').replace('÷', '/').replace(',', '.')
        if not re.fullmatch(r'[\d. +*/()-]+', expression):
            return None
        def evaluer(node):
            if isinstance(node, ast.Constant):
                return Decimal(str(node.value))
            if isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
                return {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul, ast.Div:operator.truediv}[type(node.op)](evaluer(node.left),evaluer(node.right))
            raise ValueError('Expression non arithmétique')
        return evaluer(ast.parse(expression, mode='eval').body)
    if re.fullmatch(r'Combien font \d+ % de \d+ \?', texte): return n[0]*n[1]/100
    if texte.startswith('Combien manque-t-il à '): return n[1]-n[0]
    if re.fullmatch(r'\d+ = \? × \d+', texte): return n[0]/n[1]
    if texte.startswith('Une commande contient '): return n[0]*n[1]+n[2]*n[3]
    if texte.startswith('Un nombre est multiplié '): return (n[2]-n[1])/n[0]
    if texte.startswith('Un atelier possède '): return n[0]+n[1]*n[2]-n[3]
    if texte.startswith('Trois mesures doivent '): return 3*n[0]-n[1]-n[2]
    if texte.startswith('Achat de '): return n[0]*n[1]+n[2]-n[3]
    if texte.startswith('Budget de '): return n[0]-n[1]-n[2]
    if texte.startswith('Un lot de ') and 'dossiers' in texte: return n[1]/n[0]
    if texte.startswith('On paie '): return n[2]-n[0]*n[1]
    if texte.startswith('Pour ') and 'g de riz' in texte:
        return n[1]*n[2]/n[0]-(n[3] if 'déjà' in texte else 0)
    if 'interventions de ' in texte: return n[0]*n[1]+(n[0]-1)*n[2]
    if texte.startswith('Une machine produit '): return n[0]*n[2]/n[1]
    if texte.startswith('Travail de '): return 60*(n[2]-n[0])+n[3]-n[1]-n[4]
    if texte.startswith('Un article coûte '): return n[0]*(100-n[1])/100
    if texte.startswith('Un budget de '): return n[0]*(100+n[1])/100
    if texte.startswith('Après une remise de '): return n[1]*100/(100-n[0])
    if texte.startswith('Une quantité passe de '): return (n[1]-n[0])*100/n[0]
    if texte.startswith('Pour ') and 'utilisations : offre A' in texte: return n[3]+n[4]*n[0]-n[1]-n[2]*n[0]
    if texte.startswith('Offre A : '): return (n[0]-n[2])/(n[3]-n[1])
    if 'articles à ' in texte and 'Livraison de ' in texte: return n[0]*n[1]+(n[2] if n[0]*n[1]<n[3] else 0)
    if texte.startswith('Un lot de ') and 'inutilisables' in texte: return n[1]/(n[0]-n[2])
    if texte.startswith('Un prix de '): return n[0]*(100+n[1])*(100-n[2])/10000
    if texte.startswith('Un atelier accueille '): return n[0]*(n[1]-n[3])-n[2]
    if texte.startswith('Vente de '): return n[0]*n[1]*(100-n[2])/100-n[3]
    return None
