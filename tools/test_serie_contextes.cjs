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
  c.refs = { carteFeedback: { replaceChildren: () => enfants.splice(0), append: (...e) => enfants.push(...e) } };
  c.creerElement = (balise, options = {}, ...contenu) => ({ balise, options, contenu, addEventListener() {}, append(...e) { this.contenu.push(...e); } });
  vm.runInContext(fonction('rendreFeedback', 'programmerSuiteLexicale'), c);
  c.rendreFeedback({ correcte, attendue: 'Sur le frigo' });
  const figures = enfants.filter(e => e.balise === 'figure');
  assert.equal(figures.length, correcte ? 0 : 1);
  if (!correcte) assert.equal(figures[0].contenu[0].options.attributs.src, 'scene.webp');
});
