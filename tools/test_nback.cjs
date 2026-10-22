const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
class Element {
  constructor(tag, opts = {}) { this.tagName = tag.toUpperCase(); this.textContent = opts.texte || ''; this.className = opts.classe || ''; this.children = []; this.dataset = {}; this.events = {}; this.disabled = false; this.hidden = false; Object.assign(this, opts.attributs); this.classList = { add: name => { this.className += ` ${name}`; } }; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this[key] = value; }
  removeAttribute(key) { delete this[key]; }
  addEventListener(event, cb) { this.events[event] = cb; }
  querySelector(query) { return this.querySelectorAll(query)[0]; }
  focus() { this.focused = true; }
  async click() { if (!this.disabled) return this.events.click?.(); }
}
// Match class selectors independently from tag selectors.
Element.prototype.querySelectorAll = function(query) {
  return this.children.flatMap(n => [...((query.startsWith('.') ? n.className.split(' ').includes(query.slice(1)) : n.tagName.toLowerCase() === query) ? [n] : []), ...n.querySelectorAll(query)]);
};
function setup(phase = 'decision') {
  const nodes = new Map(), calls = [], listeners = {}, audio = [], unloadCalls = [], preferences = new Map();
  const ctx = { preferenceLocale: (key, def) => preferences.get(key) ?? def, garderPreference: (key, value) => preferences.set(key, value), crypto: { randomUUID: () => 'same-id' }, etat: {}, CAPACITES: { arreter() {}, lire: text => { audio.push(text); } },
    window: { addEventListener: (event, cb) => { listeners[event] = cb; } },
    fetch: (path, options) => { unloadCalls.push({ path, options }); return Promise.resolve(); },
    document: { hidden: false, addEventListener: (event, cb) => { listeners[event] = cb; } }, annulerMemo() {}, afficherVue() {}, afficherBandeau() {}, revenirAuxThemes() {}, sansLimiteActivee: () => false,
    actualiserBoutonAudio: (active, b) => { b.textContent = active ? 'Muet' : 'Écouter'; },
    immediateVisualGlyph: id => new Element('svg', { attributs: { forme: id } }),
    creerElement: (tag, opts, ...children) => { const e = new Element(tag, opts); e.append(...children); return e; },
    $: id => { if (!nodes.has(id)) nodes.set(id, new Element('div')); return nodes.get(id); },
    fetchJson: async (base, path, opts) => { const body = JSON.parse(opts.body); calls.push({ path, body }); return ctx.respond(body); }, respond: () => ({ phase: 'neutre', position: 2, total: 16 }) };
  vm.createContext(ctx); vm.runInContext(fs.readFileSync('frontend/src/nback.js', 'utf8'), ctx);
  ctx.initial = { session_id: 's', phase, position: 2, total: 16, symbole: 'carre', choix: null, exemple: null, pending: null, busy: false };
  vm.runInContext('nbackSession = initial; rendreNBack()', ctx);
  return { ctx, calls, listeners, audio, unloadCalls, preferences, get: () => vm.runInContext('nbackSession', ctx), c: ctx.$('nback-contenu'), buttons: () => [...ctx.$('nback-contenu').querySelectorAll('button'), ...ctx.$('nback-commandes').querySelectorAll('button')] };
}
const button = (e, text) => e.buttons().find(b => b.textContent === text);
test('aucune réponse présélectionnée; choix modifiable avant validation', async () => {
  const e = setup(); assert.equal(button(e, 'Valider').disabled, true);
  await button(e, 'Identique').click(); assert.equal(button(e, 'Valider').disabled, false); assert.equal(button(e, 'Identique')['aria-pressed'], 'true');
  await button(e, 'Différent').click(); assert.equal(button(e, 'Identique')['aria-pressed'], 'false');
  await button(e, 'Valider').click(); assert.equal(e.calls[0].body.donnees.decision, 'different');
});
test('réponse enregistrée masque la forme sans correction ni suivant automatique', async () => {
  const e = setup(); await button(e, 'Identique').click(); await button(e, 'Valider').click();
  assert.equal(e.c.querySelectorAll('svg').length, 0); assert.deepEqual(e.c.querySelectorAll('p').map(p => p.textContent), ['Réponse enregistrée.']);
  assert.ok(button(e, 'Suivant')); assert.equal(e.calls.length, 1);
});
test('absence explicite transmet absence et non une réponse devinée', async () => {
  const e = setup(); await button(e, 'Je ne sais pas').click(); await button(e, 'Valider').click(); assert.equal(e.calls[0].body.donnees.decision, 'absence');
});
test('première forme sans question ni réponse enregistrable', () => {
  const e = setup('initialisation'); assert.equal(e.c.querySelectorAll('svg').length, 1); assert.ok(button(e, 'Suivant')); assert.equal(button(e, 'Valider'), undefined); assert.equal(button(e, 'Identique'), undefined);
});
test('échec réseau efface stimulus et conserve identifiant/payload jusqu’à retry', async () => {
  const e = setup(); let count = 0; e.ctx.respond = () => { if (++count === 1) throw Error('réseau'); return { phase: 'neutre' }; };
  await button(e, 'Identique').click(); await button(e, 'Valider').click(); assert.equal(e.c.querySelectorAll('svg').length, 0);
  await e.ctx.nbackEtape('repondre', { decision: 'different' }); assert.equal(e.calls.length, 1);
  await button(e, 'Réessayer').click(); assert.deepEqual(e.calls[0], e.calls[1]);
});
test('masquage durant requête sérialise interruption et ne réaffiche jamais la forme', async () => {
  const e = setup('neutre'); let resolve; e.ctx.respond = body => body.action === 'suivant' ? new Promise(r => { resolve = r; }) : { phase: 'interrompu', resultat: { statut: 'interrompu' } };
  const pending = button(e, 'Suivant').click(); e.ctx.document.hidden = true; e.listeners.visibilitychange(); assert.equal(e.get().interrompre, "masquage");
  resolve({ phase: 'decision', position: 3, symbole: 'triangle' }); await pending;
  assert.deepEqual(e.calls.map(c => c.body.action), ['suivant', 'interrompre']); assert.equal(e.get().phase, 'interrompu'); assert.equal(e.c.querySelectorAll('svg').length, 0);
});
test('terminer la séance interrompt la série et conserve les réponses', async () => {
  const e = setup(); e.ctx.respond = () => ({ phase: 'interrompu', resultat: { statut: 'interrompu', decisions_observees: 1 } });
  await button(e, 'Terminer la séance').click(); assert.equal(e.calls[0].body.action, 'interrompre'); assert.equal(e.calls[0].body.donnees.raison, 'sortie'); assert.equal(button(e, 'Reprendre'), undefined); assert.ok(button(e, 'Retour à l’accueil'));
});
test('exemple facultatif guidé ne journalise aucune réponse', async () => {
  const e = setup('ready'); await button(e, 'Voir un exemple').click(); await button(e, 'Suivant').click(); await button(e, 'Identique').click();
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent.startsWith('À revoir.'))); assert.equal(e.calls.length, 0);
  await button(e, 'Quitter l’exemple').click(); assert.equal(e.get().exemple, null); assert.ok(button(e, 'Commencer'));
});
test('lecture commune seulement consigne, jamais forme ni historique', async () => {
  const e = setup('ready'); await button(e, 'Écouter').click(); assert.equal(button(e, 'Muet').textContent, 'Muet'); await button(e, 'Muet').click();
  assert.equal(e.audio.length, 1); const active = setup(); assert.equal(button(active, 'Écouter'), undefined); assert.equal(active.audio.length, 0);
});
test('résultat descriptif affiche catégories serveur sans score global', () => {
  const e = setup('resultat'); e.get().resultat = { statut: 'termine', decisions_observees: 15, correspondances_detectees: 4, correspondances_manquees: 1, fausses_alertes: 2, non_correspondances_rejetees: 7, absences_declarees: 1 }; e.ctx.rendreNBack();
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Identiques reconnues : 4')); assert.equal(e.c.querySelectorAll('svg').length, 0);
});
test('Entrée ignore composition, répétition, boutons natifs et vue masquée', async () => {
  const e = setup('initialisation'), handler = e.ctx.$('vue-nback').onkeydown;
  for (const props of [{ isComposing: true }, { repeat: true }, { target: { tagName: 'BUTTON' } }]) handler({ key: 'Enter', target: { tagName: 'DIV' }, preventDefault() {}, ...props });
  e.ctx.$('vue-nback').hidden = true; handler({ key: 'Enter', target: { tagName: 'DIV' }, preventDefault() {} }); assert.equal(e.calls.length, 0);
  e.ctx.$('vue-nback').hidden = false; handler({ key: 'Enter', target: { tagName: 'DIV' }, preventDefault() {} }); assert.equal(e.calls.length, 1);
});
test('navigation nettoie DOM et clôture sans repeupler vue masquée', async () => {
  const e = setup(); e.ctx.$('vue-nback').hidden = true; e.ctx.respond = () => ({ phase: 'interrompu', resultat: { statut: 'interrompu' } }); e.ctx.nbackQuitter(); await Promise.resolve(); await Promise.resolve();
  assert.equal(e.c.children.length, 0); assert.equal(e.calls[0].body.action, 'interrompre');
});
test('terminer reste disponible durant réseau et est sérialisé après accusé', async () => {
  const e = setup(); let resolve; e.ctx.respond = body => body.action === 'repondre' ? new Promise(r => { resolve = r; }) : { phase: 'interrompu', resultat: { statut: 'interrompu' } };
  await button(e, 'Identique').click(); const pending = button(e, 'Valider').click();
  assert.equal(button(e, 'Terminer la séance').disabled, false); await button(e, 'Terminer la séance').click();
  assert.equal(e.calls.length, 1); resolve({ phase: 'neutre' }); await pending;
  assert.equal(e.calls[1].body.action, 'interrompre'); assert.equal(e.calls[1].body.donnees.raison, 'sortie');
});
test('forme et nom accessible effacés immédiatement quand requête reste ouverte', async () => {
  const e = setup(); let resolve; e.ctx.respond = () => new Promise(r => { resolve = r; });
  await button(e, 'Identique').click(); const pending = button(e, 'Valider').click(); const zone = e.c.querySelector('.nback-forme');
  assert.equal(zone['aria-label'], undefined); assert.equal(zone.role, undefined); assert.equal(zone.children.length, 0);
  resolve({ phase: 'neutre' }); await pending;
});
test('répétition native Entrée/Espace empêchée après changement du bouton principal', () => {
  const e = setup('neutre'); let prevented = 0;
  for (const key of ['Enter', ' ']) e.ctx.$('vue-nback').onkeydown({ key, repeat: true, target: { tagName: 'BUTTON' }, preventDefault() { prevented++; } });
  assert.equal(prevented, 2); assert.equal(e.calls.length, 0);
});
test('retour partiel utilise seulement les occurrences observées comme dénominateur', () => {
  const e = setup('interrompu'); e.get().resultat = { statut: 'interrompu', correspondances_detectees: 1, correspondances_observees: 2, non_correspondances_rejetees: 1, non_correspondances_observees: 3 }; e.ctx.rendreNBack();
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Identiques reconnues : 1 sur 2'));
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Différentes reconnues : 1 sur 3'));
});
test('pagehide clôture au mieux une seule fois et masque toute information', () => {
  const e = setup(); e.listeners.pagehide(); e.listeners.pagehide();
  assert.equal(e.unloadCalls.length, 1); assert.equal(e.unloadCalls[0].options.keepalive, true); assert.equal(e.unloadCalls[0].path, '/api/nback/sessions/s/fin');
  assert.equal(e.c.children.length, 0); assert.equal(e.get().interrompre, 'sortie');
});
test('pagehide pendant requête ne réaffiche pas le symbole au retour', async () => {
  const e = setup('neutre'); let resolve; e.ctx.respond = () => new Promise(r => { resolve = r; });
  const pending = button(e, 'Suivant').click(); e.listeners.pagehide(); resolve({ phase: 'decision', symbole: 'triangle' }); await pending;
  assert.equal(e.c.children.length, 0); await e.ctx.nbackEtape('suivant'); assert.equal(e.calls.length, 1);
});
test('interruption avant première décision sans fractions vides', () => {
  const e = setup('interrompu'); e.get().resultat = { statut: 'interrompu', decisions_observees: 0, correspondances_detectees: 0, correspondances_observees: 0, non_correspondances_rejetees: 0, non_correspondances_observees: 0 }; e.ctx.rendreNBack();
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Aucune réponse enregistrée.')); assert.ok(!e.c.querySelectorAll('p').some(p => p.textContent.includes('sur 0')));
});
test('aucun identique observé ne produit pas de fraction 0 sur 0', () => {
  const e = setup('interrompu'); e.get().resultat = { statut: 'interrompu', decisions_observees: 1, correspondances_detectees: 0, correspondances_observees: 0 }; e.ctx.rendreNBack();
  assert.ok(e.c.querySelectorAll('p').some(p => p.textContent === 'Aucune forme identique observée.'));
});

