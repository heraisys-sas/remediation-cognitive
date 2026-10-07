"""Le délai de feedback lexical ne doit pas sauter une question ultérieure."""
import shutil
import subprocess
from pathlib import Path
from tools.verifier_interface import corps_fonction


def test_suite_lexicale():
    source = (Path(__file__).parents[2] / 'frontend/src/app.js').read_text()
    script = "function programmerSuiteLexicale(resultat, item) " + corps_fonction(source, 'programmerSuiteLexicale')
    script += r'''
const assert=require('node:assert/strict');
let timer,delai,suites=0;
const setTimeout=(f,ms)=>{timer=f;delai=ms;return 1};
const itemSuivant=()=>suites++;
const etat={theme:{id:'evocation'},session:{},indexItem:0,repondu:true,actionEnCours:false,minuteriesMemo:[]};
const item={type:'rappel-indice'};
programmerSuiteLexicale({correcte:false},item);assert.equal(timer,undefined);
programmerSuiteLexicale({correcte:true},{type:'analyse-mot'});assert.equal(timer,undefined);
etat.theme.id='calcul-mental';programmerSuiteLexicale({correcte:true},item);assert.equal(timer,undefined);
etat.theme.id='evocation';programmerSuiteLexicale({correcte:true},item);
assert.equal(delai,3000);assert.deepEqual(etat.minuteriesMemo,[1]);timer();assert.equal(suites,1);
etat.indexItem++;timer();assert.equal(suites,1);
etat.indexItem=0;etat.session={};timer();assert.equal(suites,1);
programmerSuiteLexicale({correcte:true},item);etat.actionEnCours=true;timer();assert.equal(suites,1);
'''
    subprocess.run([shutil.which('node'), '-e', script], check=True)
    assert 'programmerSuiteLexicale(resultat, item);' in corps_fonction(source, 'soumettreValeur')
    assert 'clearTimeout(minuterie)' in corps_fonction(source, 'annulerMemo')
