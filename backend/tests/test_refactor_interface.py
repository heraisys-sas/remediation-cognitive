import shutil
import subprocess
from pathlib import Path

from tools.verifier_interface import source_interface

ROOT = Path(__file__).parents[2]


def test_etat_session_reinitialise_sans_perdre_preferences_et_generation():
    source = (ROOT / 'frontend/src/state.js').read_text()
    subprocess.run([shutil.which('node'), '-e', source + r'''
const assert=require('node:assert/strict');
etat.session={session_id:'ancienne'};
etat.grille=['triangle:rouge'];
etat.consignesAudioVues.add('Ancienne consigne');
etat.dicteeAutoAutorisee=true;
etat.sequence={'2':'Question'};
etat.memoGeneration=17;
etat.themesParId.set('deduction',{});
const precedente=etat.seance;
resetSessionState();
assert.notEqual(etat.seance, precedente);
assert.equal(etat.session,null);
assert.equal(etat.grille,null);
assert.equal(etat.consignesAudioVues.size,0);
assert.equal(etat.dicteeAutoAutorisee,false);
assert.deepEqual(etat.sequence,{});
assert.equal(etat.themesParId.size,1);
assert.equal(etat.memoGeneration,17); // les anciens callbacks restent invalidés
'''], check=True, capture_output=True, text=True)


def test_scripts_charges_et_handlers_sans_dom_au_chargement():
    source = source_interface()
    # Initialisation des scripts réellement servis avec un DOM minimal et API locale simulée.
    prefixe = r'''
const assert=require('node:assert/strict');
const node=()=>({hidden:false,value:'',children:[],classList:{add(){},remove(){}},
  addEventListener(){},setAttribute(){},focus(){},append(...x){this.children.push(...x)},
  replaceChildren(...x){this.children=x},querySelector(){return null}});
const nodes=new Map();
const document={getElementById(id){if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)},
  createElement:node,querySelectorAll(){return []},addEventListener(){}};
const fetch=async()=>({ok:true,json:async()=>({themes:[],voix:[],disponible:false})});
const window={matchMedia(){return {matches:true}},scrollTo(){},localStorage:{getItem(){return null}}};
const location={hostname:'localhost'};
const navigator={};
'''
    assertions = r'''
assert.equal(typeof init,'function');
assert.equal(handlerPour({type:'grille-deduction'}),deductionHandler);
assert.equal(handlerPour({type:'pqrst-mise-en-oeuvre'}),sequenceHandler);
assert.equal(handlerPour({type:'actualiser-consigne'}),functionalHandler);
assert.equal(handlerPour({type:'production'}),defaultHandler);
etat.theme={id:'evocation'};
assert.equal(defaultHandler.readAnswer('  un verre  '),'un verre');
const reponse={'2':'Ma question'};
assert.equal(sequenceHandler.readAnswer(reponse),reponse);
'''
    resultat = subprocess.run([shutil.which('node'), '-'],
                              input=prefixe + source + assertions,
                              capture_output=True, text=True)
    assert resultat.returncode == 0, resultat.stderr[-2000:]
