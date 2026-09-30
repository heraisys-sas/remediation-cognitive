"""Lisibilité P2 et exactitude des aides sans information cachée."""
from copy import deepcopy
from backend.app.domain.contenu import ChargeurContenu
from deduction_accompagnement import regrouper_meme_pion
from deduction_commun import informations_autonomes, phrases_qui_fixent_seules
import validate_items

F=['cercle','carre','triangle']; C=['rouge','bleu','vert']


def test_regroupe_deux_reperes_du_meme_pion_sans_le_placer():
    a={'type':'pas-ligne','figure':'carre','couleur':'bleu','ligne':0}
    b={'type':'pas-colonne','figure':'carre','couleur':'bleu','colonne':0}
    resultat=regrouper_meme_pion([a,b],3,F,C)
    assert len(resultat)==1 and resultat[0]['et']==[b]
    assert not phrases_qui_fixent_seules(resultat,3,F,C)
    assert regrouper_meme_pion([{**a,'type':'ligne'},{**b,'type':'colonne'}],3,F,C)==[
        {**a,'type':'ligne'},{**b,'type':'colonne'}]


def test_palier2_sujet_unique_et_aides_sur_tous_les_paliers():
    items=list(ChargeurContenu().items('deduction'))
    groupes=0
    for item in items:
        c=item['contenu']
        assert c['indices']==[]
        assert c['aide_raisonnement']
        assert not validate_items._erreurs_grille_deduction(item,'',c)
        if item['palier']==2:
            for ph in c['enonces']:
                atomes=informations_autonomes(ph)
                assert len(atomes)<=2
                if len(atomes)==2:
                    groupes+=1
                    assert len({(a['figure'],a['couleur']) for a in atomes})==1
                    assert not any('figure2' in a for a in atomes)
    assert groupes>=7, 'le regroupement doit être présent dans les exercices servis'


def test_refuse_aide_qui_invente_une_possibilite_ou_une_etape():
    item=next(i for i in ChargeurContenu().items('deduction') if i['contenu']['aide_raisonnement']['mode']=='croisement')
    for cible in ('possibilites','demonstration'):
        faux=deepcopy(item);c=faux['contenu'];a=c['aide_raisonnement']
        if cible=='possibilites': a['possibilites'][0]=[]
        else: a['demonstration'][0]['reductions'][0]['cases']=[]
        assert any('aide de raisonnement invalide' in e for e in validate_items._erreurs_grille_deduction(faux,'',c))
