"""Encodage local et annulation avant ouverture du micro."""
from tools.verifier_interface import source_interface
from pathlib import Path
import shutil
import subprocess


def test_wav_et_annulation():
    source=(Path(__file__).parents[2]/'frontend/src/dictee-native.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
const location={hostname:'127.0.0.1'};
const window={AudioContext:class{}};
let micros=0, resolveMicro, liberes=0;
const navigator={mediaDevices:{getUserMedia(){micros++;return new Promise(r=>{resolveMicro=r})}}};
const fetch=()=>{throw Error('pas de réseau avant la capture')};
''' + source + r'''
(async()=>{
assert.equal(DicteeNative.disponible(),true);
location.hostname='example.org';assert.equal(DicteeNative.disponible(),false);
location.hostname='127.0.0.1';
const bytes=DicteeNative.wav([new Float32Array(48000).fill(.5)],48000);
const vue=new DataView(bytes.buffer);
assert.equal(vue.getUint32(24,true),16000);
assert.equal(vue.getUint32(40,true),32000);
assert.equal(vue.getInt16(44,true),16383);
let erreurs=0;
const control=DicteeNative.demarrer({onErreur(){erreurs++}});
control.abort();
resolveMicro({getTracks(){return [{stop(){liberes++}}]}});
await new Promise(r=>setImmediate(r));
assert.equal(micros,1);assert.equal(liberes,1);assert.equal(erreurs,0);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)


def test_capture_stop_et_transcription_loopback():
    source=(Path(__file__).parents[2]/'frontend/src/dictee-native.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
const location={hostname:'localhost'};
let processor,tracksStopped=0,texte='';
class AudioContext {
 constructor(){this.sampleRate=48000;this.state='running';this.destination={};}
 async resume(){} async close(){this.state='closed'}
 createMediaStreamSource(){return {connect(){},disconnect(){}}}
 createScriptProcessor(){processor={connect(){},disconnect(){}};return processor;}
}
const window={AudioContext};
const navigator={mediaDevices:{async getUserMedia(){return {getTracks(){return [{stop(){tracksStopped++}}]}}}}};
let calls=0;
async function fetch(url,options={}){
 assert.equal(url,'/api/capacites/dictee');calls++;
 if(options.method==='POST'){
 const audio=Buffer.from(JSON.parse(options.body).audio_base64,'base64');
 assert.equal(audio.toString('ascii',0,4),'RIFF');
 return {ok:true,json:async()=>({disponible:true,texte:'la gare'})};
 }
 return {ok:true,json:async()=>({disponible:true})};
}
''' + source + r'''
(async()=>{
let fin=0,pret=0;
const control=DicteeNative.demarrer({onDebut(){pret++},onResultat(t){texte=t},onFin(){fin++}});
await new Promise(r=>setImmediate(r));
assert.equal(pret,0);
processor.onaudioprocess({inputBuffer:{getChannelData(){return new Float32Array(4800).fill(.1)}}});
assert.equal(pret,1);
await control.stop();
assert.equal(texte,'la gare');assert.equal(fin,1);assert.equal(tracksStopped,1);assert.equal(calls,1);
await control.stop();assert.equal(calls,1);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)


def test_apercus_corriges_sans_attendre_arret_et_sans_requetes_concurrentes():
    source=(Path(__file__).parents[2]/'frontend/src/dictee-native.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
const location={hostname:'localhost'};
let processor,tick,resolvePost,posts=0;
const setInterval=(f,ms)=>{assert.equal(ms,600);tick=f;return 1},clearInterval=()=>{};
class AudioContext {
 constructor(){this.sampleRate=48000;this.state='running';this.destination={}}
 async resume(){} async close(){this.state='closed'}
 createMediaStreamSource(){return {connect(){},disconnect(){}}}
 createScriptProcessor(){processor={connect(){},disconnect(){}};return processor}
}
const window={AudioContext};
const navigator={mediaDevices:{async getUserMedia(){return {getTracks(){return [{stop(){}}]}}}}};
async function fetch(url,options={}){
 if(!options.method)return {ok:true,json:async()=>({disponible:true})};
 posts++;
 return new Promise(resolve=>{resolvePost=t=>resolve({ok:true,json:async()=>({disponible:true,texte:t})})});
}
''' + source + r'''
(async()=>{
let visible='',fini=false;
const control=DicteeNative.demarrer({onPartiel(t){visible=t},onResultat(t){visible=t},onFin(){fini=true}});
const flush=()=>new Promise(r=>setImmediate(r));
await flush();
const audio=()=>processor.onaudioprocess({inputBuffer:{getChannelData(){return new Float32Array(4800).fill(.1)}}});
audio();tick();tick();assert.equal(posts,1);
resolvePost('le ver');await flush();
assert.equal(visible,'le ver');assert.equal(fini,false);
audio();tick();resolvePost('le verre est plein');await flush();
assert.equal(visible,'le verre est plein');assert.equal(fini,false);
await control.stop();assert.equal(fini,true);assert.equal(posts,2);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)


def test_micro_prepare_ne_conserve_pas_la_question_et_garde_la_premiere_reponse():
    source=(Path(__file__).parents[2]/'frontend/src/dictee-native.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
const location={hostname:'localhost'};
let processor,tick,posts=0,ready=0,stopped=0;
const setInterval=f=>{tick=f;return 1},clearInterval=()=>{};
class AudioContext {
 constructor(){this.sampleRate=16000;this.state='running';this.destination={}}
 async resume(){} async close(){this.state='closed'}
 createMediaStreamSource(){return {connect(){},disconnect(){}}}
 createScriptProcessor(){processor={connect(){},disconnect(){}};return processor}
}
const window={AudioContext};
const navigator={mediaDevices:{async getUserMedia(){return {getTracks(){return [{stop(){stopped++}}]}}}}};
async function fetch(url,options){
 posts++;
 const audio=Buffer.from(JSON.parse(options.body).audio_base64,'base64');
 assert.equal(audio.readUInt32LE(40),3200);
 assert.equal(audio.readInt16LE(44),3276); // La réponse .1, pas la consigne .8.
 return {ok:true,json:async()=>({disponible:true,texte:'gare'})};
}
''' + source + r'''
(async()=>{
 const c=DicteeNative.demarrer({enAttente:true,onDebut(){ready++}});
 const flush=()=>new Promise(r=>setImmediate(r));await flush();
 const audio=value=>processor.onaudioprocess({inputBuffer:{getChannelData(){return new Float32Array(1600).fill(value)}}});
 audio(.8);tick();await flush();assert.equal(posts,0);assert.equal(ready,0);
 c.activer();audio(.1);assert.equal(ready,1);await c.stop();assert.equal(posts,1);assert.equal(stopped,1);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)


def test_autorisation_avant_question_et_reutilisation_du_micro():
    source=(Path(__file__).parents[2]/'frontend/src/dictee-native.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
const location={hostname:'localhost'};
let demandes=0,arrets=0,refus=false;
class AudioContext {
 constructor(){this.state='running';this.destination={};this.sampleRate=16000}
 async resume(){} async close(){this.state='closed'}
 createMediaStreamSource(){return {connect(){},disconnect(){}}}
 createScriptProcessor(){return {connect(){},disconnect(){}}}
}
const window={AudioContext};
const navigator={mediaDevices:{async getUserMedia(){demandes++;if(refus)throw Error('refus');return {getTracks(){return [{stop(){arrets++}}]}}}}};
''' + source + r'''
(async()=>{
 assert.equal(await DicteeNative.autoriser(),true);assert.equal(demandes,1);assert.equal(arrets,0);
 const c=DicteeNative.demarrer({enAttente:true});await new Promise(r=>setImmediate(r));
 assert.equal(demandes,1);c.abort();assert.equal(arrets,1);
 assert.equal(await DicteeNative.autoriser(),true);DicteeNative.libererPreparation();assert.equal(arrets,2);
 refus=true;assert.equal(await DicteeNative.autoriser(),false);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)


def test_autorisation_precede_la_premiere_question():
    from tools.verifier_interface import corps_fonction
    source=source_interface()
    demarrage=corps_fonction(source, 'demarrerSession')
    assert demarrage.index('await CAPACITES.autoriserDictee') < demarrage.index('montrerItem()')
    assert 'etat.dicteeAutoAutorisee = false' in demarrage
    question=corps_fonction(source, 'afficherQuestion')
    assert 'dicteePossible && etat.dicteeAutoAutorisee' in question
