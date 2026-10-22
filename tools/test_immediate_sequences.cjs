const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag) { this.tagName = tag; this.children = []; this.events = {}; this.attributes = {}; this.style = {}; this.textContent = ''; this.disabled = false; this.className = ''; this.classList = { add: name => { this.className += ` ${name}`; }, remove: name => { this.className = this.className.replace(` ${name}`, ''); } }; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, handler) { this.events[name] = handler; }
  focus() { this.focused = true; }
  querySelectorAll(selector) { return this.children.flatMap(node => [...(selector.split(',').includes(node.tagName) ? [node] : []), ...node.querySelectorAll(selector)]); }
  click(detail = 1) { if (!this.disabled) this.events.click?.({ detail }); }
}
function environment(parcours = 'code', extras = {}) {
  const root = new Element('div'), events = [], answers = [], incidents = [], waits = [];
  const context = { document: { createElement: tag => new Element(tag), createElementNS: (_, tag) => new Element(tag) }, DOMException, ...extras };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('frontend/src/exercises/immediate-sequences.js', 'utf8'), context);
  const trial = { parcours, parametres: { longueur: 3, modalite: 'visuelle', signal_ms: 10, intervalle_ms: 5, masque_ms: 2 },
    stimulus: parcours === 'code' ? { chiffres: ['0','4','7'] } : { positions: [{id:'a',x:.1,y:.2},{id:'b',x:.8,y:.1},{id:'c',x:.4,y:.8}], trajet:['a','b','c'] } };
  const renderer = context.renderImmediateSequence({ root, trial, wait: async delay => { waits.push(delay); }, now: () => events.length,
    emit: (type, value) => events.push({type,...value}), onAnswer: value => answers.push(value), onIncident: value => incidents.push(value) });
  const buttons = () => root.querySelectorAll('button');
  return { root, trial, renderer, events, answers, incidents, waits, buttons };
}
test('code masqué puis saisie conserve le zéro initial et les séparateurs', async () => {
  const e = environment(); await e.renderer.present();
  assert.deepEqual(e.events.filter(x=>x.type==='phase').map(x=>x.phase), ['exposition','masque','reponse']);
  assert.deepEqual(e.waits, [10,5,10,5,10,2]);
  assert.equal(e.root.querySelectorAll('div').length, 0);
  const input = e.root.querySelectorAll('input')[0];
  input.value = '0 - 4 7'; input.events.input();
  const form = e.root.querySelectorAll('form')[0];
  form.events.submit({preventDefault(){}}); form.events.submit({preventDefault(){}});
  assert.equal(e.answers.length, 1); assert.equal(e.answers[0].response, '047');
});
test('saisie invalide ne devient pas une absence implicite', async () => {
  const e = environment(); await e.renderer.present();
  const input = e.root.querySelectorAll('input')[0]; input.value='';
  e.root.querySelectorAll('form')[0].events.submit({preventDefault(){}});
  assert.equal(e.answers.length,0);
  assert.ok(!e.buttons().some(b=>b.textContent==='Je ne sais pas'));
  e.buttons().find(b=>b.textContent==='Confirmer cette réponse').click();
  assert.equal(e.answers[0].response,null); assert.equal(e.answers[0].absence,true);
});
test('chemin masque les indications et autorise annulation, réponse clavier verrouillée', async () => {
  const e = environment('chemin'); await e.renderer.present();
  const cells = e.buttons().filter(b=>b.className==='immediate-path-cell');
  assert.equal(cells.length,3); assert(cells.every(b=>b.textContent===''));
  cells[0].click(0); cells[2].click(0);
  cells[2].click(0);
  cells[1].click(0); cells[2].click(0);
  assert.equal(cells[1].textContent,'2');
  e.buttons().find(b=>b.textContent==='Valider le chemin').click();
  assert.deepEqual(Array.from(e.answers[0].response),['a','b','c']);
  assert.equal(e.answers[0].modality,'clavier');
  cells[0].click(0); assert.equal(e.answers.length,1);
});
test('interruption enlève le stimulus et empêche toute réponse tardive', async () => {
  let release;
  const e = environment();
  const original = e.renderer;
  // L’arrêt pendant le premier délai doit rendre la suite inerte.
  const context = { document:{createElement:tag=>new Element(tag)},DOMException };
  vm.createContext(context); vm.runInContext(fs.readFileSync('frontend/src/exercises/immediate-sequences.js','utf8'),context);
  const renderer = context.renderImmediateSequence({root:e.root,trial:e.trial,wait:()=>new Promise(r=>{release=r}),now:()=>0,emit:()=>{},onAnswer:v=>e.answers.push(v),onIncident:v=>e.incidents.push(v)});
  const pending=renderer.present(); renderer.destroy(); release(); await pending;
  assert.equal(e.root.children.length,0); assert.equal(e.answers.length,0);
  original.destroy();
});
test('auditif indisponible signale un incident sans exposer de chiffres', async () => {
  const e=environment('code',{speechSynthesis:{getVoices:()=>[]}}); e.trial.parametres.modalite='auditive';
  await e.renderer.present(); assert.deepEqual(e.incidents,['audio_indisponible']);
  assert.equal(e.events.length,0); assert.equal(e.root.querySelectorAll('input').length,0);
});
test('auditif attend la fin effective de chaque chiffre, puis l’intervalle', async () => {
  const pending=[],spoken=[];
  const e=environment('code',{SpeechSynthesisUtterance:class{constructor(text){this.text=text;}},speechSynthesis:{getVoices:()=>[{localService:true,lang:'fr-FR',voiceURI:'local'}],speak:u=>{spoken.push(u.text);pending.push(u);},cancel(){}}});
  e.trial.parametres.modalite='auditive';
  const presentation=e.renderer.present();
  assert.deepEqual(spoken,['zéro']); assert.equal(e.waits.length,0);
  for(let i=0;i<3;i++){pending[i].onend();await new Promise(resolve=>setImmediate(resolve));}
  await presentation;
  assert.deepEqual(spoken,['zéro','quatre','sept']); assert.deepEqual(e.waits,[5,5,2]);
  assert(e.events.some(v=>v.type==='voix'&&v.voix==='local'));
});

