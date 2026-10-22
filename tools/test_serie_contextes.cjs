// Sans dépendance : node --test tools/test_serie_contextes.cjs
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = require('./frontend_source')();
function fonction(nom, suivante) {
  return source.slice(source.indexOf(`function ${nom}(`), source.indexOf(`function ${suivante}(`)).replace(/async\s*$/, "");
}
function environnement(phase = 'decouverte') {
  const appels = [];
  const contexte = {
    etat: { phaseContextes: phase, indexItem: 0, repondu: true, session: { items: [{}, {}, {}] } },
    montrerItem: () => appels.push('item'),
    finirSeance: () => appels.push('fin'),
  };
  vm.createContext(contexte);
  vm.runInContext(fonction('itemSuivant', 'finirSeance'), contexte);
  return { contexte, appels };
}
test('une question après chaque photo, puis rappel de la même série', () => {
  const { contexte: c, appels } = environnement();
  c.itemSuivant();
  assert.equal(c.etat.indexItem, 1);
  assert.equal(c.etat.phaseContextes, 'decouverte');
  c.itemSuivant();
  assert.equal(c.etat.indexItem, 2);
  c.itemSuivant();
  assert.equal(c.etat.indexItem, 0);
  assert.equal(c.etat.phaseContextes, 'rappel');
  c.itemSuivant(); c.itemSuivant(); c.itemSuivant();
  assert.deepEqual(appels, ['item', 'item', 'item', 'item', 'item', 'fin']);
});
test('les autres parcours se terminent sans seconde passe', () => {
  const { contexte: c, appels } = environnement(null);
  c.etat.indexItem = 2;
  c.itemSuivant();
  assert.deepEqual(appels, ['fin']);
});
test('un arrêt de séance ne démarre jamais le rappel', () => {
  const { contexte: c, appels } = environnement();
  c.etat.seanceTerminee = true;
  c.itemSuivant();
  assert.deepEqual(appels, ['fin']);
});
for (const correcte of [true, false]) test(`correction ${correcte ? 'juste sans image' : 'erronée avec scène'}`, () => {
  const { contexte: c } = environnement('rappel');
  const enfants = [];
  c.etat.session.items[0] = { contenu: { affichage: { image: {
    src: 'scene.webp', srcset: 'scene.webp 640w', width: 960, height: 640, alt: 'Le message.'
  } } } };
  const observation = { photo_apres_erreur: false, incident_photo: false };
  c.observationContexte = () => observation;
  c.refs = { carteFeedback: { replaceChildren: () => enfants.splice(0), append: (...e) => enfants.push(...e) } };
  c.creerElement = (balise, options = {}, ...contenu) => ({ balise, options, contenu, events: {}, isConnected: true, addEventListener(nom, callback) { this.events[nom] = callback; }, replaceChildren(...e) { this.contenu = e; }, append(...e) { this.contenu.push(...e); } });
  vm.runInContext(fonction('rendreFeedback', 'programmerSuiteLexicale'), c);
  c.rendreFeedback({ correcte, attendue: 'Sur le frigo' });
  const figures = enfants.filter(e => e.balise === 'figure');
  assert.equal(figures.length, correcte ? 0 : 1);
  if (!correcte) {
    const image = figures[0].contenu[0];
    assert.equal(image.options.attributs.src, 'scene.webp');
    assert.equal(observation.photo_apres_erreur, false);
    image.events.load();
    assert.equal(observation.photo_apres_erreur, true);
    image.events.error();
    assert.equal(observation.incident_photo, true);
  }
});

function observations() {
  const c = { etat: { phaseContextes: 'decouverte', indexItem: 0,
    observationsContextes: { decouverte: [], rappel: [] } }, Date };
  vm.createContext(c);
  vm.runInContext(fonction('observationContexte', 'reinitialiserConfirmationFin'), c);
  return c;
}
test('deux passes distinctes gardent la première erreur après aide', () => {
  const c = observations(), item = { id: 'scene-1', type: 'rappel-source' };
  c.observationContexte(item, true);
  c.enregistrerReponseContexte(item, { reponse: 'frigo', temps_ms: 100 }, { correcte: true });
  c.etat.phaseContextes = 'rappel';
  const rappel = c.observationContexte(item, true);
  c.enregistrerReponseContexte(item, { reponse: 'porte', temps_ms: 200 }, { correcte: false });
  rappel.photo_apres_erreur = true;
  c.enregistrerReponseContexte(item, { reponse: 'frigo', temps_ms: 300 }, { correcte: true });
  assert.equal(c.etat.observationsContextes.decouverte[0].premiere_reponse.correcte, true);
  assert.equal(rappel.premiere_reponse.correcte, false);
  assert.equal(rappel.premiere_reponse.reponse, 'porte');
  const stats = c.statistiquesContextes();
  assert.equal(stats.find(s => s.label === 'Sans photo — premières réponses justes').valeur, '0');
  assert.equal(stats.find(s => s.label === 'Photos revues après erreur').valeur, '1');
  assert.ok(!stats.some(s => s.label === 'Réussite'));
});
test('sortie partielle ne compte pas les questions futures et fin ne transmet pas de justesse client', () => {
  const c = observations();
  c.observationContexte({ id: 'chargee', type: 'rappel-source' }, true);
  c.enregistrerReponseContexte({ id: 'chargee', type: 'rappel-source' },
    { reponse: 'porte', temps_ms: 10 }, { correcte: false });
  c.observationContexte({ id: 'incident', type: 'rappel-source' }).incident_photo = true;
  const stats = c.statistiquesContextes();
  assert.equal(stats.find(s => s.label === 'Après photo — questions présentées').valeur, '1');
  assert.equal(stats.find(s => s.label === 'Après photo — réponses validées').valeur, '1');
  assert.equal(stats.find(s => s.label === 'Sans photo — questions présentées').valeur, '0');
  assert.ok(!JSON.stringify(c.faitsContextes()).includes('premiere_reponse'));
});

for (const phase of ['decouverte', 'rappel', null]) test(`payload de réponse : ${phase}`, async () => {
  let corps;
  const c = {
    etat: { phaseContextes: phase, repondu: false, actionEnCours: false,
      debutQuestion: Date.now(), theme: { id: 'evocation' },
      session: { session_id: 'test', items: [{ id: 'scene', type: 'rappel-source' }] }, indexItem: 0,
      observationsContextes: { decouverte: [], rappel: [] } },
    handlerPour: () => ({ readAnswer: x => x, renderFeedback() {} }),
    apiFetch: async (_, options) => { corps = JSON.parse(options.body); return { essai_supplementaire: true }; },
    masquerBandeau() {}, reglerEtatBoutons() {}, Date,
  };
  vm.createContext(c);
  vm.runInContext(fonction('observationContexte', 'enregistrerReponseContexte') + '\nasync ' + fonction('soumettreValeur', 'programmerSuiteLexicale'), c);
  await c.soumettreValeur('Sur le frigo', 0);
  assert.equal(corps.memorisation === true, phase === 'decouverte');
  assert.equal(corps.reponse, 'Sur le frigo');
  assert.equal(corps.observation_contextes?.passe ?? null, phase);
});
