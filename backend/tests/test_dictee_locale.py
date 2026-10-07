"""Aucune reconnaissance distante, y compris en cas d'absence du pack français."""
from pathlib import Path
import shutil
import subprocess


def test_dictee_ne_demarre_que_si_locale_disponible():
    source = (Path(__file__).parents[2] / 'frontend/src/capacites.js').read_text()
    for cas in ('absent', 'ancien', 'pack_absent', 'erreur', 'local'):
        script = r'''
const assert=require('node:assert/strict');
const localStorage={getItem(){return null}};
let starts=0,errors=0;
class Speech {
 constructor(){if(CAS!=='ancien')this.processLocally=false;}
 start(){assert.equal(this.processLocally,true);starts++;}
 abort(){} stop(){}
 static async available(options){
 assert.deepEqual(options,{langs:['fr-FR'],processLocally:true});
 if(CAS==='erreur')throw Error('indisponible');
 return CAS==='pack_absent'?'downloadable':'available';
 }
}
const window={SpeechRecognition:CAS==='absent'?null:Speech};
''' .replace('CAS', repr(cas)) + source + r'''
(async()=>{
Capacites.dicter({onErreur(){errors++}});
await new Promise(resolve=>setImmediate(resolve));
assert.equal(starts, EXPECTED);
assert.equal(errors, 1-EXPECTED);
})().catch(e=>{console.error(e);process.exitCode=1});
'''.replace('EXPECTED', '1' if cas == 'local' else '0')
        subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)
