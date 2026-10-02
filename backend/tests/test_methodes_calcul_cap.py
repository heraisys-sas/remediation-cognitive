import json
from pathlib import Path
import re
import subprocess
import shutil
from tools.methodes_calcul import methode_calcul
from tools.verifier_interface import corps_fonction
from backend.app.domain.contenu import ChargeurContenu

ROOT=Path(__file__).resolve().parents[2]


def test_methodes_adaptees_et_couverture():
    for path in (ROOT/'content/entrainement/calcul-mental/paliers').glob('*.json'):
        for item in json.loads(path.read_text()):
            assert item['contenu']['methode']==methode_calcul(item['contenu']['enonce'],item['palier'])
            assert 'aide' not in item['contenu']
    assert 'centimes' in methode_calcul('2 articles à 1,50 € — combien en tout ?',8)
    assert 'monnaie rendue' in methode_calcul('Un article à 7 €, payé avec 10 € — combien te rend-on ?',8)
    assert 'Convertis' in methode_calcul("Trois rendez-vous d'une heure trente ? (en minutes)",9)
    assert 'stock' in methode_calcul('Une boîte de 30 comprimés',9)
    assert 'dix' not in methode_calcul('Combien font 2 + 6 ?',3)
    assert 'double' in methode_calcul('Combien font 6 + 6 ?',3)
    assert '9' in methode_calcul('72 = ? × 9',12)
    assert '72' not in methode_calcul('72 = ? × 9',12)


def test_garder_cap_accessible_et_corrige(client):
    themes=client.get('/api/entrainement/themes').json()['themes']
    theme=next(t for t in themes if t['id']=='garder-cap')
    assert theme['categorie']=='entrainement'
    contenu=ChargeurContenu()
    for palier in (2,3):
        r=client.post('/api/entrainement/garder-cap/sessions',json={'palier':palier})
        assert r.status_code==201,r.text
        session=r.json();assert len(session['items'])==4
        item=session['items'][0]
        assert 'affichage' not in item['contenu'] and 'reponse' not in item
        bonne=contenu.item('garder-cap',item['id'])['reponse']['valeur']
        mauvaise=next(o for o in item['contenu']['options'] if o!=bonne)
        url=f"/api/entrainement/garder-cap/sessions/{session['session_id']}/reponses"
        premier=client.post(url,json={'item_id':item['id'],'reponse':mauvaise,'temps_ms':1000})
        assert premier.status_code==200,premier.text
        assert premier.json().get('attendue') is None
        second=client.post(url,json={'item_id':item['id'],'reponse':bonne,'temps_ms':2000})
        assert second.status_code==200 and second.json()['correcte']


def test_reprise_reellement_interrompue_et_correction_detaillee(client):
    contenu=ChargeurContenu()
    items=[i for i in contenu.items('garder-cap') if i['palier']==1]
    assert len(items)==12
    assert {i['contenu']['interruption_apres'] for i in items}=={1,2,3}
    assert all(i['type']=='reprise-interrompue' and len(i['contenu']['points'])==4 for i in items)
    profils={tuple(i['reponse']['valeur']['points'][p['id']] for p in i['contenu']['points']) for i in items}
    assert len(profils)>=5
    for position in range(4):
        assert {tuple(i['reponse']['valeur']['points'].values())[position] for i in items}=={'valide','reprendre'}
    session=client.post('/api/entrainement/garder-cap/sessions',json={
        'parcours':'reprendre','palier':1}).json()
    assert len(session['items'])==4
    public=session['items'][0]; complet=contenu.item('garder-cap',public['id'])
    assert 'reponse' not in public
    bonne=complet['reponse']['valeur']
    payload={**bonne,'interruption':'réponse non notée'}
    url=f"/api/entrainement/garder-cap/sessions/{session['session_id']}/reponses"
    resultat=client.post(url,json={'item_id':public['id'],'reponse':payload,'temps_ms':4000})
    assert resultat.status_code==200,resultat.text
    corps=resultat.json();assert corps['correcte']
    assert corps['detail_fonctionnel']['type']=='reprise-interrompue'
    assert corps['detail_fonctionnel']['interruption_non_notee'] is True
    assert len(corps['detail_fonctionnel']['lignes'])==5

    mauvaise={**bonne,'reprise':complet['contenu']['points'][0]['id']}
    if mauvaise['reprise']==bonne['reprise']:
        mauvaise['reprise']=complet['contenu']['points'][-1]['id']
    from backend.app.domain.attention_fonctionnelle import corriger_detail
    juste,detail=corriger_detail(complet,mauvaise)
    assert not juste and not detail['lignes'][-1]['correcte']


def test_panneau_methode_specifique_ou_masque_sans_repli_generique():
    source=(ROOT/'frontend/src/app.js').read_text()
    types_consigne = re.search(
        r'const TYPES_CONSIGNE_COMME_METHODE = new Set\(\[.*?\]\);', source, re.S
    ).group(0)
    methodes_type = re.search(
        r'const METHODES_PAR_TYPE = Object\.freeze\(\{.*?\}\);', source, re.S
    ).group(0)
    script=types_consigne+'\n'+methodes_type+'''
const assert=require('node:assert/strict');
const refs=new Proxy({}, {get(o,k){return o[k]??={style:{},setAttribute(){}}}});
const etat={session:{items:[]},indexItem:0,reprisesAfficher:new Set()};
function annulerMemo(){} function afficherQuestion(){} function afficherPhaseMemo(){}
'''+ 'function methodePourItem(item) '+corps_fonction(source,'methodePourItem') \
        +'\nfunction montrerItem() '+corps_fonction(source,'montrerItem')+'''
etat.session.items=[{id:'calcul',contenu:{methode:'Décompose le nombre.'}}];
refs.panneauMethode.open=true;
montrerItem();
assert.equal(refs.panneauMethode.open,false);
assert.equal(refs.panneauMethode.hidden,false);
assert.equal(refs.titreMethode.textContent,'Une méthode possible');
assert.equal(refs.methodeExercice.textContent,'Décompose le nombre.');

etat.session.items=[{id:'empan',type:'empan',contenu:{consigne:'Mémorise les chiffres.'}}];
montrerItem();
assert.equal(refs.panneauMethode.hidden,false);
assert.ok(refs.methodeExercice.textContent.includes('Regroupe mentalement'));

etat.session.items=[{id:'strategie',type:'auto-instruction',contenu:{consigne:'Formule une consigne avant d’agir.'}}];
montrerItem();
assert.equal(refs.panneauMethode.hidden,false);
assert.equal(refs.methodeExercice.textContent,'Formule une consigne avant d’agir.');

etat.session.items=[{id:'reconnaissance',type:'reconnaissance',contenu:{consigne:'Choisis le mot.'}}];
montrerItem();
assert.equal(refs.panneauMethode.hidden,true);
assert.equal(refs.methodeExercice.textContent,'');

etat.session.items=[{id:'guide',type:'pqrst-mise-en-oeuvre',contenu:{consigne:'Les étapes sont déjà affichées.'}}];
montrerItem();
assert.equal(refs.panneauMethode.hidden,true);
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)