test('chemin incomplet ou vide validé seulement après confirmation, vider conserve la possibilité de répondre', async () => {
  const e = environment('chemin'); await e.renderer.present();
  const cells = e.buttons().filter(b=>b.className==='immediate-path-cell');
  cells[0].click(); e.buttons().find(b=>b.textContent==='Vider les cases').click();
  assert.ok(cells.every(b=>b.textContent===''));
  assert.ok(!e.buttons().some(b=>b.textContent==='Je ne sais pas'));
  e.buttons().find(b=>b.textContent==='Valider le chemin').click(); assert.equal(e.answers.length,0);
  e.buttons().find(b=>b.textContent==='Confirmer cette réponse').click(); assert.deepEqual(Array.from(e.answers[0].response),[]);
});

test('traits relient uniquement les choix courants et disparaissent au retrait ou au vidage', async () => {
  const e = environment('chemin'); await e.renderer.present();
  const cells = e.buttons().filter(b=>b.className==='immediate-path-cell');
  assert.equal(e.root.querySelectorAll('line').length,0);
  cells[0].click(); cells[1].click(); cells[2].click();
  assert.equal(e.root.querySelectorAll('line').length,2);
  cells[1].click(); const lines = e.root.querySelectorAll('line'); assert.equal(lines.length,1);
  assert.equal(lines[0].attributes.x2,40); assert.equal(lines[0].attributes.y2,80);
  e.buttons().find(b=>b.textContent==='Vider les cases').click(); assert.equal(e.root.querySelectorAll('line').length,0);
});

test('réponse vocale locale convertit les chiffres, conserve zéro et ignore un retour après destruction', async () => {
  let callbacks, aborted=0;
  const e=environment('code',{CAPACITES:{voixDisponible:()=>true,arreter(){},dicter:c=>{callbacks=c;return {stop(){},abort(){aborted++;}};}},SpeechSynthesisUtterance:class{},speechSynthesis:{getVoices:()=>[{localService:true,lang:'fr-FR'}],speak:u=>setImmediate(()=>u.onend()),cancel(){}}});
  e.trial.parametres.modalite='auditive';await e.renderer.present();
  assert.ok(callbacks, 'micro démarré automatiquement');
  callbacks.onPartiel('zéro quatre sept');
  const input=e.root.querySelectorAll('input')[0];assert.equal(input.value,'047');assert.equal(e.answers.length,0);
  callbacks.onResultat('bonjour quatre');assert.equal(input.value,'047');
  callbacks.onResultat('zéro quatre sept');
  assert.equal(e.answers.length,1);assert.equal(e.answers[0].response,'047');assert.equal(e.answers[0].modality,'vocale');assert.equal(aborted,1);
  callbacks.onResultat('neuf neuf neuf');assert.equal(e.answers.length,1);
  e.renderer.destroy();callbacks.onResultat('neuf neuf neuf');assert.equal(input.value,'047');
});

test('code auditif utilise la voix choisie via le lecteur commun avant ouverture du micro', async () => {
  const order=[];
  const e=environment('code',{CAPACITES:{voixLocales:()=>[{voiceURI:'macos:Audrey',native:'Audrey'}],choixVoix:()=> 'macos:Audrey',voixDisponible:()=>true,arreter(){},lire:(text,options)=>{order.push(text);setImmediate(options.onFin);return true;},dicter:()=>{order.push('micro');return {stop(){},abort(){}};}}});
  e.trial.parametres.modalite='auditive';await e.renderer.present();
  assert.deepEqual(order,['zéro','quatre','sept','micro']);
  assert.ok(e.events.some(event=>event.type==='voix'&&event.voix==='macos:Audrey'));
  e.renderer.destroy();
});
