const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag, opts = {}) { this.tag = tag; this.tagName = tag.toUpperCase(); this.textContent = opts.texte || ''; this.children = []; this.dataset = {}; this.events = {}; this.disabled = false; Object.assign(this, opts.attributs || {}); }
  get options() { return this.children.filter(n => n.tag === 'option'); }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  addEventListener(event, cb) { const previous = this.events[event]; this.events[event] = (...args) => { previous?.(...args); return cb(...args); }; }
  querySelectorAll(tags) { return this.children.flatMap(n => [...(tags.split(',').some(t => t.trim() === n.tag || (t.trim() === "input[type='number']" && n.tag === 'input' && n.type === 'number')) ? [n] : []), ...n.querySelectorAll(tags)]); }
  querySelector(tag) { return this.querySelectorAll(tag)[0]; }
  focus() {}
  async click() { if (!this.disabled) return this.events.click?.(); }
}
function setup(parcours = 'message', phase = 'encodage', condition = 'sans-note') {
  const nodes = new Map(), calls = [], listeners = {}, audio = [], clock = { now: 0 };
  const ctx = { console, crypto: { randomUUID: () => 'immutable-id' }, performance: { now: () => clock.now }, etat: {},
    document: { hidden: false, addEventListener: (event, cb) => { listeners[event] = cb; } },
    actualiserBoutonAudio: (active, b) => { b.textContent = active ? "Muet" : "Écouter"; }, CAPACITES: { arreter() {}, lire: text => { audio.push(text); } }, annulerMemo() {}, afficherVue() {}, afficherBandeau() {}, revenirAuxThemes() {}, sansLimiteActivee: () => false,
    creerElement: (tag, opts, ...children) => { const n = new Element(tag, opts); n.append(...children); return n; },
    $: id => { if (!nodes.has(id)) nodes.set(id, new Element('div')); return nodes.get(id); },
    fetchJson: async (base, path, opts) => { const body = JSON.parse(opts.body); calls.push({ path, body }); return ctx.respond(body); }, respond: () => ({ phase: 'restitution', scenario: {}, donnees: {} }) };
  vm.createContext(ctx); vm.runInContext(fs.readFileSync('frontend/src/strategies.js', 'utf8'), ctx);
  ctx.initial = { session_id: 's', parcours, phase, condition, scenario: { message: 'Appelez le secrétariat à 15 heures.', ...(parcours === 'message' ? {actions:[{id:'appeler',texte:'Appeler le secrétariat'},{id:'envoyer',texte:'Envoyer un courrier'}],heures:['15 h','10 h']} : {}) }, donnees: {}, note: '', brouillon: {}, timing: null, busy: false, pending: null };
  vm.runInContext('strategieSession = initial; rendreStrategies()', ctx);
  return { ctx, calls, clock, listeners, audio, get: () => vm.runInContext('strategieSession', ctx), c: ctx.$('strategie-contenu'), buttons: () => [...ctx.$('strategie-commandes').querySelectorAll('button'), ...ctx.$('strategie-contenu').querySelectorAll('button')] };
}
test('message retiré du DOM et de la lecture après masquage sans note', async () => {
  const e = setup(); await e.buttons().find(b => b.textContent === 'Masquer le message').click();
  assert.equal(e.get().phase, 'restitution'); assert.equal(e.c.querySelectorAll('textarea').length, 0);
  assert.ok(!e.c.querySelectorAll('p').some(p => p.textContent.includes('15 heures')));
  await e.buttons().find(b => b.textContent === 'Écouter').click(); assert.ok(!e.audio.at(-1).includes('secrétariat'));
});
test('sauvegarde échouée bloque et retry conserve exactement étape et identifiant', async () => {
  const e = setup(); let n = 0; e.ctx.respond = () => { if (++n === 1) throw Error('réseau'); return { phase: 'restitution', scenario: {}, donnees: {} }; };
  await e.buttons().find(b => b.textContent === 'Masquer le message').click(); assert.equal(e.get().phase, 'encodage');
  await e.ctx.strategieEtape('restituer', { quoi: 'autre' }); assert.equal(e.calls.length, 1);
  await e.buttons().find(b => b.textContent === 'Réessayer').click(); assert.deepEqual(e.calls[0], e.calls[1]); assert.equal(e.get().phase, 'restitution');
});
test('note facultative locale sans texte envoyé au serveur', async () => {
  const e = setup('message', 'encodage', 'avec-note'); const note = e.c.querySelector('textarea'); note.value = 'Note privée'; note.events.input();
  await e.buttons().find(b => b.textContent === 'Masquer le message').click(); assert.equal(e.calls[0].body.donnees.note_presente, true); assert.ok(!JSON.stringify(e.calls).includes('Note privée'));
  assert.ok(e.buttons().some(b => b.textContent === 'Consulter ma note'));
});
test('durée monotone et pauses sont séparées; visibilité invalide comparaison', async () => {
  const e = setup('temps', 'classement'); e.get().timing = { debut: 1000, active: 6000, segment: null, pauses: 3000, pause: null, fiable: true }; e.clock.now = 10000;
  const data = e.ctx.strategieTemps(e.get()); assert.equal(data.duree_active_secondes, 6); assert.equal(data.duree_ecoulee_secondes, 9); assert.equal(data.pauses_secondes, 3);
  e.ctx.document.hidden = true; e.listeners.visibilitychange(); assert.equal(e.get().timing.fiable, false); assert.deepEqual(JSON.parse(JSON.stringify(e.ctx.strategieTemps(e.get()))), {});
});
test('plan enregistre ordre choisi puis nouvelle contrainte sans correction révélée', async () => {
  const e = setup('plan', 'plan_initial'); e.get().ordre = null; e.get().scenario = { actions: [{ id:'remplir', texte:'Compléter' }, { id:'signer', texte:'Signer' }, { id:'joindre', texte:'Joindre' }], contraintes: ['Compléter avant de signer.'] }; e.ctx.rendreStrategies();
  e.ctx.respond = () => ({ phase: 'revision', donnees: { plan_initial: ['remplir','signer','joindre'] }, scenario: { contraintes: ['Joindre avant de signer.'] } });
  await e.buttons().find(b => b.textContent === 'Enregistrer mon plan').click(); assert.equal(e.get().phase, 'revision'); assert.deepEqual(e.calls[0].body.donnees.ordre, ['remplir','signer','joindre']); assert.ok(!e.c.querySelectorAll('p').some(p => p.textContent.includes('compatible :')));
});

