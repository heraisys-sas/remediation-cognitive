"""Dialogue facultatif : contexte exact, deux échanges, aucune note modifiée."""
from pathlib import Path
import shutil
import subprocess


def test_dialogue_borne_erreurs_et_resultat_obsolete():
    source = (Path(__file__).parents[2] / 'frontend/src/approfondir-documents.js').read_text()
    script = r'''
const assert=require('node:assert/strict');
const document={createElement(tag){return {tag,value:'',children:[],isConnected:true,
 append(...xs){this.children.push(...xs)},setAttribute(){},focus(){},
 addEventListener(event,fn){this[event]=fn}
}}};
let fail=true, lastBody, appels=0, detach=null;
async function fetch(url, options){
 assert.equal(url,'/api/capacites/accompagnement-documents');
 lastBody=JSON.parse(options.body); appels++;
 if(fail) throw Error('test');
 if(detach) detach.isConnected=false;
 return {ok:true,json:async()=>({disponible:true,relance:'Quelle conséquence pour le jour ?'})};
}
''' + source + r'''
(async()=>{
const initial={jour:'ecart'};
const zone=creerApprofondissementDocuments('item',initial);
initial.jour='conforme'; // capture immutable des choix soumis
const champ=zone.children[3].children[0], bouton=zone.children[4];
assert.equal(bouton.disabled,true);
champ.value='Les jours diffèrent';champ.input();
await bouton.click();
assert.equal(bouton.disabled,false);assert.equal(champ.value,'Les jours diffèrent');
fail=false;
await Promise.all([bouton.click(),bouton.click()]);
assert.equal(appels,2);assert.deepEqual(lastBody.reponses,{jour:'ecart'});
assert.deepEqual(lastBody.echanges,[]);
assert.equal(champ.value,'');
champ.value='Je ferais confirmer la date';champ.input();
await bouton.click();
assert.equal(lastBody.echanges.length,1);
assert.equal(lastBody.echanges[0].justification,'Les jours diffèrent');
assert.equal(bouton.hidden,true);
await bouton.click();assert.equal(appels,3);
const obsolete=creerApprofondissementDocuments('autre',{});
detach=obsolete;
const input=obsolete.children[3].children[0];input.value='réflexion';
await obsolete.children[4].click();
assert.equal(obsolete.children[2].children.length,0);
})().catch(e=>{console.error(e);process.exitCode=1});
'''
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)


def test_approfondissement_recoit_item_et_choix_apres_correction():
    from tools.verifier_interface import corps_fonction
    source = (Path(__file__).parents[2] / 'frontend/src/app.js').read_text()
    script = r'''
const assert=require('node:assert/strict');
const refs={carteFeedback:{append(x){this.children.push(x)},replaceChildren(...xs){this.children=xs}}};
const etat={theme:{id:'comparer-documents'},session:{items:[{id:'doc1',type:'comparer-documents'}]},indexItem:0};
function creerElement(tag,opts){return opts}
function creerApprofondissementDocuments(id,reponse){assert.equal(id,'doc1');assert.deepEqual(reponse,{jour:'ecart'});return {dialogue:true};}
''' + 'function rendreFeedback(resultat,reponseInitiale) ' + corps_fonction(source, 'rendreFeedback') + r'''
rendreFeedback({detail_fonctionnel:{type:'comparer-documents',lignes:[]},correcte:true},{jour:'ecart'});
assert.equal(refs.carteFeedback.hidden,false);
assert.ok(refs.carteFeedback.children.at(-1).dialogue);
'''
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)
