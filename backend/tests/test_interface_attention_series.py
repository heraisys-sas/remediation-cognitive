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
    script=BASE+'\nfunction lireEtapeActualisation() {}\nfunction rendreFonctionnel(item) '+corps_fonction(SOURCE,'rendreFonctionnel')
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
for(let i=0;i<item.contenu.messages.length;i++) {
  const m=item.contenu.messages[i];
  assert.ok(texte(refs.zoneSequence).includes(item.contenu.critere));
  assert.ok(texte(refs.zoneSequence).includes(m.texte));
  const choix=nodes(refs.zoneSequence,'button')[item.reponse.valeur[m.id]==='oui'?0:1];
  choix.click();
  // Un double clic sur l'ancien bouton ne doit pas répondre au message suivant.
  if(i===0) choix.click();
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
const BLANC_INTER_ITEM_MS=2000;
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


def test_consigne_memo_identique_lue_une_seule_fois_mais_reste_affichee():
    script = BASE + r'''
for (const nom of ['enonce','rappelConsigne','zoneAide','carteFeedback',
                   'boutonSuivant','formulaire']) refs[nom]=creerElement('div');
const etat={consignesMemoVues:new Set(),enonceCourant:''};
const CAPACITES={syntheseDisponible(){return true}};
const BLANC_INTER_ITEM_MS=2000;
let lectures=[];
function viderZonesReponse(){}
function lireSiLectureAuto(texte){lectures.push(texte)}
function reglerEtatBoutons(){}
function jouerAffichage(){}
'''
    script += '\nfunction afficherPhaseMemo(item) ' + corps_fonction(SOURCE, 'afficherPhaseMemo')
    script += r'''
const item={type:'empan',contenu:{
  consigne:'Mémorise la séquence de chiffres.',
  affichage:{mode:'sequence',elements:['4','7'],duree_par_item_ms:2000,pause_item_ms:2000}
}};
afficherPhaseMemo(item);
assert.deepEqual(lectures,['Mémorise la séquence de chiffres.']);
assert.equal(refs.enonce.textContent,'Mémorise la séquence de chiffres.');
afficherPhaseMemo(item);
assert.equal(lectures.length,1);
assert.equal(refs.enonce.textContent,'Mémorise le contenu affiché.');
const nouvelle={...item,contenu:{...item.contenu,consigne:'Mémorise les mots dans l’ordre.'}};
afficherPhaseMemo(nouvelle);
assert.deepEqual(lectures,[
  'Mémorise la séquence de chiffres.',
  'Mémorise les mots dans l’ordre.'
]);
assert.equal(refs.enonce.textContent,'Mémorise les mots dans l’ordre.');
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


def test_reprise_interrompt_masque_le_dossier_et_retrouve_le_point_suivant():
    item=next(i for i in ChargeurContenu().items('garder-cap') if i['type']=='reprise-interrompue'
              and i['contenu']['interruption_apres']==2)
    script=BASE+'\nfunction rendreRepriseInterrompue(item) '+corps_fonction(SOURCE,'rendreRepriseInterrompue')
    script+='\nconst item='+json.dumps(item)+r''';
rendreRepriseInterrompue(item);
for(let i=0;i<item.contenu.interruption_apres;i++) {
  const point=item.contenu.points[i];
  assert.ok(texte(refs.zoneSequence).includes(point.etat));
  const position=item.reponse.valeur.points[point.id]==='valide'?0:1;
  nodes(refs.zoneSequence,'button')[position].click();
}
assert.ok(texte(refs.zoneSequence).includes('Interruption'));
assert.ok(!texte(refs.zoneSequence).includes(item.contenu.but));
const boutonsDétour=nodes(refs.zoneSequence,'button');
boutonsDétour[0].click();boutonsDétour[0].click();boutonsDétour[1].click();
assert.ok(texte(refs.zoneSequence).includes('Retrouve le fil'));
assert.ok(!texte(refs.zoneSequence).includes(item.contenu.but));
const prochain=item.reponse.valeur.reprise;
const labels=item.contenu.points.map(p=>p.label);
nodes(refs.zoneSequence,'button')[item.contenu.points.findIndex(p=>p.id===prochain)].click();
for(let i=item.contenu.interruption_apres;i<item.contenu.points.length;i++) {
  const point=item.contenu.points[i];
  assert.ok(texte(refs.zoneSequence).includes(point.etat));
  nodes(refs.zoneSequence,'button')[item.reponse.valeur.points[point.id]==='valide'?0:1].click();
}
nodes(refs.zoneSequence,'button')[0].click();
assert.deepEqual(soumis.points,item.reponse.valeur.points);
assert.equal(soumis.reprise,item.reponse.valeur.reprise);
assert.equal(soumis.interruption,item.contenu.interruption.options[0]);
'''
    execute(script)


def test_feedback_rappel_distingue_omission_confusion_et_intrusion():
    script=BASE+'''\nconst etat={theme:{id:'rappel-series'},reponseSoumise:''};
refs.carteFeedback=creerElement('div');refs.carteFeedback.hidden=true;
function rendreFeedbackGrille(){} function rendreFeedbackSequence(){}
'''
    script+='\nfunction rendreFeedback(resultat) '+corps_fonction(SOURCE,'rendreFeedback')
    script+='''
rendreFeedback({correcte:false,attendue:['chat','lune'],detail_rappel:{
  retrouves:['chat'],omis:['lune'],confusions_series:['gare'],intrusions:['ardoise']
}});
const retour=texte(refs.carteFeedback);
assert.ok(retour.includes('Retrouvés : 1 sur 2'));
assert.ok(retour.includes('Il restait : lune'));
assert.ok(retour.includes('Mots d’une autre série : gare'));
assert.ok(retour.includes('Mots non présentés : ardoise'));
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


def test_synthese_explicitement_les_operateurs_sans_casser_les_mots_composes():
    source=(ROOT/'frontend/src/capacites.js').read_text()
    script=r'''
const assert=require('node:assert/strict');
let prononce=[];
class Enonce {constructor(texte){this.text=texte}}
const window={
  SpeechSynthesisUtterance:Enonce,
  speechSynthesis:{cancel(){},getVoices(){return [{lang:"fr-FR",localService:true,voiceURI:"locale"}]},speak(e){prononce.push(e.text)}}
};
const SpeechSynthesisUtterance=Enonce;
'''+source+r'''
Capacites.lire('Combien font 8 − 3 × 2 ?');
assert.equal(prononce.pop(),'Combien font 8 moins 3 multiplié par 2 ?');
Capacites.lire('42 = ? × 7');
assert.equal(prononce.pop(),'42 égale quel nombre multiplié par 7');
Capacites.lire('? + 3 = 8');
assert.equal(prononce.pop(),'quel nombre plus 3 égale 8');
Capacites.lire('10 − ? = 4');
assert.equal(prononce.pop(),'10 moins quel nombre égale 4');
Capacites.lire('? = 6 × 7');
assert.equal(prononce.pop(),'quel nombre égale 6 multiplié par 7');
Capacites.lire('Combien font 8 - 3 x 2 + 1 ?');
assert.equal(prononce.pop(),'Combien font 8 moins 3 multiplié par 2 plus 1 ?');
Capacites.lire('Rendez-vous à mi-parcours.');
assert.equal(prononce.pop(),'Rendez-vous à mi-parcours.');
'''
    execute(script)


def test_actualisation_audio_message_courant_et_consigne_non_repetee():
    script = r"""
const assert=require('node:assert/strict');
const etat={consignesMemoVues:new Set(),enonceCourant:''};
const refs={ligneAudio:{hidden:true}};
let lectures=[],auto=true,arrets=0;
const CAPACITES={arreter(){arrets++},syntheseDisponible(){return true}};
function lireSiLectureAuto(t){if(auto) lectures.push(t)}
""" + 'function lireEtapeActualisation(item, texte, premiereEtape = false) ' + corps_fonction(SOURCE,'lireEtapeActualisation') + r"""
const item={contenu:{consigne:'Garde ce qui reste valable.'}};
lireEtapeActualisation(item,'Réunion à 14 h.',true);
assert.equal(refs.ligneAudio.hidden,false);
assert.equal(lectures.at(-1),'Garde ce qui reste valable. Réunion à 14 h.');
lireEtapeActualisation(item,'Nouvel horaire : 15 h.');
assert.equal(etat.enonceCourant,'Nouvel horaire : 15 h.');
assert.equal(lectures.at(-1),'Nouvel horaire : 15 h.');
lireEtapeActualisation(item,'Autre réunion à 10 h.',true);
assert.equal(lectures.at(-1),'Autre réunion à 10 h.');
assert.equal(etat.enonceCourant,'Garde ce qui reste valable. Autre réunion à 10 h.');
auto=false;
const nb=lectures.length;
lireEtapeActualisation(item,'Écris la consigne finale.');
assert.equal(lectures.length,nb);
assert.equal(etat.enonceCourant,'Écris la consigne finale.');
assert.equal(arrets,4);
"""
    execute(script)


def test_choix_voix_locale_prioritaire_et_persistant():
    source=(ROOT/'frontend/src/capacites.js').read_text()
    execute(r"""
const assert=require('node:assert/strict');
let dernier, stock={}, voix=[
 {lang:'fr-FR',localService:false,voiceURI:'cloud',default:true},
 {lang:'fr-FR',localService:true,voiceURI:'premiere'},
 {lang:'fr-FR',localService:true,voiceURI:'preferee',default:true}];
class Enonce {constructor(t){this.text=t}}
const SpeechSynthesisUtterance=Enonce;
const window={SpeechSynthesisUtterance:Enonce,
 localStorage:{getItem(k){return stock[k]},setItem(k,v){stock[k]=v}},
 speechSynthesis:{cancel(){},getVoices(){return voix},speak(e){dernier=e}}};
""" + source + r"""
Capacites.lire('Bonjour');
assert.equal(dernier.voice.voiceURI,'preferee');
Capacites.choisirVoix('premiere');
Capacites.lire('Bonjour');
assert.equal(dernier.voice.voiceURI,'premiere');
assert.equal(stock['remediation.voixLocale'],'premiere');
assert.equal(Capacites.voixLocales().length,2);
Capacites.choisirVoix('disparue');
Capacites.lire('Bonjour');
assert.equal(dernier.voice.voiceURI,'preferee');
voix=[voix[0]];
assert.equal(Capacites.lire('Bonjour'),false);
""")
