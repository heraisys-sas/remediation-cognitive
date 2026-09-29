"""Progression réelle : accès aux nouveautés et maîtrise des dernières étapes."""
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.app.main import creer_app
from backend.app.domain.selection import selectionner_items
from engine.srs.fsrs import CarteFSRS, planifier


def test_revisions_faciles_ne_masquent_pas_les_nouvelles_etapes():
    now = datetime(2026,9,29,tzinfo=timezone.utc)
    items = [dict(id=str(i),palier=2,contenu={'etape_progression':1 if i<6 else 2}) for i in range(12)]
    cartes={str(i):planifier(CarteFSRS(str(i)),3,now-timedelta(days=7))[0] for i in range(6)}
    selection=selectionner_items(items,cartes,2,now,6)
    assert len(selection)==6
    assert [i['id'] for i in selection[3:]]==['6','7','8']
    assert len({i['id'] for i in selection})==6


def test_palier_ne_valide_pas_sur_les_seules_etapes_faciles(tmp_path):
    now=[datetime(2026,9,29,tzinfo=timezone.utc)]
    app=creer_app(racine_donnees=tmp_path/'data',horloge=lambda:now[0])
    client=TestClient(app)
    gestion=app.state.gestionnaire_entrainement
    # Historique parfait de l'ancien corpus : il ne doit pas permettre de
    # sauter les dernières étapes des nouvelles grilles.
    gestion.stockage.ecrire_maitrise('deduction',1,[(2,1.0),(2,1.0),(2,1.0)])
    eligibles=0
    for jour in range(9):
        now[0]+=timedelta(days=1)
        session=client.post('/api/entrainement/deduction/sessions',json={'palier':2}).json()
        finales=False
        for item in session['items']:
            finales |= item['contenu']['etape_progression']==3
            reponse=gestion.contenu.item('deduction',item['id'])['reponse']['valeur']
            result=client.post(f"/api/entrainement/deduction/sessions/{session['session_id']}/reponses",
                               json={'item_id':item['id'],'reponse':reponse,'temps_ms':2000})
            assert result.status_code==200
        client.post(f"/api/entrainement/deduction/sessions/{session['session_id']}/fin")
        eligibles+=finales
        maitrise=gestion.stockage.lire_maitrise('deduction')
        if eligibles<3:
            assert maitrise['palier_courant']==1
        else:
            assert maitrise['palier_courant']==3
            assert len(maitrise['historique_etapes'])==3
            assert maitrise['historique'][:3]==[(2,1.0)]*3
            break
    assert eligibles>=3, 'les dernières étapes doivent devenir accessibles malgré les révisions dues'
