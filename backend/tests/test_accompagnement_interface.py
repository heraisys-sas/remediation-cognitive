"""Vérifie les limites du dialogue facultatif, sans moteur de notation."""
import shutil
import subprocess
from pathlib import Path


def test_relances_bornees_et_erreur_recuperable():
    source = (Path(__file__).parents[2] / 'frontend/src/accompagnement.js').read_text()
    script = r'''
const assert = require('node:assert/strict');
const document = {createElement(tag) { return {tag, children: [], value: '', isConnected: true,
  append(...nodes) {this.children.push(...nodes)}, setAttribute() {},
  addEventListener(event, fn) {this[event] = fn}
}; }};
let appels = 0;
let panne = true;
async function fetch(url, options) {
  appels++;
  assert.equal(url, '/api/capacites/accompagnement');
  const body = JSON.parse(options.body);
  assert.deepEqual(Object.keys(body).sort(), ['categories_deja_vues', 'question', 'reformulation', 'texte']);
  assert.equal(body.question, 'Pourquoi ?');
  if (panne) throw new Error('test');
  return {ok:true,json:async()=>({disponible:true,relance:'Que vérifier ?'})};
}
''' + source + r'''
(async () => {
 const zone = creerAccompagnementPqrst('Texte', 'Mon résumé', 'Pourquoi ?');
 const bouton = zone.children[3];
 await bouton.click();
 assert.equal(bouton.disabled, false);
 panne = false;
 await Promise.all([bouton.click(), bouton.click()]);
 assert.equal(appels, 2); // un échec + une relance, pas de double clic
 await bouton.click();
 assert.equal(bouton.disabled, true);
 await bouton.click();
 assert.equal(appels, 3);
 const vide = creerAccompagnementPqrst('Texte', '');
 assert.equal(vide.children[3].disabled, true);
})().catch(e => {console.error(e);process.exitCode = 1});
'''
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)


def test_retour_pqrst_visible_et_accompagnement_apres_correction():
    from tools.verifier_interface import corps_fonction
    source = (Path(__file__).parents[2] / 'frontend/src/app.js').read_text()
    body = corps_fonction(source, 'rendreFeedback')
    script = "const assert=require('node:assert/strict');" + r"""
const etat={theme:{id:'methodes'}, session:{items:[{type:'pqrst-mise-en-oeuvre',contenu:{texte:'Texte'}}]},indexItem:0,sequence:{'4':'Résumé','2':'Pourquoi ?'}};
const refs={carteFeedback:{hidden:true,append(node){this.node=node}}};
let corrige=false;
function rendreFeedbackSequence(){corrige=true;}
function creerAccompagnementPqrst(texte,reponse,question){assert.equal(question, "Pourquoi ?");assert.ok(corrige);assert.equal(reponse,'Résumé');return 'accompagnement'}
""" + 'function rendreFeedback(resultat) ' + body + r"""
rendreFeedback({sequence:{}});
assert.equal(refs.carteFeedback.hidden,false);
assert.equal(refs.carteFeedback.node,'accompagnement');
"""
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)


def test_bilan_affiche_question_personnelle_et_modele_separement():
    from tools.verifier_interface import corps_fonction
    source = (Path(__file__).parents[2] / 'frontend/src/app.js').read_text()
    script = r"""
const assert=require('node:assert/strict');
const etat={sequence:{'2':'Pourquoi une lessive à vide ?'}};
const refs={carteFeedback:{children:[],replaceChildren(){this.children=[]},append(x){this.children.push(x)}}};
function creerElement(tag, options){return options}
""" + 'function rendreFeedbackSequence(resultat) ' + corps_fonction(source, 'rendreFeedbackSequence') + r"""
rendreFeedbackSequence({sequence:{'2':{modele:'Que faire avant ?'}}});
const ligne=refs.carteFeedback.children.find(x=>x.texte.startsWith('2. Ta question'));
assert.ok(ligne.texte.includes('Pourquoi une lessive à vide ?'));
assert.ok(ligne.texte.includes('sans score. Autre question possible : « Que faire avant ? »'));
"""
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)


def test_sequence_pqrst_ne_reaffiche_pas_saisie_generique():
    from tools.verifier_interface import corps_fonction
    source = (Path(__file__).parents[2] / 'frontend/src/app.js').read_text()
    script = r"""
const assert=require('node:assert/strict');
const refs = Object.fromEntries(['boutonDicter','ligneAudio','enonce','rappelConsigne','texteAide','zoneAide','formulaire','carteFeedback','boutonSuivant'].map(k=>[k,{hidden:false}]));
const etat={consignesVues:new Set()};
const CAPACITES={arreter(){},syntheseDisponible(){return true}};
function annulerMemo(){} function viderZonesReponse(){} function lireSiLectureAuto(){}
function aideGeneriquePourItem(){return null} function reglerEtatBoutons(){}
let sequenceAffichee=false;
function rendreSequence(){sequenceAffichee=true;refs.formulaire.hidden=true;}
""" + 'function afficherQuestion(item) ' + corps_fonction(source, 'afficherQuestion') + r"""
afficherQuestion({type:'pqrst-mise-en-oeuvre',contenu:{enonce:'PQRST'}});
assert.ok(sequenceAffichee);
assert.equal(refs.formulaire.hidden,true);
assert.equal(refs.boutonDicter.hidden,true);
assert.equal(refs.carteFeedback.hidden,true);
assert.equal(refs.boutonSuivant.hidden,true);
assert.ok(etat.debutQuestion>0);
"""
    subprocess.run([shutil.which('node'), '-e', script], check=True, capture_output=True, text=True)
