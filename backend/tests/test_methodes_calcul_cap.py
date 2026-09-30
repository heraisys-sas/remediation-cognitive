import json
from pathlib import Path
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
    for palier in (1,2,3):
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


def test_panneau_methode_reinitialise_et_retour_generique():
    source=(ROOT/'frontend/src/app.js').read_text()
    script='''
const assert=require('node:assert/strict');
const refs=new Proxy({}, {get(o,k){return o[k]??={style:{},setAttribute(){}}}});
const etat={session:{items:[]},indexItem:0,reprisesAfficher:new Set()};
function annulerMemo(){} function afficherQuestion(){} function afficherPhaseMemo(){}
'''+ 'function montrerItem() '+corps_fonction(source,'montrerItem')+'''
etat.session.items=[{id:'calcul',contenu:{methode:'Décompose le nombre.'}}];
refs.panneauMethode.open=true;
montrerItem();
assert.equal(refs.panneauMethode.open,false);
assert.equal(refs.titreMethode.textContent,'Une méthode possible');
assert.equal(refs.methodeGenerique.hidden,true);
assert.equal(refs.methodeExercice.textContent,'Décompose le nombre.');
etat.session.items=[{id:'autre',contenu:{consigne:'Lis le message.'}}];
montrerItem();
assert.equal(refs.methodeGenerique.hidden,false);
assert.equal(refs.methodeExercice.textContent,'Lis le message.');
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)
