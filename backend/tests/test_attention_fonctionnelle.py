"""Correction, intégrité du contenu et indépendance des parcours."""
import json
from pathlib import Path
import pytest
from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction import corriger
from backend.app.domain.attention_fonctionnelle import corriger_detail

ROOT=Path(__file__).resolve().parents[2]
CONTENU=ChargeurContenu()
THEMES=('actualiser-consigne','comparer-documents','reperer-essentiel')

@pytest.mark.parametrize('theme', THEMES)
def test_cycle_fonctionnel_et_correction_point_par_point(client, theme):
    session=client.post(f'/api/entrainement/{theme}/sessions',json={'palier':3}).json()
    assert len(session['items'])==4
    for n,public in enumerate(session['items']):
        complet=CONTENU.item(theme,public['id'])
        assert 'reponse' not in public
        bonne=complet['reponse']['valeur']
        assert corriger(theme,complet,bonne)
        assert not corriger(theme,complet,{})
        assert not corriger(theme,complet,{**bonne,'inconnu':'x'})
        reponse=dict(bonne)
        if n==0: reponse[next(iter(reponse))]='erroné'
        res=client.post(f"/api/entrainement/{theme}/sessions/{session['session_id']}/reponses",json={
            'item_id':public['id'],'reponse':reponse,'temps_ms':2000})
        assert res.status_code==200,res.text
        assert res.json()['correcte']==(n!=0)
        assert len(res.json()['detail_fonctionnel']['lignes'])==len(bonne)
        assert '[object Object]' not in res.json()['attendue']
    fin=client.post(f"/api/entrainement/{theme}/sessions/{session['session_id']}/fin")
    assert fin.status_code==200


def test_reponses_actualisees_derivent_des_messages():
    for item in CONTENU.items('actualiser-consigne'):
        c=item['contenu'];etat=dict(c['etat_initial'])
        for etape in c['etapes']:
            if etape['evenement']=='mise_a_jour':
                etat[etape['champ']]=etape['nouveau']
        assert etat==item['reponse']['valeur'],item['id']
        assert len(c['etapes'])=={1:2,2:3,3:6}[item['palier']]


def test_banque_actualisation_progressive_et_correction_successive():
    for palier in range(1,4):
        items=[i for i in CONTENU.items('actualiser-consigne') if i['palier']==palier]
        assert len(items)==12
        assert all(len(i['contenu']['champs'])==palier+1 for i in items)
    for item in (i for i in CONTENU.items('actualiser-consigne') if i['palier']==3):
        c=item['contenu']; mises=[e for e in c['etapes'] if e['evenement']=='mise_a_jour']
        assert len({e['champ'] for e in mises})<len(mises),item['id']
        assert any(item['reponse']['valeur'][k]==v for k,v in c['etat_initial'].items()),item['id']
        assert sum(e['evenement']=='autre_tache' for e in c['etapes'])==1


def test_ecarts_recalculables_et_cas_entierement_conformes():
    for item in CONTENU.items('comparer-documents'):
        a,b=[{l['id']:l['texte'] for l in d['lignes']} for d in item['contenu']['documents']]
        calcule={k:'conforme' if a[k]==b[k] else 'ecart' for k in a}
        assert calcule==item['reponse']['valeur']
        assert len(a)==2*item['palier']
    assert sum(all(v=='conforme' for v in i['reponse']['valeur'].values())
               for i in CONTENU.items('comparer-documents'))==9


def test_banque_comparaison_varie_nombre_ecarts_et_contextes():
    for palier in range(1,4):
        items=[i for i in CONTENU.items('comparer-documents') if i['palier']==palier]
        assert len(items)==12
        assert len({i['contenu']['enonce'] for i in items})==12
        comptes={sum(v=='ecart' for v in i['reponse']['valeur'].values()) for i in items}
        assert 0 in comptes and max(comptes)==palier


