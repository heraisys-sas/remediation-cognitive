const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.attributes = {}; this.events = {}; this.style = {setProperty(key, value) { this[key] = value; }}; this.classList = {add: (...names) => { this.className += ' ' + names.join(' '); }}; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key,value) { this.attributes[key] = value; }
  addEventListener(event, callback) { this.events[event] = callback; }
  querySelectorAll(tag) { return this.children.flatMap(child => [...(child.tag === tag ? [child] : []), ...child.querySelectorAll(tag)]); }
  querySelector(tag) { return this.querySelectorAll(tag)[0]; }
  focus() { this.focused = true; }
  click() { if (!this.disabled) this.events.click?.({detail:0}); }
}
function setup(parcours = 'changement', condition = 'association') {
  const root = new Element('section'), answers = [], events = [], timers = [];
  const trial = {parcours, parametres:{condition,exposition_ms:5000,masque_ms:1000}, stimulus: parcours === 'changement' ? {
    avant:[{position:'0',forme:'carre',couleur:'bleu'},{position:'1',forme:'triangle',couleur:'rose'}],
    apres:[{position:'0',forme:'carre',couleur:'rose'},{position:'1',forme:'triangle',couleur:'bleu'}],palette:{bleu:'#668fc0',rose:'#b87892'},
  } : {positions:[{id:'0',x:.25,y:.5},{id:'1',x:.75,y:.5}],objets:[{id:'cle',nom:'Clé'},{id:'tasse',nom:'Tasse'}],modele:{cle:'1',tasse:'0'},reserve:['tasse','cle']}};
  const context = {document:{createElementNS: (_,tag) => new Element(tag)}, creerElement(tag, options = {}, ...nodes) { const e = new Element(tag); e.className = options.classe || ''; e.textContent = options.texte || ''; Object.entries(options.attributs || {}).forEach(([k,v]) => e.setAttribute(k,v)); e.append(...nodes); return e; }};
  vm.createContext(context); vm.runInContext(fs.readFileSync('frontend/src/exercises/immediate-visual.js','utf8'),context);
  const renderer = context.renderImmediateVisual({root,trial,wait:ms => new Promise(resolve => timers.push({ms,resolve})),emit:(name,data) => events.push({name,data}),onAnswer: async data => answers.push(data)});
  const button = text => { const b = root.querySelectorAll('button').find(e => (e.attributes["aria-label"] || e.textContent) === text); assert.ok(b, text); return b; };
  async function response() { const task = renderer.present(); timers.shift().resolve(); await new Promise(setImmediate); timers.shift().resolve(); await task; }
  return {root,renderer,answers,events,timers,button,response};
}
test('exposition supprimée au masque, aucune couleur verbalisée, seconde composition avant réponse', async () => {
  const s = setup(); const task = s.renderer.present();
  assert.equal(s.root.querySelectorAll('svg').length,2);
  assert.equal(s.root.children[0].children[0].attributes['aria-label'],'Élément 1');
  s.timers.shift().resolve(); await new Promise(setImmediate);
  assert.equal(s.root.querySelectorAll('svg').length,0);
  assert.equal(s.root.querySelectorAll('button').length,0);
  s.timers.shift().resolve(); await task;
  assert.deepEqual(s.events.map(e => e.name), ['phase','phase','seconde_composition','phase']);
});
test('décision différente verrouillée, deux éléments obligatoires sauf absence de localisation', async () => {
  const s = setup(); await s.response(); s.button('Différent').click();
  assert.equal(s.root.querySelectorAll('button').some(b => b.textContent === 'Identique'),false);
  assert.equal(Boolean(s.button('Valider la localisation').disabled),false);
  s.button('Élément 1').click(); assert.equal(Boolean(s.button('Valider la localisation').disabled),false);
  s.button('Élément 2').click(); s.button('Valider la localisation').click();
  assert.equal(s.answers.length,1); assert.deepEqual(Array.from(s.answers[0].response.localisation),['0','1']);
  assert.equal(s.answers[0].modality,'clavier');
});
test('absence de localisation conserve détection différente', async () => {
  const s = setup(); await s.response(); s.button('Différent').click(); s.button('Valider la localisation').click(); assert.equal(s.answers.length,0); s.button('Confirmer cette réponse').click();
  assert.equal(s.answers[0].response.decision,'different'); assert.equal(s.answers[0].response.localisation_absente,true);
});
test('placements vides puis réserve indépendante, réponse partielle exige confirmation', async () => {
  const s = setup('objets'); await s.response();
  const slots = s.root.querySelectorAll('button').filter(b => (b.attributes['aria-label'] || '').includes(' : vide'));
  assert.equal(slots.length,2);
  assert.ok(!s.root.querySelectorAll('button').some(b => b.textContent === 'Je ne sais pas'));
  assert.ok(slots.every(b => b.textContent === '' && b.children.length === 0));
  s.button('Clé').click(); s.button('Emplacement 1 : vide').click(); s.button('Valider les placements').click();
  assert.equal(s.answers.length,0); s.button('Confirmer cette réponse').click();
  assert.equal(s.answers[0].response.cle,'0'); assert.equal(s.answers[0].response.tasse,undefined);
});
test('objet placé grisé et désactivé ; clic sur sa case le remet en réserve', async () => {
  const s = setup('objets'); await s.response();
  s.button('Clé').click(); s.button('Emplacement 1 : vide').click();
  const placed = s.button('Clé, déjà placé'); assert.equal(placed.disabled, true);
  assert.ok(placed.className.includes('is-placed'));
  assert.ok(!s.root.querySelectorAll('button').some(b => b.textContent === 'Retirer l’objet sélectionné'));
  s.button('Emplacement 1 : Clé').click();
  assert.ok(s.button('Emplacement 1 : vide')); assert.equal(s.button('Clé').disabled, false);
  assert.equal(s.button('Vider les cases').disabled, true);
});
test('destruction durant exposition empêche phase réponse', async () => {
  const s = setup(); const task = s.renderer.present(); s.renderer.destroy(); s.timers.shift().resolve(); await task;
  assert.equal(s.root.children.length,0); assert.equal(s.events.length,1);
});
test('vider les cases retire tous les objets et réactive toute la réserve', async () => {
  const s = setup('objets'); await s.response();
  assert.equal(s.button('Vider les cases').disabled, true);
  s.button('Clé').click(); s.button('Emplacement 1 : vide').click();
  s.button('Tasse').click(); s.button('Emplacement 2 : vide').click();
  s.button('Vider les cases').click();
  assert.ok(s.button('Emplacement 1 : vide')); assert.ok(s.button('Emplacement 2 : vide'));
  assert.equal(s.button('Clé').disabled, false); assert.equal(s.button('Tasse').disabled, false);
  assert.equal(s.button('Vider les cases').disabled, true); assert.equal(s.answers.length, 0);
});
test('forme croix et objet pomme ont des tracés distincts, sans nom caché de stimulus', () => {
  const context = {document:{createElementNS: (_,tag) => new Element(tag)}};
  vm.createContext(context); vm.runInContext(fs.readFileSync('frontend/src/exercises/immediate-visual.js','utf8'),context);
  const cross = context.immediateVisualGlyph('croix'), apple = context.immediateVisualGlyph('pomme');
  assert.equal(cross.children[0].tag, 'path'); assert.notEqual(cross.children[0].attributes.d, apple.children[0].attributes.d);
  assert.equal(cross.attributes['aria-hidden'], 'true'); assert.equal(cross.attributes['aria-label'], undefined);
});
