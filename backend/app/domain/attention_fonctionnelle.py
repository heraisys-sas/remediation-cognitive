"""Correction explicite des trois tâches fonctionnelles, sans similarité approximative."""
from .correction import _clef_reponse

TYPES = frozenset({'actualiser-consigne', 'comparer-documents', 'reperer-essentiel'})

def corriger_detail(item, reponse):
    c = item['contenu']
    attendu = item['reponse']['valeur']
    donne = reponse if isinstance(reponse, dict) else {}
    champs = c.get('champs') or [{'id':m['id'],'label':m['texte']} for m in c['messages']]
    lignes=[]
    omissions=fausses_selections=0
    for champ in champs:
        key=champ['id']; valeur=attendu[key]; fournie=donne.get(key)
        juste = isinstance(fournie, str) and _clef_reponse(fournie)==_clef_reponse(valeur)
        if item['type']=='reperer-essentiel':
            omissions += valeur=='oui' and fournie!='oui'
            fausses_selections += valeur=='non' and fournie=='oui'
        label={'oui':'À prendre en compte','non':'Sans conséquence selon les critères',
               'ecart':'Écart à corriger','conforme':'Conforme'}.get(valeur,valeur)
        lignes.append({'label':champ['label'],'correcte':juste,'attendue':label,
                       'explication':item['reponse'].get('explications',{}).get(key,'')})
    return all(l['correcte'] for l in lignes) and set(donne)==set(attendu), {
        'lignes':lignes,'omissions':omissions,'fausses_selections':fausses_selections,
        'type':item['type'],
    }
