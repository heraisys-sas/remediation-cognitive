import copy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from backend.app.domain.contenu import ChargeurContenu
from backend.app.domain.correction.sequence import (
    ETAPES_PQRST, corriger_sequence, normaliser_observation_pqrst,
)
from backend.app.domain.messages import PQRST_INTERFACE

ROOT = Path(__file__).parents[2]
ITEM = ChargeurContenu().item("methodes", "mt2-6-pqrst-01")
ETAPES = {e["etape"]: e for e in ITEM["contenu"]["etapes"]}


def payload():
    reponse = {"1": ETAPES[1]["bonne"], "2": "Que retenir ?", "4": ETAPES[4]["modele"],
               "5": [q["bonne"] for q in ETAPES[5]["questions"]]}
    reponse["_pqrst"] = {
        "version": "pqrst-sequence-v1", "etapes_realisees": list(ETAPES_PQRST),
        "phase": "fin", "modele_avant_test": True, "reprise_apres_correction": False,
        "statuts": dict.fromkeys(("1", "2", "4", "5.0", "5.1"), "reponse"),
        "tentatives": {k: [{"reponse": reponse["4"] if k == "4" else reponse["5"][int(k[-1])],
                            "condition": "sans_relecture", "modalite": "clavier" if k == "4" else "choix"}]
                        for k in ("4", "5.0", "5.1")},
        "relectures": [], "interruptions": {},
    }
    return reponse


def test_premiere_reformulation_preservee_apres_aide_correcte():
    r = payload()
    r["4"] = "Le colis."
    m = r["_pqrst"]
    m["tentatives"]["4"][0]["reponse"] = r["4"]
    m["tentatives"]["4"].append({"reponse": ETAPES[4]["modele"], "condition": "apres_relecture", "modalite": "clavier"})
    m["relectures"] = ["4"]
    avant = copy.deepcopy(r)
    correcte, detail = corriger_sequence(ITEM, r)
    assert not correcte
    essais = detail["observation"]["tentatives"]["4"]
    assert essais[0]["correction"]["etat"] == "a_verifier"
    assert essais[1]["correction"]["correcte"] is True
    assert r == avant


def test_absence_declaree_non_notee_question_et_distincte_reformulation():
    r = payload()
    r["2"] = r["4"] = r["5"][0] = None
    for k in ("2", "4", "5.0"):
        r["_pqrst"]["statuts"][k] = "absence_declaree"
        if k != "2":
            r["_pqrst"]["tentatives"][k][0]["reponse"] = None
    _, detail = corriger_sequence(ITEM, r)
    assert detail["2"]["non_notee"]
    for k in ("4", "5.0"):
        assert detail["observation"]["tentatives"][k][0]["correction"]["etat"] == "absence_declaree"


def test_checkpoint_partiel_ne_produit_pas_de_correction():
    r = payload()
    r.pop("4")
    r["5"] = []
    m = r["_pqrst"]
    m.update(etapes_realisees=["P", "Q", "R"], phase="4", modele_avant_test=False,
             statuts={"1": "reponse", "2": "reponse"}, tentatives={})
    observation = normaliser_observation_pqrst(ITEM, r)
    assert observation["statut"] == "partielle"
    assert observation["tentatives"] == {}
    assert observation["question"] == r["2"]
    assert "correcte" not in observation
    with pytest.raises(ValueError):
        corriger_sequence(ITEM, r)


@pytest.mark.parametrize("modifier", [
    lambda r: r["_pqrst"].update(version="inconnue"),
    lambda r: r["_pqrst"].update(modele_avant_test=False),
    lambda r: r["_pqrst"].update(phase=[]),
    lambda r: r["_pqrst"]["statuts"].update({"4": "absence_declaree"}),
    lambda r: r["_pqrst"]["tentatives"]["4"][0].update(reponse="autre première réponse"),
    lambda r: r["_pqrst"]["tentatives"]["4"].append(copy.deepcopy(r["_pqrst"]["tentatives"]["4"][0])),
    lambda r: r["_pqrst"]["relectures"].extend(["4", "4"]),
    lambda r: r["_pqrst"]["interruptions"].update({"4": True}),
    lambda r: r["_pqrst"]["interruptions"].update({"4": 10001}),
    lambda r: r["_pqrst"]["tentatives"]["5.0"][0].update(condition="reprise_interrompue"),
    lambda r: r["_pqrst"]["tentatives"]["5.0"][0].update(modalite="dictée"),
    lambda r: r["5"].append("réponse supplémentaire"),
    lambda r: r.update({"2": "a" * 2001}),
    lambda r: r["_pqrst"].update(secret="champ non prévu"),
])
def test_trace_incoherente_ou_hors_bornes_refusee(modifier):
    r = payload()
    modifier(r)
    with pytest.raises(ValueError):
        normaliser_observation_pqrst(ITEM, r)


def test_payload_historique_ne_devient_pas_protocole_masque():
    r = payload()
    del r["_pqrst"]
    correcte, detail = corriger_sequence(ITEM, r)
    assert correcte
    assert "observation" not in detail


