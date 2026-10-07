"""Contrôle des transitions de la dictée automatique sans microphone réel."""
import shutil
import subprocess
from pathlib import Path


def test_dictee_auto_transitions():
    node = shutil.which('node')
    assert node, 'Node requis pour vérifier les transitions de dictée'
    source = (Path(__file__).parents[2] / 'frontend/src/dictee-auto.js').read_text()
    scenario = r'''
const assert = require('node:assert/strict');
let timers = [], lecture, callbacks, opens = 0, aborts = 0;
global.setTimeout = f => { timers.push(f); return f; };
global.clearTimeout = f => { timers = timers.filter(x => x !== f); };
const tick = async () => { const work=timers; timers=[]; work.forEach(f=>f()); await Promise.resolve(); };
let playing = true, shown='', submitted=[], checks=[], keyboard=0, resolve;
const capacites = {
 lectureEnCours:()=>playing,
 observerLecture:f=>{lecture=f;f(playing);return()=>{lecture=null;};},
 dicter:c=>{opens++;callbacks=c;return {abort:()=>aborts++};}
};
const config={capacites, verifier:t=>{checks.push(t);return Promise.resolve({acceptee:t==='un verre'});},
 afficher:t=>shown=t, valider:t=>submitted.push(t), statut:()=>{}, clavier:()=>keyboard++};
(async()=>{
 let c=DicteeAuto.demarrer(config);
 await tick(); assert.equal(opens,0);
 playing=false;lecture(false);await tick();assert.equal(opens,1);
 callbacks.onPartiel('ver');await tick();assert.equal(submitted.length,0);
 callbacks.onPartiel('un verre');await tick();assert.deepEqual(submitted,['un verre']);assert.equal(lecture,null);
 callbacks.onResultat('un verre');await tick();assert.equal(submitted.length,1);
 c=DicteeAuto.demarrer({...config,verifier:()=>new Promise(r=>resolve=r)});
 await tick(); callbacks.onPartiel('un verre');await tick();
 c.manuel();assert.equal(shown,'');assert.equal(keyboard,1);
 resolve({acceptee:true});await Promise.resolve();assert.equal(submitted.length,1);
 callbacks.onPartiel('ancien');assert.equal(shown,'');
 c=DicteeAuto.demarrer(config);c.abort();await tick();assert.equal(opens,2);
 c=DicteeAuto.demarrer(config);await tick();
 playing=true;lecture(true);assert.ok(aborts>=3);
 playing=false;lecture(false);playing=true;lecture(true);await tick();assert.equal(opens,3);
 c.abort();
 let preparations=0,activations=0;
 capacites.preparerDictee=c=>{preparations++;callbacks=c;return {activer:()=>activations++,abort:()=>aborts++};};
 playing=true;c=DicteeAuto.demarrer(config);
 assert.equal(preparations,1);assert.equal(activations,0);
 playing=false;lecture(false);playing=true;lecture(true);await tick();
 assert.equal(preparations,1);assert.equal(activations,0);
 playing=false;lecture(false);await tick();assert.equal(activations,1);
 c.manuel();assert.equal(lecture,null);
})().catch(e=>{console.error(e);process.exitCode=1;});
'''
    subprocess.run([node, '-e', source + '\n' + scenario], check=True)