def test_selection_omissions_et_fausses_selections_separees():
    for item in CONTENU.items('reperer-essentiel'):
        attendu=item['reponse']['valeur']
        assert set(attendu.values())=={'oui','non'},item['id']
        _,detail=corriger_detail(item,{k:'non' for k in attendu})
        assert detail['omissions']==sum(v=='oui' for v in attendu.values())
        assert detail['fausses_selections']==0
        _,detail=corriger_detail(item,{k:'oui' for k in attendu})
        assert detail['omissions']==0
        assert detail['fausses_selections']==sum(v=='non' for v in attendu.values())


def test_filtrage_sans_distracteur_auto_revelateur_et_nombre_variable():
    interdits=('sans modification','aucun changement','ne change rien','reste identique','toujours prévu')
    for palier in range(1,4):
        items=[i for i in CONTENU.items('reperer-essentiel') if i['palier']==palier]
        assert len(items)==12
        for item in items:
            textes=' '.join(m['texte'].lower() for m in item['contenu']['messages'])
            assert not any(mot in textes for mot in interdits),item['id']
        comptes={sum(v=='oui' for v in i['reponse']['valeur'].values()) for i in items}
        assert comptes==({1} if palier==1 else ({1,2} if palier==2 else {2,3}))


def test_listes_modalites_rythme_et_absence_de_doublons_exacts():
    vus=set()
    for theme,modalite in [('rappel-series','visuelle'),('series-entendues','auditive')]:
        for item in CONTENU.items(theme):
            a=item['contenu']['affichage']
            assert a['modalite']==modalite
            assert a['duree_par_item_ms']==2000 and a['pause_item_ms']==2000
            serie=tuple(tuple(s) for s in a['series'])
            assert serie not in vus;vus.add(serie)
            assert corriger(theme,item,' '.join(item['reponse']['valeur']))


def test_stockages_des_parcours_independants(client,tmp_path):
    session=client.post('/api/entrainement/series-entendues/sessions').json()
    item=session['items'][0]
    client.post(f"/api/entrainement/series-entendues/sessions/{session['session_id']}/reponses",json={
      'item_id':item['id'],'reponse':' '.join(CONTENU.item('series-entendues',item['id'])['reponse']['valeur']),'temps_ms':3000})
    client.post(f"/api/entrainement/series-entendues/sessions/{session['session_id']}/fin")
    assert (tmp_path/'data/series-entendues/cartes-fsrs.json').exists()
    assert not (tmp_path/'data/rappel-series/cartes-fsrs.json').exists()


def test_audio_mutualise_compact_et_tous_les_fichiers_existent():
    manifest=json.loads((ROOT/'frontend/audio/series/fr-thomas-155-v1/manifest.json').read_text())
    assert len(manifest['mots'])==48
    assert sum(m['octets'] for m in manifest['mots'].values())<1_000_000
    urls=set()
    for item in CONTENU.items('series-entendues'):
        a=item['contenu']['affichage']
        mots={mot for serie in a['series'] for mot in serie}
        assert set(a['audio'])==mots
        for mot,url in a['audio'].items():
            urls.add(url)
            chemin=ROOT/'frontend'/url.removeprefix('/ui/')
            data=chemin.read_bytes()
            assert data[4:8]==b'ftyp'
            assert len(data)==manifest['mots'][mot]['octets']
            assert 0.1<manifest['mots'][mot]['duree_s']<5
    assert len(urls)<=48


def test_audio_cache_immuable_scripts_non_caches(tmp_path):
    from fastapi.testclient import TestClient
    from backend.app.main import creer_app
    client=TestClient(creer_app(racine_donnees=tmp_path,dossier_frontend=ROOT/'frontend'))
    url=next(iter(CONTENU.items('series-entendues')[0]['contenu']['affichage']['audio'].values()))
    r=client.get(url)
    assert r.status_code==200
    assert 'immutable' in r.headers['cache-control']
    assert 'no-store' in client.get('/ui/src/app.js').headers['cache-control']