DOM = r'''
const assert = require('node:assert/strict');
class Element {
  constructor(tag) { this.tag=tag; this.children=[]; this.attributes={}; this.hidden=false;
    this.value=''; this.disabled=false; this.text=''; this.events={};
    this.classList={add(){},remove(){}}; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children=nodes; this.text=''; }
  setAttribute(k,v) { this.attributes[k]=v; }
  addEventListener(k,fn) { this.events[k]=fn; }
  focus() {}
  get textContent() { return this.text+this.children.map(n=>n.textContent).join(' '); }
  set textContent(v) { this.text=v; this.children=[]; }
  querySelectorAll(selector) {
    const tags=selector.split(',').map(s=>s.trim());
    return this.children.flatMap(n=>[...(tags.includes(n.tag)?[n]:[]),...n.querySelectorAll(selector)]);
  }
  querySelector(s) { return this.querySelectorAll(s)[0]||null; }
}
const listeners=new Map();
const document={hidden:false,addEventListener(k,f){listeners.set(k,f)},removeEventListener(k){listeners.delete(k)}};
function creerElement(tag,attrs={},...children) {
 const n=new Element(tag);n.text=attrs.texte||'';n.className=attrs.classe||'';
 Object.assign(n.attributes,attrs.attributs||{});n.append(...children);return n;
}
const refs=Object.fromEntries(['zoneSequence','formulaire','zoneChoix','zoneIndices','zoneGeneration','zoneAide',
 'panneauMethode','enonce','rappelConsigne','texteAide','methodeExercice','noteReprise','ligneAudio','carteFeedback']
 .map(k=>[k,new Element('div')]));
refs.vues={seance:{hidden:false}};
const etat={actionEnCours:false,repondu:false,indexItem:0,reponsesAttendues:{}};
let stops=0,submitted=null;
const CAPACITES={arreter(){stops++},syntheseDisponible(){return true}};
function soumettreValeur(v){submitted=JSON.parse(JSON.stringify(v));}
function click(label){const b=refs.zoneSequence.querySelectorAll('button').find(n=>n.textContent===label&&!n.hidden);
 assert.ok(b,`Missing button ${label}`);assert.ok(!b.disabled,`Disabled ${label}`);b.events.click();}
function type(value){const field=refs.zoneSequence.querySelector('textarea');assert.ok(field);field.value=value;field.events.input();}
function noLeak(text){for(const n of Object.values(refs))if(n instanceof Element)assert.ok(!n.textContent.includes(text),text);
 assert.ok(!etat.enonceCourant.includes(text));}
'''


def render_flow(actions):
    item = copy.deepcopy(ITEM)
    item["contenu"]["interface_pqrst"] = PQRST_INTERFACE
    code = DOM + (ROOT / "frontend/src/exercises/sequence.js").read_text()
    code += "\nconst item=" + json.dumps(item) + ";etat.session={items:[item]};"
    code += "const e=Object.fromEntries(item.contenu.etapes.map(e=>[e.etape,e]));const ui=item.contenu.interface_pqrst;"
    code += "rendreSequence(item);" + actions
    result = subprocess.run([shutil.which("node"), "-"], input=code, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


START = r'''
noLeak(item.contenu.texte);click(ui.commencer);
assert.ok(refs.zoneSequence.textContent.includes(item.contenu.titre_texte));
assert.ok(!refs.zoneSequence.textContent.includes(item.contenu.texte));
click(e[1].bonne);click(ui.valider);click(ui.continuer);
type('QUESTION PERSONNELLE DISTINCTE');click(ui.valider);click(ui.vers_lecture);
assert.ok(etat.enonceCourant.includes(item.contenu.texte));
const avant=stops;click(ui.vers_reformulation);assert.ok(stops>avant);
noLeak(item.contenu.texte);noLeak('QUESTION PERSONNELLE DISTINCTE');
'''


def test_interface_sequentielle_masque_audio_et_preserve_essai_aide():
    r = render_flow(START + r'''
type('Le colis.');click(ui.relire);assert.equal(etat.sequence['4'],'Le colis.');
click(ui.pause);noLeak(item.contenu.texte);click(ui.reprendre);click(ui.fin_relecture);
noLeak(item.contenu.texte);type(e[4].modele);click(ui.valider);
assert.ok(refs.zoneSequence.textContent.includes(e[4].modele));
click(ui.vers_test);noLeak(e[4].modele);noLeak(item.contenu.texte);
assert.ok(!refs.zoneSequence.textContent.includes(e[5].questions[1].enonce));
click(e[5].questions[0].bonne);click(ui.valider);
assert.ok(!refs.zoneSequence.textContent.includes(e[5].questions[0].bonne));
click(e[5].questions[1].bonne);click(ui.valider);
assert.equal(submitted,null);click(ui.envoyer);
console.log(JSON.stringify(submitted));
''')
    correcte, detail = corriger_sequence(ITEM, r)
    assert not correcte
    obs = detail["observation"]
    assert obs["modele_avant_test"] is True
    assert obs["tentatives"]["4"][1]["condition"] == "reprise_interrompue"
    assert obs["tentatives"]["4"][1]["correction"]["correcte"]


def test_interface_absences_aide_t1_reste_visible_t2_et_checkpoint():
    r = render_flow(START + r'''
click(ui.sans_reponse);click(ui.vers_test);click(ui.absence_relire);
click(ui.fin_relecture);click(e[5].questions[0].bonne);click(ui.valider);
assert.ok(refs.zoneSequence.textContent.includes(ui.aidee));
document.hidden=true;listeners.get('visibilitychange')();noLeak(item.contenu.texte);
const checkpoint=snapshotPqrst();assert.equal(checkpoint['5'].length,1);
nettoyerSequence();assert.equal(snapshotPqrst(),null);assert.equal(listeners.size,0);
console.log(JSON.stringify(checkpoint));
''')
    obs = normaliser_observation_pqrst(ITEM, r)
    assert obs["statuts"]["4"] == "absence_declaree"
    assert obs["statuts"]["5.0"] == "absence_declaree"
    assert obs["tentatives"]["5.0"][1]["reponse"] == ETAPES[5]["questions"][0]["bonne"]
    assert "5.1" not in obs["tentatives"]
