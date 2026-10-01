"""Exécute les composants réels avec horloge contrôlée et DOM minimal."""
import json
import shutil
import subprocess
from pathlib import Path
from tools.verifier_interface import corps_fonction
from backend.app.domain.contenu import ChargeurContenu
ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/'frontend/src/app.js').read_text()

BASE=r'''
const assert=require('node:assert/strict');
function creerElement(tag, attrs={}, ...children) {
  return {tag,...attrs,children,hidden:false,
    append(...x){this.children.push(...x)},replaceChildren(...x){this.children=x},
    addEventListener(event,f){this[event]=f},
    set textContent(v){this.texte=v;this.children=[]},get textContent(){return this.texte},
    querySelectorAll(sel){return this.children.filter(n=>'.'+n.classe===sel)},
  };
}
const refs={zoneSequence:creerElement('div'),zoneMemo:creerElement('div'),ligneAudio:{}};
let soumis=null;
function soumettreValeur(v){soumis=v}
function texte(node){return (node.texte||'')+' '+node.children.map(texte).join(' ')}
function nodes(node,tag){return [...(node.tag===tag?[node]:[]),...node.children.flatMap(x=>nodes(x,tag))]}
'''

def execute(script):
    subprocess.run([shutil.which('node'),'-e',script],check=True,capture_output=True,text=True)

def test_actualiser_masque_chaque_message_et_compare_garde_les_documents():
    contenu=ChargeurContenu()
    items=[contenu.items(t)[-1] for t in ('actualiser-consigne','comparer-documents','reperer-essentiel')]
    script=BASE+'\nfunction rendreFonctionnel(item) '+corps_fonction(SOURCE,'rendreFonctionnel')
    script+='\nconst items='+json.dumps(items)+r''';
let item=items[0]; rendreFonctionnel(item);
for(let i=0;i<item.contenu.etapes.length;i++) {
  assert.ok(texte(refs.zoneSequence).includes(item.contenu.etapes[i].texte));
  nodes(refs.zoneSequence,'button')[0].click();
}
for(const etape of item.contenu.etapes) assert.ok(!texte(refs.zoneSequence).includes(etape.texte));
const inputs=nodes(refs.zoneSequence,'input');
inputs.forEach((input,i)=>{input.value=Object.values(item.reponse.valeur)[i];input.input()});
assert.equal(nodes(refs.zoneSequence,'button').at(-1).disabled,false);
nodes(refs.zoneSequence,'button').at(-1).click();
assert.deepEqual(soumis,item.reponse.valeur);
item=items[1]; rendreFonctionnel(item);
for(const d of item.contenu.documents) for(const l of d.lignes) assert.ok(texte(refs.zoneSequence).includes(l.texte));
assert.equal(nodes(refs.zoneSequence,'select').length,item.contenu.champs.length);
item=items[2];rendreFonctionnel(item);
for(const m of item.contenu.messages) {
  assert.ok(texte(refs.zoneSequence).includes(item.contenu.critere));
  assert.ok(texte(refs.zoneSequence).includes(m.texte));
  nodes(refs.zoneSequence,'button')[item.reponse.valeur[m.id]==='oui'?0:1].click();
}
nodes(refs.zoneSequence,'button')[0].click();assert.deepEqual(soumis,item.reponse.valeur);
'''
    execute(script)


def test_audio_attend_fin_voix_pause_et_annulation():
    script=BASE+r'''
const etat={memoGeneration:1,minuteriesMemo:[]};
let timers=[],voix=[],fins=0;
function setTimeout(f,ms){timers.push({f,ms});return timers.length}
const CAPACITES={lire(mot,callbacks){voix.push({mot,...callbacks});return true},arreter(){}};
function jouerDelaiOuQuestion(){fins++}
function afficherPhaseMemo(){} function annulerMemo(){etat.memoGeneration++}
'''
    script+='\nfunction jouerSeriesAudio(item, plateau, indicateur) '+corps_fonction(SOURCE,'jouerSeriesAudio')
    script+=r'''
const plateau=creerElement('div'),indicateur=creerElement('p');
const item={contenu:{affichage:{series:[['chat','lune']],pause_item_ms:2000,pause_serie_ms:3000}}};
jouerSeriesAudio(item,plateau,indicateur);
assert.equal(voix.length,1);
assert.ok(!texte(plateau).includes('chat'));
assert.equal(timers.filter(t=>t.ms===2000).length,0);
voix[0].onFin();assert.equal(voix.length,1);
timers.find(t=>t.ms===2000).f();assert.equal(voix.length,2);
voix[1].onFin();timers.filter(t=>t.ms===2000).at(-1).f();assert.equal(fins,1);
// La clôture ou un changement d'item invalide les callbacks restants.
jouerSeriesAudio(item,plateau,indicateur);const avant=timers.length;
etat.memoGeneration++;voix.at(-1).onFin();assert.equal(timers.length,avant);
'''
    execute(script)


