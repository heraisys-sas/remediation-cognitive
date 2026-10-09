const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Node {
  constructor(tag, options = {}) { this.tag = tag; this.textContent = options.texte || ''; this.children = []; this.events = {}; this.disabled = false; this.dataset = {}; this.style = {}; }
  get childNodes() { return this.children; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  addEventListener(name, callback) { this.events[name] = callback; }
  setAttribute() {}
  focus() { this.focused = true; }
  querySelector(tag) { return tag === ".bouton-audio" ? this.querySelectorAll("button").find(n => n.className?.includes("bouton-audio")) || null : this.querySelectorAll(tag)[0] || null; }
  querySelectorAll(tag) { return this.children.flatMap(child => [...(child.tag === tag ? [child] : []), ...child.querySelectorAll(tag)]); }
  async click() { if (!this.disabled) return this.events.click?.(); }
}
function environment() {
  const nodes = new Map(), calls = [], listeners = {}, saved = {}, clock = { now: 0 }, destroyed = [];
  const context = { console, AbortController, DOMException, setTimeout, clearTimeout,
    performance: { now: () => clock.now }, etat: { actionEnCours: false },
    document: { hidden: false, addEventListener: (name, callback) => { listeners[name] = callback; } },
    window: { innerWidth: 600, addEventListener: (name, callback) => { listeners[name] = callback; } },
    CAPACITES: { arreter() {}, lire: () => false },
    actualiserBoutonAudio(active, button) { button.textContent = active ? "" : "Écouter"; },
    creerElement: (tag, options, ...children) => { const node = new Node(tag, options); node.className = options?.classe || ''; node.append(...children); return node; },
    $: id => { if (!nodes.has(id)) nodes.set(id, new Node('div')); return nodes.get(id); },
    preferenceLocale: (key, fallback = '') => saved[key] ?? fallback,
    garderPreference: (key, value) => { saved[key] = value; }, modeDerogatoireActif: () => false,
    sansLimiteActivee: () => false, annulerMemo() {}, afficherVue() {}, afficherBandeau() {}, revenirAuxThemes() {},
    fetchJson: async (_base, path, options) => {
      const body = options.body === undefined ? undefined : JSON.parse(options.body);
      calls.push({ path, body }); return context.respond(path, body);
    }, respond: () => ({}), renderImmediateVisualModel() {},
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync('frontend/src/immediate-memory.js', 'utf8'), context);
  const set = values => { context.values = values; vm.runInContext('immediateBlock = values', context); };
  const get = () => vm.runInContext('immediateBlock', context);
  set({ session_id: 's', parcours: 'code', trial: { id: 'original', index: 1, stimulus: { chiffres: ['0','4','7'] } },
    parametres: { longueur: 3, modalite: 'visuelle' }, phase: 'reponse', facts: {}, times: { reponse: 0 }, pending: false,
    renderer: { destroy: () => destroyed.push(true) }, controller: new AbortController(), assistee: false, example: false });
  return { context, nodes, calls, listeners, saved, clock, destroyed, get, set,
    buttons: () => context.$('mi-commandes').querySelectorAll('button'),
    settle: () => new Promise(resolve => setImmediate(resolve)) };
}
test('réponse non confirmée reste verrouillée et Réessayer renvoie exactement le même payload', async () => {
  const e = environment(); let requests = 0;
  e.context.respond = () => { if (++requests === 1) throw new Error('réseau'); return { correction: { exacte:true, positions_exactes:3, elements_retrouves:3, longueur:3 }, essai_suivant:null }; };
  e.clock.now = 120;
  await e.context.immediateAnswer({ response:'047', modality:'clavier' });
  assert.equal(e.get().phase,'retour'); assert.equal(e.destroyed.length,1);
  e.clock.now = 500;
  await e.buttons().find(b=>b.textContent==='Réessayer').click();
  assert.equal(e.calls.length,2); assert.deepEqual(e.calls[0].body,e.calls[1].body);
  assert.equal(e.calls[0].body.reponse,'047'); assert.equal(e.get().correction.exacte,true);
});
test('durées de masque, délai de rappel, latence et saisie restent distinctes', () => {
  const e = environment(); const c = e.context;
  e.clock.now=10;c.immediateEmit('phase',{phase:'exposition'});
  e.clock.now=110;c.immediateEmit('phase',{phase:'masque'});
  e.clock.now=125;c.immediateEmit('seconde_composition');
  e.clock.now=130;c.immediateEmit('phase',{phase:'reponse'});
  e.clock.now=150;c.immediateEmit('premiere_action',{modalite:'clavier'});
  e.clock.now=175;c.immediateEmit('premiere_action',{modalite:'clavier'});
  e.clock.now=180;const facts=c.immediateFacts('clavier');
  assert.equal(facts.exposition_ms,100);assert.equal(facts.masque_ms,20);
  assert.equal(facts.delai_rappel_ms,20);assert.equal(facts.seconde_composition_ms,15);
  assert.equal(facts.latence_ms,20);assert.equal(facts.saisie_ms,30);
});
test('le clavier mobile modifiant seulement la hauteur n’interrompt pas ; largeur et onglet masqué interrompent', async () => {
  const e=environment();const reasons=[]; e.context.immediatePause=reason=>reasons.push(reason);
  e.context.initialiserMemoiresImmediates();
  e.context.window.innerHeight=400;e.listeners.resize();assert.deepEqual(reasons,[]);
  e.context.window.innerWidth=700;e.listeners.resize();assert.deepEqual(reasons,['geometrie_modifiee']);
  e.context.document.hidden=false;e.listeners.visibilitychange();assert.equal(reasons.length,1);
  e.context.document.hidden=true;e.listeners.visibilitychange();assert.equal(reasons[1],'onglet_masque');
});
test('pause avant le départ ne crée aucun incident ni nouvel essai', async () => {
  const e=environment();e.get().phase='pret';await e.context.immediatePause('pause');
  assert.equal(e.calls.length,0);assert.equal(e.get().trial.id,'original');assert.equal(e.destroyed.length,0);
});
test('aide séparée conserve le prochain essai initial et envoie assistee:true', async () => {
  const e=environment();const next={id:'suivant',index:2,stimulus:{chiffres:['1','2','3']}};
  e.get().phase='retour';e.get().next=next;e.get().correction={exacte:true,positions_exactes:3,elements_retrouves:3,longueur:3};e.get().response='047';
  e.context.respond=path=>path.endsWith('/aide')?{essai:{id:'aide',index:1,stimulus:{chiffres:['0','4','7']}}}:{correction:{exacte:true,positions_exactes:3,elements_retrouves:3,longueur:3},essai_suivant:next};
  e.context.immediateFeedback();await e.buttons().find(b=>b.textContent==='Revoir et essayer avec aide').click();
  assert.equal(e.get().assistee,true);assert.equal(e.get().next.id,'suivant');
  await e.context.immediateAnswer({response:'047',modality:'clavier'});
  assert.equal(e.calls[1].body.assistee,true);assert.equal(e.get().next.id,'suivant');
  e.context.immediateStop();
  e.get().trial = next; e.get().assistee = false;
  assert.equal(e.get().trial.id,'suivant');assert.equal(e.get().assistee,false);
  e.context.immediateStop();
});
test('pause d’un essai aidé est signalée sans remplacer une réponse initiale', async () => {
  const e=environment();e.get().assistee=true;e.get().phase='exposition';
  e.context.respond=()=>({essai:{id:'nouveau',index:2,stimulus:{chiffres:['1','2','3']}}});
  await e.context.immediatePause('pause');
  assert.equal(e.calls[0].body.assistee,true);assert.equal(e.calls[0].body.phase,'exposition');
  assert.equal(e.get().trial.id,'nouveau');assert.equal(e.get().assistee,false);
});
test('terminer pendant l’exposition persiste l’interruption avant la fin du bloc', async () => {
  const e=environment();e.get().phase='exposition';
  e.context.respond=path=>path.endsWith('/interruption')?{essai:{id:'nouveau',index:1,stimulus:{chiffres:['1','2','3']}}}:{observations:[{interruption:{raison:'sortie'}}]};
  await e.context.immediateFinish();
  assert.deepEqual(e.calls.map(c=>c.path),['/sessions/s/interruption','/sessions/s/fin']);
  assert.equal(e.calls[0].body.observations.raison,'sortie');assert.equal(e.get().phase,'fin');
});
test('préférences de confort persistantes et valeurs dérogatoires appliquées seulement en mode dérogatoire', () => {
  const e=environment();e.saved['orthogone.mi.code.modalite']='auditive';e.saved['orthogone.mi.code.longueur']='5';
  assert.equal(e.context.immediateParameters('code').modalite,'auditive');assert.equal(e.context.immediateParameters('code').longueur,4);
  e.context.modeDerogatoireActif=()=>true;assert.equal(e.context.immediateParameters('code').longueur,5);
  e.context.modeDerogatoireActif=()=>false;assert.equal(e.context.immediateParameters('code').longueur,4);
  assert.equal(e.saved['orthogone.mi.code.longueur'],'5');assert.equal(e.context.immediateParameters('chemin').modalite,'visuelle');
});
test('un incident audio avant tout signal reste enregistré et propose un autre essai visuel', async () => {
  const e=environment();e.get().phase='pret';e.get().parametres.modalite='auditive';
  e.context.respond=()=>({essai:{id:'nouveau',index:1,stimulus:{chiffres:['1','2','3']}}});
  e.context.renderImmediateSequence=({onIncident})=>({present:async()=>{onIncident('audio_indisponible');},destroy(){}});
  await e.context.immediatePresent();await e.settle();
  assert.equal(e.calls.length,1);assert.equal(e.calls[0].body.phase,'pret');assert.equal(e.calls[0].body.observations.raison,'audio_indisponible');
  assert(e.buttons().some(button=>button.textContent==='Choisir les chiffres vus'));
});

test('consigne objets lue une seule fois avec bouton muet puis suite silencieuse', async () => {
  const e = environment(), readings = [];
  e.get().parcours = 'objets'; e.get().parametres.exposition_ms = 8000;
  e.context.CAPACITES.lire = (text, options) => { readings.push({text, options}); return true; };
  e.context.immediateReady();
  assert.equal(readings.length, 1); assert.match(readings[0].text, /8 secondes seulement/);
  const audio = e.context.$('mi-contenu').querySelectorAll('button').find(b => b.dataset.reading === 'on'); assert.ok(audio);
  await audio.click(); assert.equal(audio.textContent, 'Écouter');
  e.context.immediateReady(); assert.equal(readings.length, 1);
  assert.ok(!e.buttons().some(b => b.textContent === 'Écouter'));
});

test('les voix locales sont chargées avant l’ouverture du bloc et sa consigne', async () => {
  const e = environment(), order = [];
  e.context.CAPACITES.chargerVoixLocales = async () => { order.push('voix'); };
  e.context.respond = () => { order.push('session'); return {parcours:'objets', parametres:{exposition_ms:6000}, essai:{id:'o',index:1,stimulus:{}}}; };
  e.context.CAPACITES.lire = text => { order.push('consigne'); return false; };
  await e.context.demarrerMemoiresImmediates('objets');
  assert.deepEqual(order,['voix','session','consigne']);
});

for (const parcours of ['chemin', 'objets', 'changement', 'code']) test(`${parcours} suivant : compte à rebours, pause sans incident et reprise avant présentation`, async () => {
  const e = environment(), timers = new Map(); let nextId = 0, starts = 0;
  e.context.setTimeout = fn => { timers.set(++nextId, fn); return nextId; };
  e.context.clearTimeout = id => timers.delete(id);
  e.context.immediatePresent = () => { assert.equal(e.get().phase, "pret"); starts++; };
  e.get().parcours = parcours; e.context.immediateCountdown();
  assert.match(e.context.$('mi-contenu').children[0].textContent, /3 secondes/);
  await e.buttons().find(b=>b.textContent==='Mettre en pause').click();
  assert.equal(timers.size,0); assert.equal(e.calls.length,0); assert.equal(starts,0);
  await e.buttons().find(b=>b.textContent==='Reprendre').click();
  for (let i=0;i<3;i++) { const [id,fn]=timers.entries().next().value; timers.delete(id); fn(); }
  assert.equal(starts,1);
});

test('correction code conservée pendant 3 secondes puis présentation directe, pause possible', async () => {
  const e=environment(), timers=new Map(); let id=0, starts=0;
  e.context.setTimeout=fn=>{timers.set(++id,fn);return id;};e.context.clearTimeout=id=>timers.delete(id);
  e.context.immediatePresent=()=>{assert.equal(e.get().phase,'pret');starts++;};
  e.get().next={id:'next',index:2};e.context.immediateCorrectionCountdown();
  await e.buttons().find(b=>b.textContent==='Mettre en pause').click();assert.equal(timers.size,0);
  e.context.immediateCorrectionCountdown();
  for(let i=0;i<3;i++){const [id,fn]=timers.entries().next().value;timers.delete(id);fn();}
  assert.equal(starts,1);assert.equal(e.get().trial.id,'next');
});

test('Entrée active le bouton principal visible sans intercepter les champs ou touches maintenues', () => {
  const e=environment(); let clicks=0, prevented=0;
  e.context.$('vue-memoires-immediates').querySelectorAll=()=>[{disabled:true,getClientRects:()=>[{}],click:()=>{throw Error('désactivé');}},{disabled:false,getClientRects:()=>[{}],click:()=>clicks++}];
  e.context.initialiserMemoiresImmediates();
  e.listeners.keydown({key:'Enter',target:{closest:()=>null},preventDefault:()=>prevented++});
  assert.equal(clicks,1);assert.equal(prevented,1);
  e.listeners.keydown({key:'Enter',target:{closest:()=>({})},preventDefault:()=>prevented++});
  e.listeners.keydown({key:'Enter',repeat:true,target:{closest:()=>null}});
  assert.equal(clicks,1);
});