test('retour du cache navigateur après sortie active revient à accueil sans reprendre', () => {
  const e = setup(); let returned = 0; e.ctx.revenirAuxThemes = () => returned++;
  e.listeners.pagehide(); e.listeners.pageshow({persisted:true});
  assert.equal(returned, 1); assert.equal(e.get(), null); assert.equal(e.unloadCalls.length, 1);
});
test('retour du cache après résultat effacé restaure accueil sans nouvelle clôture', () => {
  const e = setup('resultat'); let returned = 0; e.ctx.revenirAuxThemes = () => returned++;
  e.listeners.pagehide(); assert.equal(e.c.children.length, 0);
  e.listeners.pageshow({persisted:true});
  assert.equal(returned, 1); assert.equal(e.get(), null); assert.equal(e.unloadCalls.length, 0);
});
for (const n of [1, 2, 3]) {
  test(`création ${n}-back transmet entier et consigne adaptée, jamais les formes en audio`, async () => {
    const e = setup('ready'); e.ctx.respond = () => ({ session_id: 's', phase: 'ready', n, total: n + 15 });
    await e.ctx.demarrerNBack(n); assert.equal(e.calls[0].body.n, n); await button(e, 'Écouter').click();
    assert.ok(e.audio[0].includes(n === 1 ? 'celle juste avant' : `celle ${n} places avant`));
    assert.ok(e.c.querySelectorAll('p').some(p => p.textContent.includes(`${n + 15} formes`)));
    e.get().phase = 'initialisation'; e.get().position = n; e.get().symbole = 'carre'; e.ctx.rendreNBack();
    assert.equal(button(e, 'Identique'), undefined); assert.equal(button(e, 'Écouter'), undefined); assert.ok(e.c.querySelectorAll('p').some(p => p.textContent.includes(`${n} sur ${n}`)));
  });
}
for (const [n, choices] of [[2, ['Identique', 'Différent', 'Différent']], [3, ['Identique', 'Identique', 'Identique', 'Différent']]]) {
  test(`exemple ${n}-back compare à distance exacte et exclut ${n} initialisations`, async () => {
    const e = setup('ready'); e.get().n = n; e.get().total = n + 15; e.ctx.rendreNBack(); await button(e, 'Voir un exemple').click();
    for (let i = 0; i < n; i++) { assert.equal(button(e, 'Identique'), undefined); await button(e, 'Suivant').click(); }
    for (const choix of choices) {
      assert.equal(e.c.querySelectorAll('svg').length, 1); await button(e, choix).click();
      assert.ok(e.c.querySelectorAll('p').some(p => p.textContent.startsWith('Oui.'))); await (button(e, 'Suivant') || button(e, 'Revenir à la consigne')).click();
    }
    assert.equal(e.get().exemple, null); assert.equal(e.calls.length, 0);
  });
}
test('distance enregistrée pour prochaine carte, sans sélection automatique supérieure', () => {
  const e = setup('ready'); let card = e.ctx.carteNBack(), select = card.querySelector('select'); assert.equal(select.value, '1');
  select.value = '3'; select.events.change(); card = e.ctx.carteNBack(); assert.equal(card.querySelector('select').value, '3');
  e.preferences.set('orthogone.nback.n', '4'); assert.equal(e.ctx.carteNBack().querySelector('select').value, '1');
});