def test_affichage_visuel_deux_secondes_puis_blanc():
    script=BASE+r'''
const etat={minuteriesMemo:[]};const CAPACITES={arreter(){}};
let timers=[],heure=0;function setTimeout(f,ms){timers.push({f,ms});return timers.length}
function creerNoeud(tag,attrs,...children){return creerElement(tag,attrs,...children)}
function afficherQuestion(){}let fin=false;function jouerDelaiOuQuestion(){fin=true}
const BLANC_INTER_ITEM_MS=120;
'''
    script+='\nfunction jouerAffichage(item) '+corps_fonction(SOURCE,'jouerAffichage')
    script+=r'''
const item={contenu:{affichage:{mode:'series',series:[['chat','lune']],duree_par_item_ms:2000,pause_item_ms:2000}}};
jouerAffichage(item);
const plateau=refs.zoneMemo.children[0];
// Le faux DOM permet la suppression d'un élément comme le vrai DOM.
const append=plateau.append.bind(plateau);plateau.append=(n)=>{n.remove=()=>{plateau.children=plateau.children.filter(x=>x!==n)};append(n)};
for(const t of timers.filter(t=>t.ms===0)) t.f();assert.ok(texte(plateau).includes('chat'));
for(const t of timers.filter(t=>t.ms===2000)) t.f();assert.ok(!texte(plateau).includes('chat'));
assert.ok(!timers.some(t=>t.ms>2000&&t.ms<4000));
for(const t of timers.filter(t=>t.ms===4000)) t.f();assert.ok(texte(plateau).includes('lune'));
for(const t of timers.filter(t=>t.ms===6000)) t.f();assert.ok(!texte(plateau).includes('lune'));
assert.equal(fin,false);for(const t of timers.filter(t=>t.ms===8000))t.f();assert.equal(fin,true);
'''
    execute(script)


def test_feedback_fonctionnel_visible():
    script=BASE+'''\nconst etat={theme:{id:'actualiser-consigne'}};
refs.carteFeedback=creerElement('div');refs.carteFeedback.hidden=true;
'''
    script+='\nfunction rendreFeedback(resultat) '+corps_fonction(SOURCE,'rendreFeedback')
    script+='''
rendreFeedback({correcte:true,detail_fonctionnel:{type:'actualiser-consigne',lignes:[{label:'Salle',attendue:'Atlas',correcte:true,explication:''}]}});
assert.equal(refs.carteFeedback.hidden,false);
assert.ok(texte(refs.carteFeedback).includes('Atlas'));
'''
    execute(script)


def test_lecteur_fichiers_attend_fin_et_invalide_anciens_evenements():
    source=(ROOT/'frontend/src/capacites.js').read_text()
    script='''
const assert=require('node:assert/strict');
let lecteur;
const window={Audio:class {
 constructor(){lecteur=this;this.pauses=0}
 play(){return {catch: f=>{this.echec=f}}}
 pause(){this.pauses++}
}};
'''+source+'''
let fins=0,erreurs=0;
assert.equal(Capacites.lireFichier('/mot.m4a',{onFin(){fins++},onErreur(){erreurs++}}),true);
assert.equal(lecteur.src,'/mot.m4a');assert.equal(fins,0);
const ancienFin=lecteur.onended, ancienErreur=lecteur.echec;
Capacites.arreter();ancienFin();ancienErreur();
assert.equal(fins,0);assert.equal(erreurs,0);assert.equal(lecteur.onended,null);
Capacites.lireFichier('/autre.m4a',{onFin(){fins++}});lecteur.onended();assert.equal(fins,1);
'''
    execute(script)