for (const parcours of ['plan','rappel','message','temps']) test(`création ${parcours} envoie seulement la condition admise`, async () => {
  const e = setup(); e.ctx.respond = () => ({session_id:'s',parcours,phase:'correction',scenario:{},donnees:{},resultat:{}});
  await e.ctx.demarrerStrategies(parcours,'sans-note');
  assert.equal(e.calls[0].body.parcours,parcours);
  assert.equal(e.calls[0].body.condition,parcours === 'message' ? 'sans-note' : undefined);
  assert.equal(e.get().rappelChoisi,false);
});
test('choix explicite requis avant action et audio utilise le bouton partagé', async () => {
  const e = setup('message','action');
  const main = e.buttons().find(b => b.textContent === 'Réaliser la demande');
  assert.equal(main.disabled,true);
  const choices = e.c.querySelectorAll('select'); choices[0].value='appeler';choices[1].value='15 h';choices[1].events.change();
  assert.equal(main.disabled,false);
  const initial = setup();const audio = initial.buttons().find(b => b.textContent === 'Écouter');
  await audio.click();assert.equal(audio.textContent,'Muet');await audio.click();assert.equal(audio.textContent,'Écouter');
});

function render(e, scenario, donnees = {}) { if (e.get().parcours === "plan") e.get().ordre = null; e.get().scenario = scenario; e.get().donnees = donnees; e.ctx.rendreStrategies(); }
function choose(select, value) { select.value = value; select.events.change(); }
const plain = value => JSON.parse(JSON.stringify(value));
for (const [action, heure] of [['confirmer', '9 h'], ['deposer', '16 h'], ['rappeler', '11 h']]) {
  test(`message variable ${action} : options serveur et choix jamais présélectionnés`, async () => {
    const e = setup('message', 'action');
    render(e, { actions: [{ id: action, texte: `Action ${action}` }, { id: 'autre', texte: 'Autre action' }], heures: ['20 h', heure] });
    const selects = e.c.querySelectorAll('select'), main = e.buttons().find(b => b.textContent === 'Réaliser la demande');
    assert.deepEqual(selects.map(s => s.value), ['', '']); assert.equal(main.disabled, true);
    assert.deepEqual(selects[1].options.map(o => o.value), ['', '20 h', heure]);
    choose(selects[0], action); assert.equal(main.disabled, true); choose(selects[1], heure); await main.click();
    assert.deepEqual(e.calls[0].body.donnees, { action_id: action, heure });
  });
}
for (const [piece, intercale, signal] of [['ticket', 'reference', 'Commande prête'], ['carte', 'adresse', 'Inscription prête'], ['attestation', 'montant', 'Demande prête']]) {
  test(`rappel variable ${piece} : intention masquée et action intercalée propre`, async () => {
    const e = setup('rappel', 'intercale');
    const scenario = { pieces: [{ id: piece, texte: `Pièce ${piece}` }], actions_intercalees: [{ id: 'premiere', texte: 'Première vérification' }, { id: intercale, texte: `Vérifier ${intercale}` }] };
    render(e, scenario, { actions_intercalees: ['premiere'] });
    assert.deepEqual(e.c.querySelectorAll('p').map(p => p.textContent), [`Vérifier ${intercale}`]);
    e.ctx.respond = () => ({ phase: 'signal', scenario, donnees: { signal, rappel_delivre: false } });
    await e.buttons().find(b => b.textContent === 'C’est vérifié').click(); assert.equal(e.calls[0].body.donnees.action_id, intercale);
    assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === signal));
    assert.ok(!e.buttons().some(b => b.textContent === 'Consulter mon rappel'));
    const select = e.c.querySelector('select'); assert.equal(select.value, ''); choose(select, piece);
    await e.buttons().find(b => b.textContent === 'Joindre la pièce').click(); assert.equal(e.calls[1].body.donnees.piece_id, piece);
  });
}
for (const [id, categories] of [['lettre-7', ['urgent', 'courant']], ['bon-8', ['achats', 'ventes']], ['fiche-9', ['a-traiter', 'archive']]]) {
  test(`classement variable ${id} : documents visibles et nouveau choix pour chaque document`, async () => {
    const e = setup('temps', 'classement');
    const scenario = { consigne: 'Classer selon le type indiqué.', categories, documents: [{ id, texte: 'Premier document' }, { id: 'suivant', texte: 'Second document' }] };
    render(e, scenario); let select = e.c.querySelector('select'); assert.equal(select.value, '');
    assert.deepEqual(select.options.map(o => o.value), ['', ...categories]);
    assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Second document'));
    choose(select, categories[1]); e.ctx.respond = () => ({ phase: 'classement', scenario, donnees: { classement: { [id]: categories[1] } } });
    await e.buttons().find(b => b.textContent === 'Classer ce document').click();
    assert.deepEqual(e.calls[0].body.donnees, { document_id: id, categorie: categories[1] });
    select = e.c.querySelector('select'); assert.equal(select.value, ''); assert.equal(e.buttons().find(b => b.textContent === 'Classer ce document').disabled, true);
  });
}
test('plan variable : ordre et actions réellement exécutées utilisent les identifiants reçus', async () => {
  const e = setup('plan', 'plan_initial'), scenario = { but: 'Préparer un colis.', contraintes: ['Emballer avant fermeture.'], actions: [{ id: 'emballer', texte: 'Emballer le colis' }, { id: 'fermer', texte: 'Fermer le colis' }, { id: 'etiqueter', texte: 'Ajouter l’étiquette' }] };
  render(e, scenario); e.ctx.respond = () => ({ phase: 'execution', scenario, donnees: { plan_final: ['etiqueter','emballer','fermer'], actions_executees: ['etiqueter'] } });
  await e.buttons().find(b => b.textContent === 'Enregistrer mon plan').click();
  assert.deepEqual(e.calls[0].body.donnees.ordre, ['emballer','fermer','etiqueter']);
  await e.buttons().find(b => b.textContent === 'Réaliser : Emballer le colis').click(); assert.equal(e.calls[1].body.donnees.action_id, 'emballer');
});
test('consultation note préserve la restitution et la lecture audio suit uniquement le contenu visible', async () => {
  const e = setup('message', 'restitution', 'avec-note'); e.get().note = 'Mon aide'; e.ctx.rendreStrategies();
  const fields = e.c.querySelectorAll('input'); fields[0].value = 'Déposer'; fields[0].events.input(); fields[1].value = '9 h'; fields[1].events.input();
  e.ctx.respond = () => ({ phase: 'restitution', scenario: {}, donnees: { note_presente: true } });
  await e.buttons().find(b => b.textContent === 'Consulter ma note').click();
  assert.deepEqual(e.c.querySelectorAll('input').map(f => f.value), ['Déposer', '9 h']);
  await e.buttons().find(b => b.textContent === 'Écouter').click(); assert.ok(e.audio.at(-1).includes('Mon aide'));
  await e.buttons().find(b => b.textContent === 'Valider ma restitution').click(); assert.deepEqual(e.calls[1].body.donnees, { quoi:'Déposer', quand:'9 h', absence:false });
});
test('Enter conserve le comportement natif du select et ne valide pas une composition', () => {
  const e = setup('message','action'); let prevented = false;
  for (const extra of [{target:{tagName:'SELECT'}}, {target:{tagName:'INPUT'},isComposing:true}]) e.c.onkeydown({key:'Enter',preventDefault(){prevented=true;},...extra});
  assert.equal(prevented,false); assert.equal(e.calls.length,0);
});
test('réseau exclu de la durée active et fin figée au dernier document', async () => {
  const e = setup('temps','classement'); const scenario = { documents:[{id:'dernier',texte:'Dernier'}],categories:['archive'] };
  e.clock.now=1000; e.get().timing=null; render(e,scenario);
  e.clock.now=4000; choose(e.c.querySelector('select'),'archive');
  e.ctx.respond=()=>{e.clock.now=9000;return {phase:'comparaison',scenario,donnees:{classement:{dernier:'archive'}}};};
  await e.buttons().find(b=>b.textContent==='Classer ce document').click(); e.clock.now=30000;
  const mesure=plain(e.ctx.strategieTemps(e.get())); assert.equal(mesure.duree_active_secondes,3); assert.equal(mesure.duree_ecoulee_secondes,3); assert.equal(mesure.attente_interface_secondes,0);
});
test('durée active exclut pause et deux attentes réseau distinctes', async () => {
  const e = setup('temps','classement'), scenario={documents:[{id:'a',texte:'A'},{id:'b',texte:'B'}],categories:['archive']};
  e.clock.now=1000;e.get().timing=null;render(e,scenario);
  e.clock.now=4000;e.ctx.respond=()=>{e.clock.now=5000;return {phase:'classement',scenario,donnees:{}};};
  await e.ctx.strategieEtape('pause');
  e.clock.now=9000;e.ctx.respond=()=>{e.clock.now=10000;return {phase:'classement',scenario,donnees:{}};};
  await e.ctx.strategieEtape('reprendre');
  e.clock.now=12000;choose(e.c.querySelector('select'),'archive');
  e.ctx.respond=()=>{e.clock.now=15000;return {phase:'classement',scenario,donnees:{classement:{a:'archive'}}};};
  await e.buttons().find(b=>b.textContent==='Classer ce document').click();
  e.clock.now=17000;choose(e.c.querySelector('select'),'archive');
  e.ctx.respond=()=>({phase:'comparaison',scenario,donnees:{classement:{a:'archive',b:'archive'}}});
  await e.buttons().find(b=>b.textContent==='Classer ce document').click();
  assert.deepEqual(plain(e.ctx.strategieTemps(e.get())),{duree_active_secondes:7,duree_ecoulee_secondes:16,pauses_secondes:5,attente_interface_secondes:4});
});
test('réécoute explicite tracée puis retour à l’action conserve la première restitution', async () => {
  const e = setup('message','restitution','sans-note');
  const scenario = {actions:[{id:'reserver',texte:'Réserver la salle'},{id:'annuler',texte:'Annuler la demande'}],heures:['10 h','18 h']};
  const server={first:null,aides:[],phase:'restitution'};
  render(e,scenario);
  e.ctx.respond = body => {
    if(body.action==='restituer') { assert.equal(server.first,null);server.first={...body.donnees};server.phase='action'; }
    else if(body.action==='reecouter') { server.aides.push('reecoute');server.phase='encodage'; }
    else if(body.action==='masquer') server.phase=server.first?'action':'restitution';
    else if(body.action==='agir') server.phase='correction';
    return {phase:server.phase,scenario:{...scenario,...(server.phase==='encodage'?{message:'Réservez la salle à 10 heures.'}:{})},donnees:{},...(server.phase==='correction'?{resultat:{observations:{restitution:server.first},aides:server.aides}}:{})};
  };
  const fields=e.c.querySelectorAll('input');fields[0].value='Annuler';fields[0].events.input();fields[1].value='18 h';fields[1].events.input();
  await e.buttons().find(b=>b.textContent==='Valider ma restitution').click();
  const first={...server.first};await e.buttons().find(b=>b.textContent==='Revoir le message').click();
  assert.equal(e.calls[1].body.action,'reecouter');assert.deepEqual(e.calls[1].body.donnees,{});
  assert.ok(e.c.querySelectorAll('p').some(p=>p.textContent==='Réservez la salle à 10 heures.'));
  assert.equal(e.audio.length,0);await e.buttons().find(b=>b.textContent==='Écouter').click();assert.ok(e.audio[0].includes('Réservez'));
  await e.buttons().find(b=>b.textContent==='Masquer le message').click();
  assert.equal(e.get().phase,'action');assert.equal(e.c.querySelectorAll('input').length,0);
  assert.ok(!e.c.querySelectorAll('p').some(p=>p.textContent.includes('Réservez')));
  const selects=e.c.querySelectorAll('select');choose(selects[0],'reserver');choose(selects[1],'10 h');
  await e.buttons().find(b=>b.textContent==='Réaliser la demande').click();
  assert.deepEqual(server.first,first);assert.deepEqual(server.aides,['reecoute']);assert.deepEqual(e.calls.at(-1).body.donnees,{action_id:'reserver',heure:'10 h'});
});
test('réécoute avant restitution revient au même brouillon sans fournir une réponse', async () => {
  const e=setup('message','restitution','sans-note');let fields=e.c.querySelectorAll('input');fields[0].value='Mon début';fields[0].events.input();
  e.ctx.respond=body=>({phase:body.action==='reecouter'?'encodage':'restitution',scenario:body.action==='reecouter'?{message:'Message réexposé'}:{},donnees:{}});
  await e.buttons().find(b=>b.textContent==='Revoir le message').click();await e.buttons().find(b=>b.textContent==='Masquer le message').click();
  fields=e.c.querySelectorAll('input');assert.equal(fields[0].value,'Mon début');assert.equal(fields[1].value,'');assert.equal(e.calls.filter(c=>c.body.action==='restituer').length,0);
});
